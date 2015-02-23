#-*- coding: utf-8 -*-
import datetime
import logging
import sys

from django.shortcuts import render
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured
from django.forms.models import formset_factory
from django.http import HttpResponseRedirect, JsonResponse
from django.utils.translation import ugettext as _
from django.views.generic import CreateView, UpdateView, DetailView, ListView, TemplateView, FormView


from braces.views import LoginRequiredMixin
from datatableview.views import DatatableView
from datatableview.helpers import link_to_model
    
from auditlog.models import LogEntry
#from cbvtoolkit.views import MultiFormView

from .forms import AddressForm, ContactForm, ContactInfoForm, OrganizationForm, OrganizationMemberForm, OrganizationMemberFormSet, AddressFormSet, AddressFormSetHelper, WorkPhoneFormSet, PhoneFormSetHelper

# Import the customized User model
from .models import ContactEntity, SocialWorker, Address, Phone, Contact, Organization
from clients.models import RelationType

from core.views import MultipleModalMixin, ActionMixin, AjaxTemplateMixin

logger = logging.getLogger(__name__)



# Create your views here.

class ContactActionMixin(object):
    @property
    def action(self):
        msg = "{0} is missing action.".format(self.__class__)
        raise NotImplementedError(msg)
    
    def form_valid(self, form):
        if self.action == 'create':
            msg = _('Contact ajouté.')
        else:
            msg = _('Contact mis à jour.')
            
        messages.info(self.request, msg)
        return super(ContactActionMixin, self).form_valid(form)
    
    def form_action(self):
        if self.action == 'create':
            return reverse_lazy('contact_create')
        else:
            return reverse_lazy('contact_update', args=[str(self.object.id)])
        
    def form_title(self, form):
        if self.action == 'create':
            return _('Contact registration.')
        else:
            return _('Contact update.') 

class ContactListView(LoginRequiredMixin, DatatableView):    
    model = Contact
    
    datatable_options = {
                         #'structure_template': "datatableview/bootstrap_structure.html",
        'columns': [
            ('Name', ['first_name', 'last_name'], link_to_model),
            ],
    }
    
    implementation = u""

class ContactInfoMixin(ActionMixin):
    entity_type = ""
    initial = {
               'form': {},
               'contact_info': {},
               'address': {},
               'phones': {}
               }
    
    def get_form_action_url(self):
        
        if self.form_action_url:
            return self.form_action_url
        
        if self.action == "create":
            self.form_action_url = self.entity_type+"_create" 
        else:
            self.form_action_url = self.entity_type+"_update"
    
        return self.form_action_url
    
    
    
    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates blank versions of the form
        and its inline formsets.
        """
        print >>sys.stderr, '*** ENTERING GET ****' 
        
        forms = self.init_forms()
        
        return self.render_to_response(self.get_context_data(**forms))
   
    def post(self, request, *args, **kwargs):
        print >>sys.stderr, '***ContactInfoMixin  ENTERING POST ****' 
        
        forms = self.init_forms()
        
        forms_valid = self.validate_forms(forms)
        if forms_valid:
            print >>sys.stderr, '***ContactInfoMixin  valid forms ****' 
        
            self.form_valid(forms)
            if self.request.is_ajax():
                print >>sys.stderr, '***ContactInfoMixin  Ajax request ****' 
        
                data = {
                    'pk': self.object.pk,
                    'name' : self.object.get_display_name()
                }
                return JsonResponse(data)
            else:
                return HttpResponseRedirect(self.get_success_url())
        else:
            print >>sys.stderr, '***ContactInfoMixin  INVALID forms ****' 
        
            return self.form_invalid(forms)
        
        
    
    def get_prefix(self, prefix):
        return self.entity_type + "_" + prefix
    
    def get_initial(self, prefix):
        return self.initial[prefix].copy()
    
    def get_form_instance(self, prefix):
        if not self.object:
            return None
        
        if prefix == "form":
            return self.object
        elif prefix == "contact_info" or prefix == "phones":
            return self.object.get_contact_info()
        elif prefix == "address":
            return self.object.get_contact_info().get_address()
        
            
        
    def get_form_kwargs(self, prefix):
        """
        Returns the keyword arguments for instantiating the form.
        """
        kwargs = {
            'initial': self.get_initial(prefix),
            'prefix': self.get_prefix(prefix),
        }
        if self.request.method in ('POST', 'PUT'):
            kwargs.update({
                'data': self.request.POST,
                'files': self.request.FILES,
            })
        if hasattr(self, 'object'):
            kwargs.update({'instance': self.get_form_instance(prefix)})
        
        return kwargs

    def get_form(self, form_class, prefix):
        return form_class(**self.get_form_kwargs(prefix))
    
    def init_forms(self):
        forms = {}
        post_request = self.request.method in ('POST', 'PUT')
        form_class = self.get_form_class()
        form = self.get_form(form_class, "form")
        forms['form'] = form
        
        contact_form = self.get_form(ContactInfoForm, 'contact_info')
        forms['contact_form'] = contact_form    
        
        address_form = self.get_form(AddressForm, 'address')
        forms['address_form'] = address_form
        
        phones_form = self.get_form(WorkPhoneFormSet, 'phones')
        forms['phones_form'] = phones_form
        
        return forms
    
    def validate_forms(self, forms):
        form = forms['form']
        contact_form = forms['contact_form']
        address_form = forms['address_form']
        phones_form = forms['phones_form']
        
        print >>sys.stderr, '*** form data *** %s' % form.data
        forms_valid = form.is_valid() and \
            contact_form.is_valid() and \
            address_form.is_valid() and \
            phones_form.is_valid()
                    
        return forms_valid
    
    def form_invalid(self, forms):
        
        for form_prefix in forms.keys():
            form = forms[form_prefix]
            print >>sys.stderr, '*** %s form errors *** %s' % (form_prefix, form.errors)
        
            #messages.error(self.request, form.errors())
            
        return self.render_to_response(
            self.get_context_data(**forms))
   
class ContactEntityCreateView(LoginRequiredMixin, ContactInfoMixin, AjaxTemplateMixin, CreateView):
    model = ContactEntity
    
    action = "create"
    
#     def get_form_class(self):
#         if self.entity_type == "org":
#             self.form_class = OrganizationForm 
#         elif self.entity_type == "contact":
#             self.form_class = ContactForm
#             
#         return self.form_class
    
    
    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates blank versions of the form
        and its inline formsets.
        """
        print >>sys.stderr, '*** ENTERING GET ****' 
        
        self.object = None
        
        return super(ContactEntityCreateView, self).get(request, *args, **kwargs)
            
    # overrides ProcessFormView.post
    def post(self, request, *args, **kwargs):
        self.object = None
        
        return super(ContactEntityCreateView, self).post(request, *args, **kwargs)
    
    
    def form_valid(self, forms):
        form = forms['form']
        contact_form = forms['contact_form']
        address_form = forms['address_form']
        phones_form = forms['phones_form']
        
        self.object = form.save(commit=False)
        self.object.save()
        contact_info = contact_form.save(commit=False)
        
        contact_type = ContentType.objects.get_for_model(self.object)
        contact_info.content_type = contact_type
        contact_info.content_object = self.object
        contact_info.save()
        
        if (address_form.is_valid()):
            address = address_form.save(commit=False)
            address.contact_info = contact_info
            address.save()
               
        phones_form.instance = contact_info
        phones_form.save()
        
        
                
class ContactEntityUpdateView(LoginRequiredMixin, ContactInfoMixin, AjaxTemplateMixin, UpdateView):
    model = ContactEntity
    
    action = "update"

    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates blank versions of the form
        and its inline formsets.
        """
        print >>sys.stderr, '*** ENTERING GET ****' 
        
        self.object = self.get_object()
        
        return super(ContactEntityUpdateView, self).get(request, *args, **kwargs)
            
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        return super(ContactEntityUpdateView, self).post(request, *args, **kwargs)
    
    def form_valid(self, forms):
        form = forms['form']
        contact_form = forms['contact_form']
        address_form = forms['address_form']
        phones_form = forms['phones_form']
        
        self.object = form.save(commit=False)
        self.object.save()
        contact_info = contact_form.save(commit=False)
        
        contact_type = ContentType.objects.get_for_model(self.object)
        contact_info.content_type = contact_type
        contact_info.content_object = self.object
        contact_info.save()
        
        if address_form.is_valid():
            address = address_form.save(commit=False)
            address.contact_info = contact_info
            address.save()
               
        phones_form.instance = contact_info
        phones_form.save()

class ContactMixin(object):
    def get_initial(self, prefix):
        if prefix == "org":
            return {}
        else:
            return super(ContactMixin, self).get_initial(prefix)

    def init_forms(self):
        forms = super(ContactMixin, self).init_forms()
        
        org_form = self.get_form(OrganizationMemberFormSet, "org")
        forms['org_form'] = org_form
        
        return forms
    
    def validate_forms(self, forms):
       #forms_valid = super(ContactMixin, self).validate_forms(forms)
        
        form = forms['form']
        contact_form = forms['contact_form']
        address_form = forms['address_form']
        phones_form = forms['phones_form']
        org_form = forms['org_form']
        
        forms_valid = form.is_valid() 
        
        contact_type = form.cleaned_data['contact_type']
        if (contact_type == Contact.SOCIAL_WORKER):
            forms_valid = forms_valid and org_form.is_valid()
        else:
            forms_valid = forms_valid and address_form.is_valid()
        
        if (address_form.has_changed()):
            print >>sys.stderr, '*** address_form has changed ***' 
        
        else:
            print >>sys.stderr, '*** address_form has not changed ***' 
        
        if (org_form.has_changed()):
            print >>sys.stderr, '*** social_worker_form has changed ***!' 
        
        else:
            print >>sys.stderr, '*** social_worker_form has not changed ***!' 
        
            
        if (phones_form.has_changed()):
            forms_valid = forms_valid and phones_form.is_valid() 
            
            
        forms_valid = forms_valid and contact_form.is_valid()
        
        return forms_valid
    
    
    def form_valid(self, forms):
        super(ContactMixin, self).form_valid(forms)
        
        if isinstance(self.object, SocialWorker):
            org_form = forms['org_form']
        
            org = org_form.save(commit=False)
            org.social_worker = self.object
            org.save()
            
    
class ContactCreateView(MultipleModalMixin, ContactMixin, ContactEntityCreateView):
    model = Contact
    entity_type = "contact"
    template_name = "contacts/contact_form.html"
    ajax_template_name = "contacts/contact_form_inner.html" 
    form_class = ContactForm
    target_modals = { 'org_create_url' : 'org_create' }
    

class ContactUpdateView(MultipleModalMixin, ContactMixin, ContactEntityUpdateView):
    model = Contact
    entity_type = "contact"
    template_name = "contacts/contact_form.html"
    ajax_template_name = "contacts/contact_form_inner.html" 
    form_class = ContactForm
    target_modals = { 'org_create_url' : 'org_create' }
    
class OrganizationCreateView(ContactEntityCreateView):
    model = Organization
    entity_type = "org"
    template_name = 'contacts/organization_form.html'
    ajax_template_name = 'contacts/organization_form_inner.html'
    form_class = OrganizationForm

class OrganizationUpdateView(ContactEntityCreateView):
    model = Organization
    entity_type = "org"
    template_name = 'contacts/organization_form.html'
    ajax_template_name = 'contacts/organization_form_inner.html'
    form_class = OrganizationForm
    
class ContactCreateViewOld(LoginRequiredMixin, ActionMixin, CreateView):
    model = Contact
    action = "create" # required for ContactActionMixin 
    form_action_url = "contact_create"  # required for ContactActionMixin 
    form_class = ContactForm
     
    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates blank versions of the form
        and its inline formsets.
        """
        print >>sys.stderr, '*** ENTERING GET ****' 
        
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
    
        form.initial = { 'contact_type' : 'N'}
        
        contact_form = ContactInfoForm(prefix="contact_info")
        org_form = OrganizationMemberFormSet(prefix="sw")
        address_form = AddressForm(prefix="address")
        phone_form = WorkPhoneFormSet(prefix="phones")
        
        return self.render_to_response(
            self.get_context_data(form=form,
                                  contact_form =contact_form,
                                  org_form = org_form,
                                  address_form=address_form,
                                  phone_form=phone_form,
                                  ))

    # overrides ProcessFormView.post
    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        contact_form = ContactInfoForm(request.POST, prefix="contact_info")
        org_form = OrganizationMemberFormSet(request.POST, prefix="sw")
        address_form = AddressForm(request.POST, prefix="address")
        phone_form = WorkPhoneFormSet(request.POST, prefix="phones")
        
        print >>sys.stderr, '*** form data *** %s' % form.data
        forms_valid = form.is_valid() and contact_form.is_valid()
        
        contact_type = form.cleaned_data['contact_type']
        if (contact_type == Contact.SOCIAL_WORKER):
            forms_valid = forms_valid and org_form.is_valid()
        else:
            forms_valid = forms_valid and address_form.is_valid()
        
        if (address_form.has_changed()):
            print >>sys.stderr, '*** address_form has changed ***' 
        
        else:
            print >>sys.stderr, '*** address_form has not changed ***' 
        
        if (org_form.has_changed()):
            print >>sys.stderr, '*** social_worker_form has changed ***!' 
        
        else:
            print >>sys.stderr, '*** social_worker_form has not changed ***!' 
        
            
        if (phone_form.has_changed()):
            forms_valid = forms_valid and phone_form.is_valid() 
            
        if forms_valid:
            return self.form_valid(form, 
                                   contact_form,
                                   org_form,
                                   address_form, 
                                   phone_form)
        else:
            print >>sys.stderr, '*** invalid form data *** %s' % form.data
            return self.form_invalid(form, 
                                     contact_form,
                                     org_form, 
                                     address_form, 
                                     phone_form)
    

    def form_valid(self, form, contact_form, org_form, address_form, phone_form):
           
        self.object = form.save(commit=False)
        self.object.save()
        contact_info = contact_form.save(commit=False)
        
        contact_type = ContentType.objects.get_for_model(self.object)
        contact_info.content_type = contact_type
        contact_info.content_object = self.object
        contact_info.save()
        
        address = address_form.save(commit=False)
        address.contact_info = contact_info
        address.save()
               
        phone_form.instance = contact_info
        phone_form.save()
        
        if (contact_type == Contact.SOCIAL_WORKER):
            org = org_form.save(commit=False)
            org.social_worker = self.object
            org.save()

        return HttpResponseRedirect(self.get_success_url())
    
    def form_invalid(self, form, contact_form, org_form, address_form, phone_form):
        
        return self.render_to_response(
            self.get_context_data(form = form,
                                  contact_form =contact_form,
                                  org_form = org_form,
                                  address_form = address_form,
                                  phone_form=phone_form,
                                  )) 
    
class ContactUpdateViewOld(LoginRequiredMixin, ContactActionMixin, UpdateView):
    model = Contact
    action = "update" # used for ContactActionMixin functionality
    form_action_url = "contact_update"  # required for ContactActionMixin 
    form_class = ContactForm
        
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        form.use_for_update()
        
        contact_info = self.object.get_contact_info()
        contact_form = ContactInfoForm(prefix="contact_info", instance=contact_info)
        
        org_form = OrganizationMemberFormSet(prefix="sw", instance=self.object.get_organization())
        
        address_form = AddressForm(prefix="address", instance=contact_info.get_address())
        phone_form = WorkPhoneFormSet(prefix="phones", instance=contact_info)
         
        return self.render_to_response(
            self.get_context_data(form=form,
                                  contact_form=contact_form,
                                  org_form=org_form,
                                  address_form=address_form,
                                  phone_form=phone_form))
 
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        form.use_for_update()
        
        org_form = OrganizationMemberFormSet(request.POST, prefix="sw", instance=self.object.get_organization())
        
        contact_info = self.object.get_contact_info()
        contact_form = ContactInfoForm(request.POST, prefix="contact_info", instance=contact_info)
        address_form = AddressForm(request.POST, prefix="address", instance=contact_info.get_address())
        phone_form = WorkPhoneFormSet(request.POST, prefix="phones", instance=contact_info)
        
        print >>sys.stderr, '*** form data *** %s' % form.data
        
        forms_valid = form.is_valid() and contact_form.is_valid()
        
        contact_type = form.cleaned_data['contact_type']
        print >>sys.stderr, '*** (after form_cleaned_data) object contact type %s *** ' % self.object.contact_type
        
        print >>sys.stderr, '*** new contact type %s old contact type %s ***' % (contact_type, self.object.contact_type)
        if (contact_type == Contact.SOCIAL_WORKER):
            forms_valid = forms_valid and org_form.is_valid()
            if (org_form.has_changed()):
                print >>sys.stderr, '*** org_form has changed ***!'
            else:
                print >>sys.stderr, '*** org_form has NOT changed ***!'
        else:
            forms_valid = forms_valid and address_form.is_valid()
            if (address_form.has_changed()):
                print >>sys.stderr, '*** address_form has changed ***' 
            else:
                print >>sys.stderr, '*** address_form has NOT changed ***' 
        
        forms_valid = forms_valid and phone_form.is_valid() 
            
        if (phone_form.has_changed()):
            print >>sys.stderr, '*** phone_form has changed ***!' 
            
        else:
            print >>sys.stderr, '*** phone_form has NOT changed ***!' 
            
        if forms_valid:
            return self.form_valid(form, 
                                   contact_form,
                                   org_form,
                                   address_form, 
                                   phone_form)
        else:
            print >>sys.stderr, '*** INVALID form data !! *** %s' % form.data
            return self.form_invalid(form, 
                                     contact_form,
                                     org_form, 
                                     address_form, 
                                     phone_form)
            
 
    def form_valid(self, form, contact_form, org_form, address_form, phone_form):
        
        self.object = form.save(commit=False)
        self.object.save()
        
        contact_info = contact_form.save(commit=False)
        contact_info.save()
        
        #if phone_form.has_changed():
        print >>sys.stderr, '*** save phone_form ***' 
        phone_instances = phone_form.save(commit=False)
        for phone in phone_instances:
            print >>sys.stderr, '*** save phone_instance ***'
            phone.save()
        
        for old_phone in phone_form.deleted_objects:
            print >>sys.stderr, '*** delete phone ****'
            old_phone.delete()
            
        if address_form.has_changed():
            print >>sys.stderr, '*** save address_form ***' 
            address = address_form.save(commit=False)
            address.save()
        
        if org_form.has_changed():
            print >>sys.stderr, '*** save org_form ***' 
            org_instances = org_form.save(commit=False)
            for org in org_instances:
                org.save()
            
            for old_org in org_form.deleted_objects:
                old_org.deactivate()
                old_org.save()
         
        return HttpResponseRedirect(self.get_success_url())
     
    def form_invalid(self, form, contact_form, org_form, address_form, phone_form):
             
        return self.render_to_response(
            self.get_context_data(form = form,
                                  contact_form =contact_form,
                                  org_form = org_form,
                                  address_form = address_form,
                                  phone_form=phone_form))

class OrganizationListView(LoginRequiredMixin, DatatableView):    
    model = Organization
    
    datatable_options = {
                         #'structure_template': "datatableview/bootstrap_structure.html",
        'columns': [
            ('Name', 'name', link_to_model),
            ],
    }
    
    implementation = u""


class TestCreateView(LoginRequiredMixin, ContactActionMixin, CreateView):
    model = Contact
    action = "create" # used for ContactActionMixin functionality
    form_class = ContactForm
    template_name = "contacts/test_form.html"
    
class OrganizationOldCreateView(LoginRequiredMixin, ActionMixin, AjaxTemplateMixin, CreateView):
    model = Organization
    action = "create"
    form_action_url = "org_create"
    item_name = "Organization"
    
    form_class = OrganizationForm
    template_name = 'contacts/organization_form.html'
    ajax_template_name = 'contacts/organization_form_inner.html'
    
    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates blank versions of the form
        and its inline formsets.
        """
        print >>sys.stderr, '*** ENTERING GET ****' 
        
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        
        contact_form = ContactInfoForm(prefix="org_contact_info")
        address_form = AddressForm(prefix="org_address")
        phone_form = WorkPhoneFormSet(prefix="org_phones")
        
        return self.render_to_response(
            self.get_context_data(org_form=form,
                                  org_contact_form = contact_form,
                                  org_address_form=address_form,
                                  org_phone_form=phone_form))

    # overrides ProcessFormView.post
    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        
        contact_form = ContactInfoForm(request.POST, prefix="org_contact_info")
        address_form = AddressForm(request.POST, prefix="org_address")
        phone_form = WorkPhoneFormSet(request.POST, prefix="org_phones")
        
        print >>sys.stderr, '*** form data *** %s' % form.data
        forms_valid = form.is_valid() and contact_form.is_valid()
        
        forms_valid = forms_valid and address_form.is_valid()
        
        if (address_form.has_changed()):
            print >>sys.stderr, '*** address_form has changed ***' 
        
        else:
            print >>sys.stderr, '*** address_form has not changed ***' 
        
        forms_valid = forms_valid and phone_form.is_valid() 
            
        if forms_valid:
            return self.form_valid(form, 
                                   contact_form,
                                   address_form, 
                                   phone_form)
        else:
            print >>sys.stderr, '*** invalid form data *** %s' % form.data
            return self.form_invalid(form, 
                                     contact_form,
                                     address_form, 
                                     phone_form)
    

    def form_valid(self, form, contact_form, address_form, phone_form):
           
        self.object = form.save(commit=False)
        self.object.save()
        contact_info = contact_form.save(commit=False)
        
        organization_type = ContentType.objects.get_for_model(self.object)
        contact_info.content_type = organization_type
        contact_info.content_object = self.object
        contact_info.save()
        
        address = address_form.save(commit=False)
        address.contact_info = contact_info
        address.save()
               
        phone_form.instance = contact_info
        phone_form.save()

        if self.request.is_ajax():
            data = {
                'pk': self.object.pk,
                'name' : self.object.name
            }
            return JsonResponse(data)
        else:
            return HttpResponseRedirect(self.get_success_url())
    
    def form_invalid(self, form, contact_form, address_form, phone_form):
        
        return self.render_to_response(
            self.get_context_data(org_form = form,
                                  org_contact_form =contact_form,
                                  org_address_form = address_form,
                                  org_phone_form=phone_form)) 
    
class OrganizationUpdateViewOld(LoginRequiredMixin, ActionMixin, UpdateView):
    model = Organization
    form_class = OrganizationForm
    action = "update"
    form_action_url = "org_update"
    item_name = "Organization"
    
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        form.use_for_update()
        
        contact_info = self.object.get_contact_info()
        contact_form = ContactInfoForm(prefix="contact_info", instance=contact_info)
        
        address_form = AddressForm(prefix="address", instance=contact_info.get_address())
        phone_form = WorkPhoneFormSet(prefix="phones", instance=contact_info)
         
        return self.render_to_response(
            self.get_context_data(org_form=form,
                                  org_contact_form=contact_form,
                                  org_address_form=address_form,
                                  org_phone_form=phone_form))
 
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        form.use_for_update()
        
        contact_info = self.object.get_contact_info()
        contact_form = ContactInfoForm(request.POST, prefix="contact_info", instance=contact_info)
        address_form = AddressForm(request.POST, prefix="address", instance=contact_info.get_address())
        phone_form = WorkPhoneFormSet(request.POST, prefix="phones", instance=contact_info)
        
        print >>sys.stderr, '*** form data *** %s' % form.data
        
        forms_valid = form.is_valid() and contact_form.is_valid()
        
        forms_valid = forms_valid and address_form.is_valid()
        if (address_form.has_changed()):
            print >>sys.stderr, '*** address_form has changed ***' 
        else:
            print >>sys.stderr, '*** address_form has NOT changed ***' 
    
        forms_valid = forms_valid and phone_form.is_valid() 
            
        if (phone_form.has_changed()):
            print >>sys.stderr, '*** phone_form has changed ***!' 
            
        else:
            print >>sys.stderr, '*** phone_form has NOT changed ***!' 
            
        if forms_valid:
            return self.form_valid(form, 
                                   contact_form,
                                   address_form, 
                                   phone_form)
        else:
            print >>sys.stderr, '*** INVALID form data !! *** %s' % form.data
            return self.form_invalid(form, 
                                     contact_form,
                                     address_form, 
                                     phone_form)
            
 
    def form_valid(self, form, contact_form, address_form, phone_form):
        
        self.object = form.save(commit=False)
        self.object.save()
        
        contact_info = contact_form.save(commit=False)
        contact_info.save()
        
        #if phone_form.has_changed():
        print >>sys.stderr, '*** save phone_form ***' 
        phone_instances = phone_form.save(commit=False)
        for phone in phone_instances:
            print >>sys.stderr, '*** save phone_instance ***'
            phone.save()
        
        for old_phone in phone_form.deleted_objects:
            print >>sys.stderr, '*** delete phone ****'
            old_phone.delete()
            
        if address_form.has_changed():
            print >>sys.stderr, '*** save address_form ***' 
            address = address_form.save(commit=False)
            address.save()
        
         
        return HttpResponseRedirect(self.get_success_url())
     
    def form_invalid(self, form, contact_form, address_form, phone_form):
             
        return self.render_to_response(
            self.get_context_data(org_form = form,
                                  org_contact_form =contact_form,
                                  org_address_form = address_form,
                                  org_phone_form=phone_form))

