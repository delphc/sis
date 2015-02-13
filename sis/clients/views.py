#-*- coding: utf-8 -*-
import datetime
import logging
import sys

from django import forms
from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.contrib.formtools.wizard.views import SessionWizardView
from django.core.urlresolvers import reverse_lazy
from django.core.exceptions import ImproperlyConfigured
from django.forms.models import formset_factory
from django.http import HttpResponseRedirect, Http404
from django.utils.translation import ugettext as _
from django.views.generic import FormView, CreateView, UpdateView, DetailView, ListView, TemplateView
from django.views.generic.detail import SingleObjectMixin

from braces.views import LoginRequiredMixin, SetHeadlineMixin
#from django_datatables_view.base_datatable_view import BaseDatatableView
from datatableview.views import DatatableView
from datatableview.helpers import link_to_model
from auditlog.models import LogEntry
from cbvtoolkit.views import MultiFormView

from .forms import  ClientCreateForm, ClientSetupForm, IdentificationForm, CommunicationForm, ReferralForm

from contacts.forms import  FullContactForm, ContactInfoForm, AddressForm, AddressFormSet, AddressFormSetHelper, HomePhoneFormSet,  PhoneFormSetHelper
from orders.forms import OrderForm, OrderStopForm, OrderStopFormHelper, DeliveryDefaultForm, DefaultMealSideFormSet

# Import the customized User model
from .models import Client, Referral
from core.models import PendedForm, PendedValue
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
    success_url = 'client_setup'
    cancel_url = 'client_list'
    
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
        
        return self.render_to_response(
            self.get_context_data(form=form))

    # overrides ProcessFormView.post
    def post(self, request, *args, **kwargs):
        
        if 'cancel' in request.POST:
            return HttpResponseRedirect(reverse_lazy(self.cancel_url))
        
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        
        if (form.is_valid()):
            return self.form_valid(form)
        else:
            return self.form_invalid(form)
    
    def form_valid(self, form):
        self.object = form.save()
        
        return HttpResponseRedirect(
                                    #overrides success_url
                                    reverse_lazy('client_setup', kwargs={'pk':str(self.object.pk)}))
    
    def form_invalid(self, form):
        
        return self.render_to_response(
            self.get_context_data(form = form))
        

        
#class ClientSetupWizardView(SingleObjectMixin, SessionWizardView):
    
class ClientSetupView(LoginRequiredMixin, SingleObjectMixin, TemplateView):
    model = Client
    pend_button_name = 'pend'
    template_name = "clients/client_setup_base.html"
    FORMS = { 
             # section Identification
            "id": IdentificationForm, # instance = Client
            # section Contact
            "contact": ContactInfoForm, # instance = ContactInfo
            "address": AddressForm,
            "phones" : HomePhoneFormSet,
            # section communication
            "comm": CommunicationForm, # instance = Client
            # section referral
            "ref": ReferralForm # instance = Referral
            }
    
    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        
        context = super(ClientSetupView, self).get_context_data(**kwargs)
        
        return context 
    
#     def get_form_kwargs(self):
#         """
#         Returns a dictionary of arguments to pass into the form instantiation.
#         If resuming a pended form, this will retrieve data from the database.
#         """
#         object_pk = self.kwargs.get(self.pk_url_kwarg)
#         if 'resume' in self.request.path_info:
#             print >>sys.stderr, '*** PENDING form *** %s' 
#             import_path = self.get_import_path(self.get_form_class())
#             return { 'object_pk': object_pk, 'data': self.get_pended_data(import_path, object_pk)}
#         else:
#             print >>sys.stderr, '*** REGULAR form *** %s' 
#             
#             return super(ClientSetupView, self).get_form_kwargs()
    
    def get_pended_data(self, import_path, object_pk):
        data = PendedValue.objects.filter(form__form_class=import_path, form__object_pk=object_pk)
        return dict((d.name, d.value) for d in data)

    def get_import_path(self, form_class):
        return '{0}.{1}'.format(form_class.__module__, form_class.__name__)
    
    def pend_value(self, pended_form, form, prefix, field_name ):
        field = form.fields[field_name]
        field_value = ""
        if isinstance(field, forms.DateField):
            field_value = form._raw_value(field_name)
        else:
            # checkboxes are posted only if checked
            if prefix+"-"+field_name in form.data.keys():
                field_value = form.data[prefix+"-"+field_name]
                
        if field_value:
            pended_value, value_created = pended_form.data.get_or_create(name=field_name, defaults={'value':field_value })
            if not value_created:
                print >>sys.stderr, '***  update pended value for *** %s with %s' % ( field_name, field_value )
                
                pended_value.value=field_value  
                pended_value.save()      
            else:
                print >>sys.stderr, '***  created pended value for *** %s with %s' % ( field_name, field_value )
        else:
            print >>sys.stderr, '***  no value to save' 
            
        
    def form_pended(self, request, form_prefix, form_class):
        form = form_class(request.POST, prefix=form_prefix)
        if form.has_changed():
            print >>sys.stderr, '***  form HAS CHANGED - save pended_form %s' % form.data 
            import_path = self.get_import_path(form_class)
            object_pk = self.get_object().pk
            pended_form, created = PendedForm.objects.get_or_create(form_class=import_path,
                                                       object_pk=object_pk)
            for name in form.fields.keys():
                print >>sys.stderr, '***  get or create pended value for *** %s' % name
                
                self.pend_value(pended_form, form, form_prefix, name)
        else:
            print >>sys.stderr, '***  form has NOT CHANGED - skip form_pended' 
                
    
    def get_form_pended(self, form_prefix, form_class):
        data=self.get_pended_data( self.get_import_path(form_class), self.object.pk)
        
        if data:
            print >>sys.stderr, '***  RETRIEVED pended data *** %s' % data
        
            form = form_class( prefix=form_prefix, **{ 'initial':data }) 
        else:
            if form_prefix == "id":
                form = form_class( prefix=form_prefix, instance=self.object) 
            else:
                form = form_class( prefix=form_prefix)
    
        return form
    
    def get_form_final (self, request, form_prefix, form_class):
        self.object = self.get_object()
        
        if (form_prefix == "id"):
            form = form_class(request.POST, prefix=form_prefix, instance=self.object)
        else:
            form = form_class(request.POST, prefix=form_prefix)
        
        return form
        
             
       
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        context = self.get_context_data()
        for form_prefix in self.FORMS.keys():
            print >>sys.stderr, '***  get form  *** %s' % form_prefix
            form = self.get_form_pended( form_prefix, self.FORMS[form_prefix] )
            context[form_prefix+"_form"] = form
            
#         data=self.get_pended_data( self.get_import_path(IdentificationForm), self.object.pk)
#         
#         if data:
#             print >>sys.stderr, '***  RETRIEVED pended data *** %s' % data
#         
#             id_form = IdentificationForm( prefix="id", **{ 'initial':data }) 
#         else:
#             id_form = IdentificationForm( prefix="id", instance=self.object) 
#         contact_form = FullContactForm( prefix="contact")
#         comm_form = CommunicationForm(prefix="comm", instance=self.object)
#        referral_form = ReferralForm(prefix="ref")# target instance (referral) has not been created yet
        
        print >>sys.stderr, '***  context  *** %s' % context
        
        return self.render_to_response( context )
#             self.get_context_data(id_form=id_form,
#                                   contact_form=contact_form,
#                                   comm_form=comm_form,
#                                   referral_form=referral_form))


    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        if self.pend_button_name in self.request.POST:
            #form_class = Identification
            for form_prefix in self.FORMS.keys():
                print >>sys.stderr, '***  pend form  *** %s' % form_prefix
                form = self.form_pended( request, form_prefix, self.FORMS[form_prefix] )
            
            messages.success(request, _("Your changes have been saved successfully for later use"))
            return HttpResponseRedirect(
                                        reverse_lazy('client_setup', kwargs={'pk':str(self.object.pk)}))

        else:
            all_forms_valid = True
            all_forms = {}
            for form_prefix in self.FORMS.keys():
                print >>sys.stderr, '***  pend form  *** %s' % form_prefix
                form = self.get_form_final( request, form_prefix, self.FORMS[form_prefix] )
                
                all_forms_valid = all_forms_valid and form.is_valid()
                all_forms[form_prefix] = form
            
            if all_forms_valid:
                return self.form_valid(all_forms)
            else:
                return self.form_invalid(all_forms)
        
        
    def form_valid(self, all_forms):
        id_form = all_forms['id']
        contact_form = all_forms['contact']
        address_form = all_forms['address']    
        phones_form = all_forms['phones']
        comm_form = all_forms['comm']
        referral_form = all_forms['ref']
        
        self.object = id_form.save()
        comm_form.instance = self.object
        self.object = comm_form.save()
        # CONTACT section contains 3 forms : 
        # contact_form (for email address), address_form and referral_form
        contact_info = contact_form.save(commit=False)
        client_type = ContentType.objects.get_for_model(self.object)
        contact_info.content_type = client_type
        contact_info.content_object = self.object
        contact_info.save()
        address = address_form.save(commit=False)
        address.contact_info = contact_info
        address.save()
        print >>sys.stderr, '***  form data *** %s' % contact_form.data
            
        phones_form.instance = contact_info
        phones_form.save()
        
        referral = referral_form.save(commit=False)
        referral.client = self.object
        referral.save()
        referral_form.save_m2m()
        
        self.object.status = Client.ACTIVE
        self.object.save()
        
        return HttpResponseRedirect(self.object.get_absolute_url())
    
    def form_invalid(self, all_forms):
        
        context = self.get_context_data()
        
        for form_prefix in all_forms.keys():
            context[form_prefix+"_form"] = all_forms[form_prefix]
        
        context['invalid_forms']=True
        messages.error(self.request, _("Please correct errors and save again."))
        
        return self.render_to_response(context)
    
    
class OldClientCreateView(LoginRequiredMixin, ClientActionMixin, CreateView):
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
        
        phone_form = HomePhoneFormSet(prefix="phones",
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
        phone_form = HomePhoneFormSet(request.POST, prefix="phones")
        
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
        phone_form = HomehoneFormSet(prefix="phones", instance = self.object)
        
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
        phone_form = HomePhoneFormSet(request.POST,  prefix="phones", instance = self.object)
        
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

class ClientProfileMixin(LoginRequiredMixin, SingleObjectMixin):
    model = Client
    tab = "id"
    
    def get_context_data(self, **kwargs):
        context = super(ClientProfileMixin, self).get_context_data(**kwargs)
        context['tab']=self.tab
         
        self.object = self.get_object()
        
        contact_info = self.object.get_contact_info()
        context['contact_info'] = contact_info
        address = contact_info.get_address()
        context['address'] = address
        phones = contact_info.get_phones()
        context['phones'] = phones
        
        return context

class ClientIdentificationHeadlineMixin(SetHeadlineMixin):
    headline=_("Client Identification")

class ClientContactHeadlineMixin(SetHeadlineMixin):
    headline=_("Contact information")

class ClientCommunicationHeadlineMixin(SetHeadlineMixin):
    headline=_("Useful information for communication")

class ClientReferralHeadlineMixin(SetHeadlineMixin):
    headline=_("Referral information")
    
class ClientProfileIdentificationView(ClientProfileMixin, ClientIdentificationHeadlineMixin, DetailView):
    template_name = "clients/client_profile_identification.html"
    tab = "id"
    
class ClientProfileContactView(ClientProfileMixin, ClientContactHeadlineMixin, DetailView):
    template_name = "clients/client_profile_contact.html"
    tab = "contact"
    
    
class ClientProfileCommunicationView(ClientProfileMixin, ClientCommunicationHeadlineMixin, DetailView):
    template_name = "clients/client_profile_communication.html"
    tab = "comm"
    
class ClientProfileReferralView(ClientProfileMixin, ClientReferralHeadlineMixin, DetailView):
    template_name = "clients/client_profile_referral.html"
    tab = "ref"

    def get_context_data(self, **kwargs):
        context = super(ClientProfileReferralView, self).get_context_data(**kwargs)

        self.object = self.get_object()
        context['referral']=self.object.get_referral()
        context['ref_contact']=self.object.get_referral().contact
    
        return context

class ClientProfileEditMainView(ClientProfileMixin, FormView):
    success_url = ''
    form_classes = {}
    
#              # section Identification
#             "id": IdentificationForm, # instance = Client
#             # section Contact
#             "contact": ContactInfoForm, # instance = ContactInfo
#             "address": AddressForm,
#             "phones" : HomePhoneFormSet,
#             # section communication
#             "comm": CommunicationForm, # instance = Client
#             # section referral
#             "ref": ReferralForm # instance = Referral
#             }
    
    def get_success_url(self):
        return reverse_lazy(self.success_url, kwargs={'pk':str(self.get_object().id)})
    
    def get_form_kwargs(self, prefix):
        kwargs = super(ClientProfileEditMainView, self).get_form_kwargs()
        kwargs.update({
            'prefix': prefix,
            'instance': self.get_object(),
            'edit': True
        })
        if self.request.method in ('POST', 'PUT'):
            print >>sys.stderr, '*** include post request **** %s' % self.request.POST
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
                })
        return kwargs
    
    def get_form(self, form_class, prefix):
        return form_class(**self.get_form_kwargs(prefix))
    
    def get_forms(self, request=None):
        forms = {}
        for form_prefix in self.form_classes.keys():
            form_class = self.form_classes[form_prefix]
            form = self.get_form(form_class, form_prefix)
            forms[form_prefix] = form
        
        return forms
            
    def get(self, request, *args, **kwargs):
        
        self.object = self.get_object()
        
        forms = self.get_forms()
        context = self.get_context_data()
        
        for form_prefix in self.form_classes.keys():
            context[form_prefix+"_form"] = forms[form_prefix]
            
        
        return self.render_to_response(context)


        #return super(ClientProfileEditMainView, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        print >>sys.stderr, '*** ENTERING POST **** %s' % request.POST
        
        forms = self.get_forms()
        all_forms_valid = True
        for form_prefix in self.form_classes.keys():
            print >>sys.stderr, '*** process form **** %s' % form_prefix
            form_valid = forms[form_prefix].is_valid()
            if form_valid:
                print >>sys.stderr, '*** VALID ****'
            else:
                print >>sys.stderr, '*** INVALID !!!   *** %s' % forms[form_prefix].is_bound

            all_forms_valid = all_forms_valid and form_valid
            
        if all_forms_valid:
            print >>sys.stderr, '*** VALID ****'
        
            return self.form_valid(forms)          
        else:
            print >>sys.stderr, '*** INVALID !!!  ****'
        
            return self.form_invalid(forms)
        
    def form_valid(self, forms):
        
        for form_prefix in self.form_classes.keys():
            forms[form_prefix].save()
        
        return HttpResponseRedirect(self.get_success_url())
    
    def form_invalid(self, forms):
        
        context = self.get_context_data()
        
        for form_prefix in self.form_classes.keys():
            context[form_prefix+"_form"] = forms[form_prefix]
            
        return self.render_to_response( context)
        
class ClientProfileEditIdentificationView(ClientIdentificationHeadlineMixin, ClientProfileEditMainView):
    template_name = "clients/client_profile_identification_edit.html"
    tab = "id"
    form_classes = {
                    "id": IdentificationForm
                    }
    success_url = 'client_profile_identification'
    FORMS = {
            "id": IdentificationForm # instance = Client
            }
    
#     def get_form_kwargs(self):
#         kwargs = super(ClientProfileEditIdentificationView, self).get_form_kwargs()
#         kwargs.update({
#             'edit': True
#         })
#         return kwargs
        

    
class ClientProfileEditContactView(ClientContactHeadlineMixin, ClientProfileEditMainView):
    template_name = "clients/client_profile_contact_edit.html"
    tab = "contact"
    form_classes = {
                    "contact" : ContactInfoForm,
                    "address" : AddressForm,
                    "phones" : HomePhoneFormSet
                    }
    success_url = 'client_profile_contact'
    
    def get_form_kwargs(self, prefix):
        kwargs = super(ClientProfileEditContactView, self).get_form_kwargs(prefix)
        
        contact_info = self.get_object().get_contact_info()
        if prefix == "address":
            form_instance = contact_info.get_address()
        else:
            form_instance = contact_info
        kwargs.update({
            'instance': form_instance
        })
            
        return kwargs
    
    
#     def form_valid(self, forms):
#         self.object = self.get_object() # client
#         contact_form = forms['contact']
#         address_form = forms['address']
#         phones_form = forms['phones']
#         
#         print >>sys.stderr, '*** form_valid contact **** %s', contact_form.instance
#         print >>sys.stderr, '*** form_valid address_form **** %s', address_form.instance
#         print >>sys.stderr, '*** form_valid phones_form **** %s', phones_form.instance
#         
#         for form_prefix in self.form_classes.keys():
#             forms[form_prefix].save()
#         
#         return HttpResponseRedirect(self.get_success_url())


class ClientProfileEditCommunicationView(ClientCommunicationHeadlineMixin, ClientProfileEditMainView):
    template_name = "clients/client_profile_communication_edit.html"
    tab = "comm"
    form_classes = {
                    "comm" : CommunicationForm
                    }
    success_url = 'client_profile_communication'
    
class ClientProfileEditReferralView(ClientReferralHeadlineMixin, ClientProfileEditMainView):
    template_name = "clients/client_profile_referral_edit.html"
    form_classes = {
                    "ref" : ReferralForm
                    }
    tab = "ref"
    success_url = 'client_profile_referral'

    def get_form_kwargs(self, prefix):
        kwargs = super(ClientProfileEditReferralView, self).get_form_kwargs(prefix)
        
        referral = self.get_object().get_referral()
        
        kwargs.update({
            'instance': referral
        })
        return kwargs  
    
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
        contact_info = self.object.get_contact_info()
        address = contact_info.get_address()
        context['address'] = address
        phones = contact_info.get_phones()
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
            phone_form = HomePhoneFormSet(prefix="phones", instance = self.object)
            phone_form_helper = PhoneFormSetHelper()
        else:
            phone_form = None
            phone_form_helper = None
        
        if self.kwargs['tab'] == "ref":
            contact_form = ContactCreateForm(prefix="contact")
            contact_phone_form = HomePhoneFormSet(prefix="phones") #, instance = self.object.referral_set.latest(field_name='ref_date').contact)
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
            phone_form = HomePhoneFormSet(request.POST,  prefix="phones", instance = self.object)
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
        contact_phone_form = HomePhoneFormSet(prefix="phones") 
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
        contact_phone_form = HomePhoneFormSet(request.POST, prefix="phones", instance=referral.contact) #, instance = self.object.referral_set.latest(field_name='ref_date').contact)
        
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
    
    