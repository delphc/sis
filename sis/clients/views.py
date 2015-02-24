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
from django.core.urlresolvers import reverse, reverse_lazy
from django.core.exceptions import ImproperlyConfigured
from django.forms.models import formset_factory
from django.http import HttpResponseRedirect, Http404
from django.utils.translation import ugettext as _
from django.views.generic import FormView, CreateView, UpdateView, DeleteView, DetailView, ListView, TemplateView
from django.views.generic.detail import SingleObjectMixin

from auditlog.models import LogEntry
from cbvtoolkit.views import MultiFormView
from braces.views import LoginRequiredMixin, SetHeadlineMixin
from datatableview.utils import get_datatable_structure
from datatableview.views import DatatableView
from datatableview.helpers import link_to_model, make_boolean_checkmark
from related.views import CreateWithRelatedMixin


from .forms import  ClientCreateForm, ClientSetupForm, IdentificationForm, CommunicationForm, ReferralForm, RelationshipFormSet, RelationshipForm

from contacts.forms import  ContactInfoForm, AddressForm, AddressFormSet, AddressFormSetHelper, HomePhoneFormSet,  PhoneFormSetHelper
from orders.forms import OrderForm, MealDefaultForm, MealDefaultMealFormSet, MealDefaultSideFormSet

# Import the customized User model
from .models import Client, Referral, Relationship
from core.models import PendedForm, PendedValue
from contacts.models import Address, Phone
from orders.models import Order, ServiceDay, MealDefault

from core.views import AjaxTemplateMixin, ModalMixin, MultipleModalMixin

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
        

        
    
class ClientSetupView(LoginRequiredMixin, MultipleModalMixin,SingleObjectMixin, TemplateView):
    """
        To add a new section :
        - add prefix / formclass to FORMS dict
          the form will be accessible from the template as [prefix]_form
        - update form_valid to manage the new form
    """
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
            "ref": ReferralForm, # instance = Referral
            # section relationship
            "rel": RelationshipFormSet,
            # section meal service
            "order": OrderForm,            # main settings of meal order
#            "mealdef" : MealDefaultForm,   # main settings of meal defaults
            # FORMS["meals"] is actually a formset dict :  
            # key = meals_[day.sort_order] (1 key for each active service day + 1 for 'everyday' special day)
            # value = MealDefaultMealFormSet instance to set nb and size of meals for this day
            "meals" : MealDefaultMealFormSet,  
            # FORMS["meals"] is actually a formset dict :  
            # key = mealsides_[day.sort_order] (1 key for each active service day + 1 for 'everyday' special day)
            # value = MealDefaultSideFormSet instance to set nb of sides for this day 
            "mealsides": MealDefaultSideFormSet 
            }
    target_modals = { 'contact_create_url' : 'contact_create' }
    
    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        
        context = super(ClientSetupView, self).get_context_data(**kwargs)
        
        context['meal_service_days'] = ServiceDay.objects.get_days_for_meal_defaults()
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
        
    def get_meal_forms(self, request, context, form_prefix, usage):
        meal_forms = {}
        meal_service_days = context['meal_service_days']
        for day in meal_service_days.all():
            day_form_prefix = form_prefix+"_"+str(day.sort_order)
            if usage == "pend_get":
                form = self.get_form_pended( day_form_prefix, self.FORMS[form_prefix] )
                
            elif usage == "pend_post":
                form = self.form_pended( request, day_form_prefix, self.FORMS[form_prefix] )
                
            elif usage == "final_post":
                form = self.get_form_final( request, day_form_prefix, self.FORMS[form_prefix] )
            
            meal_forms[day.sort_order] = form
        
        context[form_prefix+"_form"] = meal_forms
        
        return meal_forms
    
    
    def validate_all_meal_forms(self, request, context, all_forms):
        """
            No need to validate all meal forms
            It depends on values entered in order form fields :
            meal_defaults_type
                same defaults for everyday -> validate forms corresponding to 'everyday' special service day
                day-specific -> 
                    for ongoing service type -> validate forms corresponding to days selected in 'days' field
                    for episodic service type -> validate forms for each active service day
                    
        """
        all_forms_valid = True
        order_form = all_forms["order"]
        service_type = order_form.cleaned_data['type']
        meal_defaults_type = order_form.cleaned_data['meal_defaults_type']
        print >>sys.stderr, '***  defaults type  *** %s' % meal_defaults_type
        selected_days = order_form.cleaned_data['days']
        print >>sys.stderr, '***  selected days  *** %s' % selected_days
        
        for form_prefix in self.FORMS.keys():
            if "meal" in form_prefix:
                meal_forms = self.get_meal_forms(request, context, form_prefix, "final_post")
                
                # build days_sort_order_list depending on values entered in order form fields
                # This list will determine for which days forms and formset need to be validated
                # Days not listed will be ignored
                days_sort_order_list = []
                if meal_defaults_type == Order.DEFAULTS_TYPE_EVERYDAY['code']:
                    everyday = ServiceDay.objects.get_meal_service_everyday()
                    days_sort_order_list.append(everyday.sort_order)
                else:
                    if service_type == Order.ONGOING:
                        for selected_day in selected_days:
                            days_sort_order_list.append(selected_day.sort_order)
                    else:
                        active_days = ServiceDays.objects.get_meal_service_days()
                        for active_day in active_days.all():
                            days_sort_order_list.append(active_day.sort_order)
                    
                meal_forms_valid = self.validate_meal_forms(context, request, form_prefix, meal_forms, days_sort_order_list)
                            
                all_forms_valid = all_forms_valid and meal_forms_valid
                all_forms[form_prefix] = meal_forms
                
        return all_forms_valid
                    
                
    def validate_meal_forms(self, request, context, form_prefix, meal_forms, day_sort_order_list):
        """
            The days_sort_order_list indicates for which days forms and formset need to be validated
            Days not listed will be ignored
        """
        #order_form = context['order_form']
        all_forms_valid = True
        
        for day_sort_order in day_sort_order_list:
            form_valid = meal_forms[day_sort_order].is_valid()
            if not form_valid:
                print >>sys.stderr, '***  INVALID form  *** %s - %s - %s' % (form_prefix, str(day_sort_order), meal_forms[day_sort_order].errors)
                #messages.error(self.request, form.non_field_errors())
            all_forms_valid = all_forms_valid and form_valid
            
        return all_forms_valid
       
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        context = self.get_context_data()
        for form_prefix in self.FORMS.keys():
            print >>sys.stderr, '***  get form  *** %s' % form_prefix
            if "meal" in form_prefix:
                self.get_meal_forms(request, context, form_prefix, "pend_get")
            else:
                form = self.get_form_pended( form_prefix, self.FORMS[form_prefix] )
                context[form_prefix+"_form"] = form
                    
        return self.render_to_response( context )

    
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        context = self.get_context_data()
        
        if self.pend_button_name in self.request.POST:
            #form_class = Identification
            for form_prefix in self.FORMS.keys():
                print >>sys.stderr, '***  pend form  *** %s' % form_prefix
                if "meal" in form_prefix:
                    self.get_meal_forms(request, context, form_prefix, "pend_post")
                else:
                    form = self.form_pended( request, form_prefix, self.FORMS[form_prefix] )
            
            messages.success(request, _("Your changes have been saved successfully for later use"))
            return HttpResponseRedirect(
                                        reverse_lazy('client_setup', kwargs={'pk':str(self.object.pk)}))

        else:
            all_forms_valid = True
            all_forms = {}
            for form_prefix in self.FORMS.keys():
                if "meal" not in form_prefix:
                    form = self.get_form_final( request, form_prefix, self.FORMS[form_prefix] )
                    form_valid = form.is_valid()
                    if form_valid:
                        print >>sys.stderr, '***  valid form  *** %s - %s' % ( form_prefix, form.errors)
                    else:
                        print >>sys.stderr, '***  INVALID form  *** %s' % form_prefix
                        messages.error(self.request, form.non_field_errors())
                    
                    #all_forms_valid = all_forms_valid and form.is_valid()
                    all_forms_valid = all_forms_valid and form_valid
                    all_forms[form_prefix] = form
            
            meal_forms_valid = self.validate_all_meal_forms(request, context, all_forms)
            all_forms_valid = all_forms_valid and meal_forms_valid
                
            if all_forms_valid:
                return self.form_valid(all_forms)
            else:
                return self.form_invalid(all_forms)

    def save_meal_default(self, meals_forms, sides_forms, order, day):
        mealdef = MealDefault(order=order, day=day) 
        mealdef.save()
        
        meals_formset = meals_forms[day.sort_order]
        meals_formset.instance = mealdef
        meals_formset.save()
        
        sides_formset = sides_forms[day.sort_order]
        sides_formset.instance = mealdef
        sides_formset.save()
    
    def form_valid(self, all_forms):
        """
            all_forms is a dict that contains valid forms
            each form can be retrieved by the prefix defined in FORMS attribute
        """
        id_form = all_forms['id']
        contact_form = all_forms['contact']
        address_form = all_forms['address']    
        phones_form = all_forms['phones']
        comm_form = all_forms['comm']
        referral_form = all_forms['ref']
        relationship_form = all_forms['rel']
        
        order_form = all_forms['order']        # OrderForm,
        # mealdef_form is actually a form dict :  
        # key = meals_[day.sort_order] (1 key for each active service day + 1 for 'everyday' special day)
        # value = MealDefaultForm instance to hold main settings for this day 
        #mealdef_forms = all_forms['mealdef']     
        # meals_form is actually a formset dict :  
        # key = meals_[day.sort_order] (1 key for each active service day + 1 for 'everyday' special day)
        # value = MealDefaultMealFormSet instance to set nb and size of meals for this day 
        meals_forms = all_forms['meals']
        # sides_form is actually a formset dict :  
        # key = mealsides_[day.sort_order] (1 key for each active service day + 1 for 'everyday' special day)
        # value = MealDefaultSideFormSet instance to set nb of sides for this day 
        sides_forms = all_forms['mealsides']  
        
        
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
        
        relationship_form.instance = self.object
        relationship_form.save()
        

        order = order_form.save(commit=False)
        order.client = self.object
        order.save()
        order_form.save_m2m()
        
        meal_defaults_type = order_form.cleaned_data['meal_defaults_type']
        if meal_defaults_type == Order.DEFAULTS_TYPE_EVERYDAY['code']:
            # same defaults for every day
            everyday_serviceday = ServiceDay.objects.get_meal_service_everyday()
            self.save_meal_default(meals_forms, sides_forms, order, everyday_serviceday)
        
        else:
            # different defaults set per day
            # if service type is ongoing
            #    need to save one MealDefault for each selected day
            if order.type == Order.ONGOING:
                for day in order.days.all():
                    self.save_meal_default(meals_forms, sides_forms, order, day)
            # if service type is episodic
            #    need to save one MealDefault for each active day of meal service
            else:
                for day in ServiceDay.get_meal_service_days().all():
                    self.save_meal_default(meals_forms, sides_forms, order, day)
                    
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
    
    



class ClientProfileMixin(LoginRequiredMixin, SingleObjectMixin):
    model = Client
    tab = "id"
    
    def get_context_data(self, **kwargs):
        self.object = self.get_object()
        
        context = super(ClientProfileMixin, self).get_context_data(**kwargs)
        context['tab']=self.tab
        
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

class ClientRelationshipHeadlineMixin(SetHeadlineMixin):
    headline=_("Relationships")

class ClientOrderHeadlineMixin(SetHeadlineMixin):
     headline=_("Meal default")
     
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
    
class ClientProfileRelationshipView(MultipleModalMixin, ClientProfileMixin, ClientRelationshipHeadlineMixin, DetailView):    
    template_name = "clients/client_profile_relationship.html"
    tab = "rel"
    target_modals = {
                     'contact_create_url' : 'contact_create'
    }
    
    def get_context_data(self, **kwargs):
        context = super(ClientProfileRelationshipView, self).get_context_data(**kwargs)
 
        relationship_view = ClientRelationshipListView()
        model = relationship_view.model
        options = relationship_view.get_datatable_options()
        datatable = get_datatable_structure(reverse_lazy('client_relationship_list', kwargs={'pk':str(self.get_object().id)} ), options, model=model)
 
        context['datatable'] = datatable
        
        context['rel_create_url'] = reverse_lazy('relationship_create', kwargs={'pk':str(self.get_object().id)})
        return context
    
class ClientRelationshipListView(DatatableView):
    model = Relationship

    datatable_options = {
        'structure_template': "datatableview/bootstrap_structure.html",
        'columns': [
            ('Contact', 'contact__full_name'),
            ('Relation type', 'rel_type'),
            ('Phone', None, 'get_entry_phones'),
            ('Emergency', 'emergency', make_boolean_checkmark), # this column is not searchable because sorting is done at code level (not db query)
            ('Follow-up', 'follow_up', make_boolean_checkmark),
            ('', None, 'get_edit_link'),
            ('', None, 'get_remove_link')
            ],
    }
    
    implementation = u""
   
    def get_queryset(self):
        print >>sys.stderr, '***  get_initial_queryset  *** %s' % self.kwargs['pk']
        
        # return queryset used as base for futher sorting/filtering
        # these are simply objects displayed in datatable
        # You should not filter data returned here by any filter values entered by user. This is because
        # we need some base queryset to count total number of records.
        return Relationship.objects.filter(client=self.kwargs['pk'])

    
    def get_entry_phones(self, instance, *args, **kwargs):
        return "%s" % instance.contact.get_phones()
    
    def get_edit_link(self, instance, *args, **kwargs):
        edit_url=reverse_lazy("relationship_edit", kwargs={'pk':str(instance.id)})
        return '<a class="btn btn-primary" href="%s">%s</a>' % (edit_url, _("Edit"))
    
    def get_remove_link(self, instance, *args, **kwargs):
        
        remove_url=reverse_lazy("relationship_delete", kwargs={'pk':str(instance.id)})
        return '<a class="btn btn-primary" href="%s">%s</a>' % (remove_url, _("Remove"))

class RelationshipCreateView(CreateWithRelatedMixin, AjaxTemplateMixin, CreateView):
    model = Relationship
    form_class = RelationshipForm
    related_model = Client
    template_name = "clients/client_profile_relationship_edit.html"
    ajax_template_name = "clients/relationship_form_inner.html"
    
    def get_success_url(self):
        return reverse_lazy('client_profile_relationship', kwargs={'pk':str(self.related_object.id)})

class RelationshipEditView(UpdateView):
    model = Relationship

class RelationshipDeleteView(DeleteView):
    model = Relationship
    
class ClientProfileOrderView(ClientProfileMixin, ClientOrderHeadlineMixin, DetailView):
    template_name = "clients/client_profile_order.html"
    tab = "order"

    def get_context_data(self, **kwargs):
        context = super(ClientProfileOrderView, self).get_context_data(**kwargs)

        self.object = self.get_object()
        context['order']=Order.objects.get_latest_order_for_client(self.object)
        context['meal_service_days'] = ServiceDay.objects.get_days_for_meal_defaults()
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
    
class ClientProfileEditReferralView(MultipleModalMixin, ClientReferralHeadlineMixin, ClientProfileEditMainView):
    template_name = "clients/client_profile_referral_edit.html"
    form_classes = {
                    "ref" : ReferralForm
                    }
    tab = "ref"
    success_url = 'client_profile_referral'
    target_modals = { 'contact_create_url' : 'contact_create' }
    
    def get_form_kwargs(self, prefix):
        kwargs = super(ClientProfileEditReferralView, self).get_form_kwargs(prefix)
        
        referral = self.get_object().get_referral()
        
        kwargs.update({
            'instance': referral
        })
        return kwargs  

class ClientProfileEditOrderView(MultipleModalMixin, ClientOrderHeadlineMixin, ClientProfileEditMainView):
    template_name = "clients/client_profile_order_edit.html"
    form_classes = {
                    "order" : OrderForm
                    }
    tab = "order"
    success_url = 'client_profile_order'
    target_modals = { 'stop_order_url' : 'stop_order' }
    
    def get_context_data(self, **kwargs):
        context = super(ClientProfileEditOrderView, self).get_context_data(**kwargs)

        self.object = self.get_object()
        context['order']=Order.objects.get_latest_order_for_client(self.object)
        context['meal_service_days'] = ServiceDay.objects.get_days_for_meal_defaults()
        return context
    
    
    def get_form_kwargs(self, prefix):
        kwargs = super(ClientProfileEditOrderView, self).get_form_kwargs(prefix)
        
        order = Order.objects.get_latest_order_for_client(self.get_object())
        
        kwargs.update({
            'instance': order
        })
        return kwargs
        

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
     
    
