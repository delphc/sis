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
from datatableview.views import DatatableView
from datatableview.helpers import link_to_model
from auditlog.models import LogEntry
from cbvtoolkit.views import MultiFormView

from .forms import ContactCreateForm, AddressFormSet, PhoneFormSet, PhoneFormSetHelper

# Import the customized User model
from .models import Address, Phone, Contact, ContactType

logger = logging.getLogger(__name__)

# Create your views here.
class ContactActionMixin(object):
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
    form_class = ContactCreateForm
       
    def get(self, request, *args, **kwargs):
        """
        Handles GET requests and instantiates blank versions of the form
        and its inline formsets.
        """
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
    
        #address_form = AddressFormSet(prefix="address")
        address_form = None
        phone_form = PhoneFormSet(prefix="phones",
         
                                initial=[
                                  {'phones-0-type': 'H',
                                   'phones-1-type': 'C',
                                   'phones-0-number': 'kjfbskb'}
                                  ])
        phone_form_helper = PhoneFormSetHelper()
        
        return self.render_to_response(
            self.get_context_data(form=form,
                                  #address_form=address_form,
                                  phone_form=phone_form,
                                  phone_form_helper=phone_form_helper))

    # overrides ProcessFormView.post
    def post(self, request, *args, **kwargs):
        self.object = None
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        address_form = None
        #address_form = AddressFormSet(request.POST, prefix="address")
        phone_form = PhoneFormSet(request.POST, prefix="phones")
        
        forms_valid = form.is_valid()
        if (address_form != None):
            forms_valid = forms_valid and address_form.is_valid() 
        if (phone_form != None):
            forms_valid = forms_valid and phone_form.is_valid() 
            
        if forms_valid:
            return self.form_valid(form, address_form, phone_form)
        else:
            return self.form_invalid(form, address_form, phone_form)
    

    def form_valid(self, form, address_form, phone_form):
        self.object = form.save(commit=False)
        category = form.cleaned_data['category']
        
        if (category == ContactType.NEXT_OF_KIN):
            self.object.type = form.cleaned_data['nok_type']
        else:
            self.object.type = form.cleaned_data['cw_type']
        self.object.save()
        
        if (address_form != None):
            address_form.instance = self.object
            address_form.save()
        
        if (phone_form != None):
            phone_form.instance = self.object
            phone_form.save()
        
        return HttpResponseRedirect(self.get_success_url())
    
    def form_invalid(self, form, address_form, phone_form):
        
        return self.render_to_response(
            self.get_context_data(form = form,
                                  address_form = address_form,
                                  phone_form = phone_form)) # add phoneformhelper ?
    
class ContactUpdateView(LoginRequiredMixin, ContactActionMixin, UpdateView):
    model = Contact
    action = "update" # used for ContactActionMixin functionality
    form_class = ContactCreateForm
    #address=AddressFormSet();
       
    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        form.use_for_update()
        #form.disable_fields()
        #form.fields['category'].initial= self.object.category
        if self.object.category == ContactType.NEXT_OF_KIN:
            print >>sys.stderr, '*** get: nok type set initial****'  
        
            form.fields['nok_type'].initial=self.object.type
        else:
            form.fields['cw_type'].initial=self.object.type
            
        #address_form = AddressFormSet(prefix="address", instance = self.object)
        address_form = None
        phone_form = PhoneFormSet(prefix="phones", instance = self.object)
        phone_form_helper = PhoneFormSetHelper()
        
        return self.render_to_response(
            self.get_context_data(form=form,
#                                  address_form=address_form,
                                  phone_form=phone_form,
                                  phone_form_helper=phone_form_helper))

    # overrides ProcessFormView.post
    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        
 #       address_form = AddressFormSet(request.POST, prefix="address", instance = self.object)
        address_form = None
        phone_form = PhoneFormSet(request.POST,  prefix="phones", instance = self.object)
        
        forms_valid = form.is_valid()
        if address_form != None:
            forms_valid = forms_valid and address_form.is_valid()
        if phone_form != None:
            forms_valid = forms_valid and phone_form.is_valid()
        if forms_valid:
            return self.form_valid(form, address_form, phone_form)
        else:
            return self.form_invalid(form, address_form, phone_form)

    def form_valid(self, form, address_form, phone_form):
        self.object = form.save(commit=False)
        print >>sys.stderr, '*** cleaned_data [%s]****' % form.cleaned_data
        
        category = form.cleaned_data['category']
        
        if (category == ContactType.NEXT_OF_KIN):
            print >>sys.stderr, '*** cleaned_data [%s]****' % form.cleaned_data['nok_type']
        
            self.object.type = form.cleaned_data['nok_type']
        else:
            self.object.type = form.cleaned_data['cw_type']
        
        self.object.save()
        
        if address_form:
            instances = address_form.save(commit=False)
            for address in instances:
                address.save()
            
        phone_instances = phone_form.save(commit = False)
        for phone in phone_instances:
            phone.save()
        
        return HttpResponseRedirect(self.get_success_url())
    
    def form_invalid(self, form, address_form, phone_form):
        phone_form_helper = PhoneFormSetHelper()
        return self.render_to_response(
            self.get_context_data(form = form,
                                  address_form = address_form,
                                  phone_form = phone_form,
                                  phone_form_helper = phone_form_helper))

    


