#-*- coding: utf-8 -*-
import datetime
import logging
import sys

from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.urlresolvers import reverse_lazy
from django.core.exceptions import ImproperlyConfigured
from django.forms.models import formset_factory
from django.http import HttpResponseRedirect, Http404
from django.utils.translation import ugettext as _
from django.views.generic import CreateView, UpdateView, DetailView, ListView, TemplateView

from braces.views import LoginRequiredMixin
#from django_datatables_view.base_datatable_view import BaseDatatableView
from datatableview.views import DatatableView
from datatableview.helpers import link_to_model
from auditlog.models import LogEntry
from cbvtoolkit.views import MultiFormView

from .forms import ClientCreateForm, IdentificationForm, CommunicationForm, ReferralForm

from contacts.forms import ContactCreateForm, AddressFormSet, AddressFormSetHelper, PhoneFormSet, PhoneFormSetHelper
from orders.forms import OrderForm, OrderStopForm, OrderStopFormHelper, DeliveryDefaultForm, DefaultMealSideFormSet

# Import the customized User model
from .models import Client, Referral
from contacts.models import Address, Phone
from orders.models import Order, OrderStop

logger = logging.getLogger(__name__)

# Create your views here.
class ClientActionMixin(object):
    @property
    def action(self):
        msg = "{0} is missing action.".format(self.__class__)
        raise NotImplementedError(msg)
    
    def form_valid(self, form):
        if self.action == 'create':
            msg = _('Client ajouté.')
        else:
            msg = _('Client mis à jour.')
            
        messages.info(self.request, msg)
        return super(ClientActionMixin, self).form_valid(form)
    
    def form_action(self):
        if self.action == 'create':
            return reverse('client_create')
        else:
            return reverse('client_update', args=[str(self.object.id)])
        
    def form_title(self, form):
        if self.action == 'create':
            return _('Client registration.')
        else:
            return _('Client update.') 

class ClientListView(LoginRequiredMixin, DatatableView):    
    model = Client
    
    datatable_options = {
                         #'structure_template': "datatableview/bootstrap_structure.html",
        'columns': [
            ('Name', ['first_name', 'last_name'], link_to_model),
            ('First name', 'first_name'),
            ('Last name', 'last_name'),
            ('Gender', 'get_gender_display'), # this column is not searchable because sorting is done at code level (not db query)
            ('Status', 'status'),
            ('Birth Date', 'birth_date'),
            #('Birth Date (Age)', None, 'get_entry_bday_age'),
            ],
    }
    
    implementation = u""
    
    def get_column_Birth_Date_data(self, instance, *args, **kwargs):
        return instance.birth_date.strftime("%d/%m/%Y")
    
    def get_entry_bday_age(self, instance, *args, **kwargs):
        return "%s (%s)" % (instance.birth_date, instance.get_age())
    

        
class ClientCreateView(LoginRequiredMixin, ClientActionMixin, CreateView):
    model = Client
    action = "create" # used for ClientActionMixin functionality
    form_class = ClientCreateForm
    
#     def get_context_data(self, **kwargs):
#         context = super(ClientCreateView, self).get_context_data(**kwargs)
#         context['address'] = self.address
#         return context
    
    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates blank versions of the form
        and its inline formsets.
        """
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
    
        address_form = AddressFormSet(prefix="address")
        
        phone_form = PhoneFormSet(prefix="phones",
                                initial=[
                                  {'phones-0-type': 'H',
                                   'phones-1-type': 'C',
                                   'phones-0-number': 'kjfbskb'}
                                  ])
        
        return self.render_to_response(
            self.get_context_data(form=form,
                                  address_form=address_form,
                                  address_form_helper=AddressFormSetHelper(),
                                  phone_form=phone_form,
                                  phone_form_helper=PhoneFormSetHelper()))

    # overrides ProcessFormView.post
    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        address_form = AddressFormSet(request.POST, prefix="address")
        phone_form = PhoneFormSet(request.POST, prefix="phones")
        
        if (form.is_valid() and address_form.is_valid() and phone_form.is_valid()):
            return self.form_valid(form, address_form, phone_form)
        else:
            return self.form_invalid(form, address_form, phone_form)
    
    def form_valid(self, form, address_form, phone_form):
        self.object = form.save()
        address_form.instance = self.object
        address_form.save()
        
        phone_form.instance = self.object
        phone_form.save()
        
        return HttpResponseRedirect(self.get_success_url())
    
    def form_invalid(self, form, address_form, phone_form):
        
        return self.render_to_response(
            self.get_context_data(form = form,
                                  address_form = address_form,
                                  address_form_helper=AddressFormSetHelper(),
                                  phone_form = phone_form,
                                  phone_form_helper=PhoneFormSetHelper()))
    
class ClientUpdateView(LoginRequiredMixin, ClientActionMixin, UpdateView):
    model = Client
    action = "update" # used for ClientActionMixin functionality
    form_class = ClientCreateForm
    #address=AddressFormSet();
       
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        form.use_for_update()
        #form.disable_fields()
        
        #address = Address.objects.get(client = self.object)
        address_form = AddressFormSet(prefix="address", instance = self.object)
        
        #phones = self.object.phone_set.all()
        phone_form = PhoneFormSet(prefix="phones", instance = self.object)
        
        return self.render_to_response(
            self.get_context_data(form=form,
                                  address_form=address_form,
                                  phone_form=phone_form))

    # overrides ProcessFormView.post
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        
        address_form = AddressFormSet(request.POST, prefix="address", instance = self.object)
        phone_form = PhoneFormSet(request.POST,  prefix="phones", instance = self.object)
        
        if (form.is_valid() and address_form.is_valid()  and phone_form.is_valid()):
            return self.form_valid(form, address_form, phone_form)
        else:
            return self.form_invalid(form, address_form, phone_form)

    def form_valid(self, form, address_form, phone_form):
        self.object = form.save(commit=False)
        self.object.save()
        
        instances = address_form.save(commit=False)
        for address in instances:
            address.save()
            
        phone_instances = phone_form.save(commit = False)
        for phone in phone_instances:
            phone.save()
        
        return HttpResponseRedirect(self.get_success_url())
    
    def form_invalid(self, form, address_form, phone_form):
        
        return self.render_to_response(
            self.get_context_data(form = form,
                                  address_form = address_form,
                                  phone_form = phone_form))

    


class ClientProfileView(LoginRequiredMixin, UpdateView):
    model = Client
    #template_name = 'clients/client_profile.html'
    tab = 'id'
    form_class=IdentificationForm
    
        
    def get_form_class(self):
        if self.kwargs['tab'] == 'id':
            form_class=IdentificationForm
        elif self.kwargs['tab'] == 'comm':
            form_class=CommunicationForm
        elif self.kwargs['tab'] == 'ref':
            form_class=ReferralForm
        else:
            raise ImproperlyConfigured('ClientProfileView requires form class for tab %s' % self.kwargs['tab'])
        
        return form_class
    
    def get_template_names(self):
        if self.kwargs['tab'] == 'id':
            return 'clients/client_identification.html'
        elif self.kwargs['tab'] == 'comm':
            return 'clients/client_communication.html'
        elif self.kwargs['tab'] == 'ref':
            return 'clients/client_referral.html'
        else:
            raise ImproperlyConfigured('ClientProfileView requires template name for tab %s' % self.kwargs['tab'])
    
    def get_success_url(self):
         return reverse_lazy('client_profile', kwargs={'tab': self.kwargs['tab'], 'pk':str(self.get_object().id)})

    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instantiating the form.
        """
        kwargs = super(ClientProfileView, self).get_form_kwargs()
        kwargs.update({
                'lang': self.request.LANGUAGE_CODE,
                });
        if self.kwargs['tab'] == 'ref' and hasattr(self, 'object'):
             kwargs.update({'instance': self.object.referral_set.latest(field_name='ref_date') })
            
        return kwargs   
    
    def get_context_data(self, **kwargs):
        logger.error('*** get_context_data: ENTERING ***!')
        context = super(ClientProfileView, self).get_context_data(**kwargs)
         
        self.object = self.get_object()
        
        context['tab']=self.kwargs['tab']
        address = self.object.address.all()[0]
        context['address'] = address
        phones = self.object.phones.all()
        context['phones'] = phones
        
        if self.kwargs['tab'] == 'ref':
            referral = self.object.referral_set.latest(field_name='ref_date')
            print >>sys.stderr, '*** put referral into context *** %s' % referral.reasons.all() 
            context['referral']  = self.object.referral_set.latest(field_name='ref_date')
#         # History tab ---------------------------------------
#         client_type=ContentType.objects.get_for_model(self.object)
#         # search with object_pk because object_id does not work (set to null)
#         logEntries = LogEntry.objects.filter(content_type__pk=client_type.id, object_pk=self.object.id)
#         
#         address_type = ContentType.objects.get_for_model(address)
#         address_logEntries = LogEntry.objects.filter(content_type__pk=address_type.id, object_pk=address.id)
#         
#         
#         context['logEntries'] = logEntries
#         context['address_logEntries'] = address_logEntries
         
        return context
     
    def get(self, request, *args, **kwargs):
        print >>sys.stderr, '*** ENTERING GET **** tab = [%s]' % self.kwargs['tab']
        
        self.object = self.get_object()
            
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if self.kwargs['tab'] == "comm":
            phone_form = PhoneFormSet(prefix="phones", instance = self.object)
            phone_form_helper = PhoneFormSetHelper()
        else:
            phone_form = None
            phone_form_helper = None
        
        if self.kwargs['tab'] == "ref":
            contact_form = ContactCreateForm(prefix="contact")
            contact_phone_form = PhoneFormSet(prefix="phones") #, instance = self.object.referral_set.latest(field_name='ref_date').contact)
            contact_phone_form_helper = PhoneFormSetHelper()
        else:
            contact_form = None
            contact_phone_form = None
            contact_phone_form_helper = None
            
        return self.render_to_response(
            self.get_context_data(form=form, 
                                  phone_form=phone_form, 
                                  phone_form_helper=phone_form_helper,
                                  contact_form=contact_form,
                                  contact_phone_form=contact_phone_form,
                                  contact_phone_form_helper=contact_phone_form_helper))

        
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        print >>sys.stderr, '*** ENTERING POST ****'
        
        if 'cancel' in request.POST:
            return HttpResponseRedirect(self.get_success_url())
        
        print >>sys.stderr, '*** submit form [%s] POST ****' % self.kwargs['tab']
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        #inline_forms = {}
        if self.kwargs['tab'] == "comm":
            phone_form = PhoneFormSet(request.POST,  prefix="phones", instance = self.object)
        else:
            phone_form = None
            
        print >>sys.stderr, 'data *** %s ****' % form.data
        forms_valid = form.is_valid()
        if phone_form != None:
            forms_valid = forms_valid and phone_form.is_valid()
        #for inline_form_name in inline_forms.keys():
        #    forms_valid = forms_valid and inline_forms[inline_form_name].is_valid()
            
        # validate
        if forms_valid:
            return self.form_valid(form, phone_form, **kwargs)
            
        else:
            return self.form_invalid(form, phone_form, **{'phone_form_helper':PhoneFormSetHelper()})
        
    def form_valid(self, form, phone_form, **kwargs):
        print >>sys.stderr, '*** form_valid ****' 
        
        if self.kwargs['tab'] == "ref":
            print >>sys.stderr, '*** save referral form****'
            referral = form.save(commit=False)
            form.save_m2m()
            referral.save()
        else:
            self.object = form.save(commit=False)
            form.save_m2m()
            self.object.save()
        
        if phone_form != None:
            print >>sys.stderr, '*** save phone form****'
            phone_instances = phone_form.save(commit = False)
            for phone in phone_instances:
                print >>sys.stderr, '*** save phone ****'
                phone.save()
            
            for old_phone in phone_form.deleted_objects:
                print >>sys.stderr, '*** delete phone ****'
                old_phone.delete()
#         for inline_form_name in inline_forms.keys():
#             form_instances = inline_forms[inline_form_name].save(commit=False)
#             for instance_target_object in form_instances:
#                 instance_target_object.save()
        #context["form"]=form
        #context[""]
        #return  render(request, 'accounts/account.html', context) 
        return HttpResponseRedirect(self.get_success_url())
    
    #def form_invalid(self, form, inline_forms):
    def form_invalid(self, form, phone_form, **kwargs):
        print >>sys.stderr, '*** form_invalid **** %s' % form.errors
        
        return self.render_to_response(
            self.get_context_data(form = form,
                                  phone_form = phone_form,
                                  **kwargs))

class ClientProfileMainView(LoginRequiredMixin, UpdateView):
    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instantiating the form.
        """
        kwargs = super(ClientProfileView, self).get_form_kwargs()
        kwargs.update({
                'lang': self.request.LANGUAGE_CODE,
                });
            
        return kwargs 
     
class ClientReferralView(LoginRequiredMixin, UpdateView):
    model = Client
    template_name = 'clients/client_referral.html'
    form_class=ReferralForm
    tab='ref'
    
    def get_success_url(self):
         return reverse_lazy('client_profile_referral', kwargs={'pk':str(self.get_object().id)})
    
    def get_referral(self):
        return self.get_object().get_referral()
        
    def get_context_data(self, **kwargs):
        logger.error('*** get_context_data: ENTERING ***!')
        context = super(ClientReferralView, self).get_context_data(**kwargs)
        
        # get client instance
        self.object = self.get_object() # self.object = Referral object
        
        context['tab']=self.tab
        address = self.object.address.all()[0]
        context['address'] = address
        phones = self.object.phones.all()
        context['phones'] = phones
        
        context['referral']  = self.get_referral()
#         # History tab ---------------------------------------
#         client_type=ContentType.objects.get_for_model(self.object)
#         # search with object_pk because object_id does not work (set to null)
#         logEntries = LogEntry.objects.filter(content_type__pk=client_type.id, object_pk=self.object.id)
#         
#         address_type = ContentType.objects.get_for_model(address)
#         address_logEntries = LogEntry.objects.filter(content_type__pk=address_type.id, object_pk=address.id)
#         
#         
#         context['logEntries'] = logEntries
#         context['address_logEntries'] = address_logEntries
         
        return context
    
    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instantiating the form.
        """
        kwargs = super(ClientReferralView, self).get_form_kwargs()
        kwargs.update({
                'lang': self.request.LANGUAGE_CODE,
                });
        if hasattr(self, 'object'):
             kwargs.update({'instance': self.get_referral() })
            
        return kwargs   
    
    def get(self, request, *args, **kwargs):
        print >>sys.stderr, '*** ENTERING GET ****' 
        
        self.object = self.get_object()
        
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        
        contact_form = ContactCreateForm(prefix="contact")
        contact_phone_form = PhoneFormSet(prefix="phones") 
        contact_phone_form_helper = PhoneFormSetHelper()
        
        print >>sys.stderr, '*** GET - render to response  ****' 
        
        return self.render_to_response(
            self.get_context_data(form=form, 
                                  contact_form=contact_form,
                                  contact_phone_form=contact_phone_form,
                                  contact_phone_form_helper=contact_phone_form_helper))

        
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        print >>sys.stderr, '*** ENTERING POST ClientReferralView ****'
        
        if 'cancel' in request.POST:
            return HttpResponseRedirect(self.get_success_url())
        
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        
        referral = self.get_context_data()['referral']
        
        contact_form = ContactCreateForm(request.POST, prefix="contact", instance=referral)
        contact_phone_form = PhoneFormSet(request.POST, prefix="phones", instance=referral.contact) #, instance = self.object.referral_set.latest(field_name='ref_date').contact)
        
        forms_valid = form.is_valid()
        if forms_valid:
            return self.form_valid(form, **{'contact_form':contact_form, 'contact_phone_form':contact_phone_form})
            
        else:
            return self.form_invalid(form, **{'contact_form':contact_form, 'contact_phone_form':contact_phone_form})
        
    def form_valid(self, form, **kwargs):
        print >>sys.stderr, '*** form_valid ClientReferralView****' 
        
        referral = form.save(commit=False)
        #form.save_m2m()
        print >>sys.stderr, '*** referral.contact:[%s] ****' % referral.contact
        referral.save()
        
        print >>sys.stderr, '** referral form contact [%s] **' % form.cleaned_data['contact']
        
        contact_form = kwargs['contact_form']
        print >>sys.stderr, '*** contact_form.data:[%s] ****' % contact_form.data
        print >>sys.stderr, '*** contact_form.initial:[%s]' % contact_form.initial
        contact_phone_form = kwargs['contact_phone_form']
#         if contact_form != None: # Adding a new contact
#             print >>sys.stderr, '*** adding NEW CONTACT ****'
#                 
#             contact = contact_form.save()
#             contact.save()
#              
#             if contact_phone_form != None:
#                 print >>sys.stderr, '*** save phone form****'
#                 phone_instances = contact_phone_form.save(commit = False)
#                 for phone in phone_instances:
#                     print >>sys.stderr, '*** save phone ****'
#                     phone.save()
#                 
#                 for old_phone in contact_phone_form.deleted_objects:
#                     print >>sys.stderr, '*** delete phone ****'
#                     old_phone.delete()
#                 
#             referral.contact = contact
#             referral.save()
#         else:
#             print >>sys.stderr, '*** CONTACT FORM is null ****'
            
        return HttpResponseRedirect(self.get_success_url())
    
    #def form_invalid(self, form, inline_forms):
    def form_invalid(self, form, **kwargs):
        print >>sys.stderr, '*** form_invalid **** %s' % form.errors
        
        return self.render_to_response(
            self.get_context_data(form = form,
                                  **kwargs))
        
    
class ClientOrderView(LoginRequiredMixin, UpdateView):
    model = Client
    template_name = 'clients/client_order.html'
    form_class=OrderForm
    tab='order'
    
    def get_success_url(self):
         return reverse_lazy('client_profile_order', kwargs={'pk':str(self.get_object().id)})
    
    def get_order(self):
        return self.object.get_order()
    
    def get_context_data(self, **kwargs):
        logger.error('*** get_context_data: ENTERING ***!')
        context = super(ClientOrderView, self).get_context_data(**kwargs)
        
        # get client instance
        self.object = self.get_object() # self.object = Referral object
        
        context['tab']=self.tab
        address = self.object.address.all()[0]
        context['address'] = address
        phones = self.object.phones.all()
        context['phones'] = phones
        
        context['order']  = self.get_order()
#         # History tab ---------------------------------------
#         client_type=ContentType.objects.get_for_model(self.object)
#         # search with object_pk because object_id does not work (set to null)
#         logEntries = LogEntry.objects.filter(content_type__pk=client_type.id, object_pk=self.object.id)
#         
#         address_type = ContentType.objects.get_for_model(address)
#         address_logEntries = LogEntry.objects.filter(content_type__pk=address_type.id, object_pk=address.id)
#         
#         
#         context['logEntries'] = logEntries
#         context['address_logEntries'] = address_logEntries
         
        return context
    
    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instantiating the form.
        """
        kwargs = super(ClientOrderView, self).get_form_kwargs()
        kwargs.update({
                'lang': self.request.LANGUAGE_CODE,
                });
        if hasattr(self, 'object'):
             kwargs.update({'instance': self.get_order() })
            
        return kwargs   
    
    def get(self, request, *args, **kwargs):
        print >>sys.stderr, '*** ENTERING GET ****' 
        
        self.object = self.get_object()
        order = self.get_order()
        
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        
        if order == None:
            title_stop_form=_('No stop scheduled')
            stop_btn_title=_('Schedule stop')
            show_stop_sched_btn=True
            show_stop_cancel_btn=False
            show_stop_form=False
            stop_form = OrderStopForm(prefix='stop')
        elif order.is_active():
            if order.has_stop():
                title_stop_form=_('Stop is scheduled')
                stop_btn_title=_('Cancel stop')
                show_stop_sched_btn=False
                show_stop_cancel_btn=True
                show_stop_form=True
                stop_form = OrderStopForm(prefix='stop', instance=order.get_stop())
            else:
               title_stop_form=_('No stop scheduled')
               stop_btn_title=_('Schedule stop')
               show_stop_sched_btn=True
               show_stop_cancel_btn=False
               show_stop_form=False 
               stop_form = OrderStopForm(prefix='stop')   
        elif order.is_stopped():
               title_stop_form=_('Order currently stopped')
               stop_btn_title=_('Cancel stop')
               # stop cannot be canceled once started
               show_stop_sched_btn=False
               show_stop_cancel_btn=False
               show_stop_form=True    
               stop_form = OrderStopForm(prefix='stop', instance=order.get_stop())
        else: # order.is_inactive()
            title_stop_form=''
            stop_btn_title=''
            show_stop_sched_btn=False
            show_stop_cancel_btn=False
            show_stop_form=False
            stop_form = OrderStopForm(prefix='stop')   
            
        print >>sys.stderr, '*** show_stop_cancel_btn %s ****' % show_stop_cancel_btn
        
        stop_form_helper = OrderStopFormHelper()
        if (order == None):
            delivery_form = DeliveryDefaultForm(prefix='deliv')
            mealside_form = DefaultMealSideFormSet(prefix="mealside")
        else:
            delivery_default = order.get_delivery_default()
            delivery_form = DeliveryDefaultForm(prefix='deliv', instance=delivery_default)
            mealside_form = DefaultMealSideFormSet(prefix="mealside", instance=delivery_default)
        
        
        return self.render_to_response(
            self.get_context_data(form=form,
                                  stop_form=stop_form,
                                  stop_form_helper=stop_form_helper,
                                  title_stop_form=title_stop_form,
                                  stop_btn_title=stop_btn_title,
                                  show_stop_sched_btn=show_stop_sched_btn,
                                  show_stop_cancel_btn=show_stop_cancel_btn,
                                  show_stop_form=show_stop_form,
                                  delivery_form=delivery_form, 
                                  mealside_form=mealside_form)
            )

        
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        print >>sys.stderr, '*** ENTERING POST ClientOrderView ****'
        
        if 'cancel' in request.POST:
            return HttpResponseRedirect(self.get_success_url())
        
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        
        forms_valid = form.is_valid()
        if forms_valid:
            print >>sys.stderr, '***  form  data %s ****' % form.data
            
            process_stop_form = form.cleaned_data['create_or_update_stop']
            if (process_stop_form):
                stop_form = OrderStopForm(request.POST, prefix='stop')
                stop_form_helper = OrderStopFormHelper()
            else:
                stop_form = None
            
            if stop_form != None:
                forms_valid = forms_valid and stop_form.is_valid()
    
        if (self.get_order() != None):
            delivery_default = self.get_order().get_delivery_default()
        else:
            delivery_default = None
            
        delivery_form = DeliveryDefaultForm(request.POST, prefix='deliv', instance=delivery_default)
        
        mealside_form = DefaultMealSideFormSet(request.POST, prefix="mealside",  instance=delivery_default)
        
        forms_valid = forms_valid and delivery_form.is_valid() and mealside_form.is_valid()
        
        if forms_valid:
            return self.form_valid(form, **{'stop_form': stop_form, 
                                            'delivery_form':delivery_form, 
                                            'mealside_form':mealside_form})
            
        else:
            if (stop_form == None):
                stop_form = OrderStopForm(prefix='stop')
            return self.form_invalid(form, **{'stop_form': stop_form, 
                                              'stop_form_helper': OrderStopFormHelper(),
                                              'delivery_form':delivery_form, 
                                              'mealside_form':mealside_form})
        
    def form_valid(self, form, **kwargs):
        print >>sys.stderr, '*** form_valid ClientOrderView****' 
        print >>sys.stderr, '***  form   CLEANED data %s ****' % form.cleaned_data
            
        order = form.save(commit=False)
        order.client = self.get_object()
        order.save()
        
        delete_stop_form = form.cleaned_data['remove_stop']
        if (delete_stop_form):
            print >>sys.stderr, '***  DELETE OBJECT ****' 
                
            order_stop = order.get_stop()
            order_stop.delete()
        else:
            stop_form = kwargs['stop_form']
            if stop_form != None:
                print >>sys.stderr, '***  STOP form   CLEANED data %s ****' % stop_form.cleaned_data
                order_stop = stop_form.save(commit=False);
                order_stop.order=order
                order_stop.save()
            else:
                print >>sys.stderr, '***  STOP form is None ****'
        
        delivery_form = kwargs['delivery_form']
        delivery = delivery_form.save(commit=False)
        delivery.order=order
        delivery.save()
        # get instances of DefaultMealSide objects
        mealside_form = kwargs['mealside_form']
        mealside_instances = mealside_form.save(commit=False)
        for mealside in mealside_instances:
            mealside.delivery = delivery
            mealside.save()
        
        for old_mealside in mealside_form.deleted_objects:
            old_mealside.delete()
            
        return HttpResponseRedirect(self.get_success_url())
    
    #def form_invalid(self, form, inline_forms):
    def form_invalid(self, form, **kwargs):
        print >>sys.stderr, '*** form_invalid **** %s' % form.errors
        
        return self.render_to_response(
            self.get_context_data(form = form,
                                  **kwargs))
    
    