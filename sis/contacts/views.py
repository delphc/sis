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
from django.http import HttpResponseRedirect, JsonResponse
from django.utils.translation import ugettext as _
from django.views.generic import CreateView, UpdateView, DetailView, ListView, TemplateView, FormView


from braces.views import LoginRequiredMixin
from datatableview.views import DatatableView
from datatableview.helpers import link_to_model
from auditlog.models import LogEntry
#from cbvtoolkit.views import MultiFormView

from .forms import ContactForm, ContactInfoForm, OrganizationForm, OrganizationMemberForm, AddressFormSet, AddressFormSetHelper, PhoneFormSet, PhoneFormSetHelper

# Import the customized User model
from .models import Address, Phone, Contact, Organization
from clients.models import RelationType

logger = logging.getLogger(__name__)

class AjaxTemplateMixin(object):
    def dispatch(self, request, *args, **kwargs):
        if not hasattr(self, 'ajax_template_name'):
            split = self.template_name.split('.html')
            split[-1] = '_inner'
            split.append('.html')
            self.ajax_template_name = ''.join(split)
        if request.is_ajax():
            self.template_name = self.ajax_template_name
        return super(AjaxTemplateMixin, self).dispatch(request, *args, **kwargs)


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
            return reverse('contact_create')
        else:
            return reverse('contact_update', args=[str(self.object.id)])
        
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

class ContactCreateView(LoginRequiredMixin, ContactActionMixin, CreateView):
    model = Contact
    action = "create" # used for ContactActionMixin functionality
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
        org_form = OrganizationMemberForm(prefix="sw")
        address_form = AddressFormSet(prefix="address")
        address_form_helper = AddressFormSetHelper()
        phone_form = PhoneFormSet(prefix="phones")
        # TODO: initial does not work - commented out for now
#                                 ,initial=[
#                                   {'phones-0-type': 'H',
#                                    'phones-1-type': 'C',
#                                    'phones-0-number': 'kjfbskb'}
#                                   ])
        phone_form_helper = PhoneFormSetHelper()
        
        return self.render_to_response(
            self.get_context_data(form=form,
                                  contact_form =contact_form,
                                  org_form = org_form,
                                  address_form=address_form,
                                  address_form_helper=address_form_helper,
                                  phone_form=phone_form,
                                  phone_form_helper=phone_form_helper))

    # overrides ProcessFormView.post
    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        contact_form = ContactInfoForm(request.POST, prefix="contact_info")
        org_form = OrganizationMemberForm(request.POST, prefix="sw")
        address_form = AddressFormSet(request.POST, prefix="address")
        phone_form = PhoneFormSet(request.POST, prefix="phones")
        
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
        
        address_form.instance = contact_info
        address_form.save()
               
        phone_form.instance = contact_info
        phone_form.save()
        
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
                                  address_form_helper=AddressFormSetHelper(),
                                  phone_form=phone_form,
                                  phone_form_helper=PhoneFormSetHelper)) 
    
class ContactUpdateView(LoginRequiredMixin, ContactActionMixin, UpdateView):
    model = Contact
    action = "update" # used for ContactActionMixin functionality
    form_class = ContactForm
        
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        form.use_for_update()
        
        contact_info = self.object.get_contact_info()
        contact_form = ContactInfoForm(prefix="contact_info", instance=contact_info)
        
        org_form = OrganizationMemberForm(prefix="sw", instance=self.object.get_organization())
        
        address_form = AddressFormSet(prefix="address", instance=contact_info)
        address_form_helper = AddressFormSetHelper()
        phone_form = PhoneFormSet(prefix="phones", instance=contact_info)
        phone_form_helper = PhoneFormSetHelper()
         
        return self.render_to_response(
            self.get_context_data(form=form,
                                  contact_form=contact_form,
                                  org_form=org_form,
                                  address_form=address_form,
                                  address_form_helper=address_form_helper,
                                  phone_form=phone_form))
 
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        form.use_for_update()
        
        org_form = OrganizationMemberForm(request.POST, prefix="sw", instance=self.object.get_organization())
        
        contact_info = self.object.get_contact_info()
        contact_form = ContactInfoForm(request.POST, prefix="contact_info", instance=contact_info)
        address_form = AddressFormSet(request.POST, prefix="address", instance=contact_info)
        phone_form = PhoneFormSet(request.POST, prefix="phones", instance=contact_info)
        
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
            address_instances = address_form.save(commit=False)
            for address in address_instances:
                address.save()
        
        if org_form.has_changed():
            print >>sys.stderr, '*** save org_form ***' 
            org = org_form.save(commit=False)
            org.save()
        
         
        return HttpResponseRedirect(self.get_success_url())
     
    def form_invalid(self, form, contact_form, org_form, address_form, phone_form):
             
        return self.render_to_response(
            self.get_context_data(form = form,
                                  contact_form =contact_form,
                                  org_form = org_form,
                                  address_form = address_form,
                                  address_form_helper=AddressFormSetHelper(),
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
    
class OrganizationCreateView(LoginRequiredMixin, AjaxTemplateMixin, CreateView):
    model = Organization
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
        address_form = AddressFormSet(prefix="org_address")
        phone_form = PhoneFormSet(prefix="org_phones")
        
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
        address_form = AddressFormSet(request.POST, prefix="org_address")
        phone_form = PhoneFormSet(request.POST, prefix="org_phones")
        
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
        
        address_form.instance = contact_info
        address_form.save()
               
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
    
class OrganizationUpdateView(LoginRequiredMixin, UpdateView):
    model = Organization
    form_class = OrganizationForm
        
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        form.use_for_update()
        
        contact_info = self.object.get_contact_info()
        contact_form = ContactInfoForm(prefix="contact_info", instance=contact_info)
        
        address_form = AddressFormSet(prefix="address", instance=contact_info)
        address_form_helper = AddressFormSetHelper()
        phone_form = PhoneFormSet(prefix="phones", instance=contact_info)
        phone_form_helper = PhoneFormSetHelper()
         
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
        address_form = AddressFormSet(request.POST, prefix="address", instance=contact_info)
        phone_form = PhoneFormSet(request.POST, prefix="phones", instance=contact_info)
        
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
            address_instances = address_form.save(commit=False)
            for address in address_instances:
                address.save()
        
         
        return HttpResponseRedirect(self.get_success_url())
     
    def form_invalid(self, form, contact_form, address_form, phone_form):
             
        return self.render_to_response(
            self.get_context_data(org_form = form,
                                  org_contact_form =contact_form,
                                  org_address_form = address_form,
                                  org_phone_form=phone_form))

