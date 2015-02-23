import sys
from django import forms

from django.core.urlresolvers import reverse_lazy
from django.forms.formsets import formset_factory
from django.forms.models import inlineformset_factory, BaseInlineFormSet
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, Fieldset, ButtonHolder, Div, HTML, Hidden
from crispy_forms.bootstrap import (
    FormActions, TabHolder, Tab, InlineRadios, InlineField, UneditableField)

from crispy_forms.layout import LayoutObject, TEMPLATE_PACK
from crispy_forms.utils import flatatt
from multiform import MultiForm

from models import SocialWorker, NextOfKin, Contact, ContactInfo, Address, Phone, OrganizationMember, Organization
from core.forms import FormContainer, CoreModelForm, CoreBaseInlineFormSet

class OrganizationForm(forms.ModelForm):
    class Meta:
        model = Organization
        fields = ['name' ]
        localized_fields = ('__all__')
    
    def __init__(self, *args, **kwargs):
        super(OrganizationForm, self).__init__(*args, **kwargs)
    
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.form_method = 'POST'
        self.helper.form_id = 'id-orgCreateForm'
        self.helper.form_title = 'New Organization'
        #self.helper.form_action = 'org_create'
        
        self.helper.layout = Layout(
            Div(
                Field('name', wrapper_class="col-xs-6"),
                css_class="row"
                )
            )
         
    def use_for_update(self):
        
        self.helper.form_title = 'Organization Update'
        #self.helper.form_action = 'org_update'
 
class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['first_name', 'last_name', 'contact_type']
        localized_fields = ('__all__')
    
    def __init__(self, *args, **kwargs):
        super(ContactForm, self).__init__(*args, **kwargs)
    
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.form_method = 'POST'
        self.helper.form_id = 'id-contactCreateForm'
        self.helper.form_title = 'New contact'
        #self.helper.form_action = 'contact_create'
        
        self.helper.layout = Layout(
            Div(
                Field('contact_type', wrapper_class="col-xs-4"),
                css_class="row"
                ),
            Div(
                Field('first_name', wrapper_class="col-xs-3"),
                Field('last_name', wrapper_class="col-xs-3"),
                
                css_class="row"
                )
            )
    def use_for_update(self):
        
        self.helper.form_title = 'Contact Update'
        self.helper.form_action = 'contact_update'

class ContactInfoCreateFormHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(ContactInfoCreateFormHelper, self).__init__(*args, **kwargs)
        
        self.form_tag = False
        self.disable_csrf = True
        self.form_method = 'POST'
        self.form_title = 'Contact'
        self.layout = Layout(  
                Div(
                    Field('email_address', wrapper_class="col-xs-6"),
                    css_class="row"
                    )
                )
class ContactInfoEditFormHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(ContactInfoEditFormHelper, self).__init__(*args, **kwargs)
        
        self.form_tag = False
        self.disable_csrf = True
        self.form_method = 'post'
        self.form_class = 'form-horizontal'
        self.label_class = 'col-lg-3'
        self.field_class = 'col-lg-8'
        self.layout = Layout('email_address')

    
class ContactInfoForm(CoreModelForm):
    class Meta:
        model = ContactInfo
        fields = ['email_address']
        localized_fields = ('__all__')
        
    def __init__(self, *args, **kwargs):
        
        super(ContactInfoForm, self).__init__(*args, **kwargs)
        
        if self.edit:
            self.helper = ContactInfoEditFormHelper(form=self)
        else:
            self.helper = ContactInfoCreateFormHelper(form=self)
    
   
class OrganizationMemberForm(CoreModelForm):
    class Meta:
        model = OrganizationMember
        autocomplete_fields = ('organization')
        fields = ['organization', 'position']
        localized_fields = ('__all__')
        
#     nok_type = ContactTypeModelChoiceField(
#                     label=_('Type'),
#                     required=False,
#                     queryset=ContactType.objects.filter(category=ContactType.NEXT_OF_KIN))
#     cw_type = ContactTypeModelChoiceField( 
#                     label=_('Type'),
#                     required=False,
#                     queryset=ContactType.objects.filter(category=ContactType.CASE_WORKER))
    
    def __init__(self, *args, **kwargs):
        super(OrganizationMemberForm, self).__init__(*args, **kwargs)
    
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.form_method = 'POST'
        self.helper.form_id = 'id-orgmemberForm'
        self.helper.form_class = 'form-inline'
        self.helper.field_template = 'bootstrap3/layout/inline_field.html'
        self.helper.layout = Layout(  
            Div(
                Div(
                    Field('id', type="hidden"),
                    Field('organization', wrapper_class="col-xs-6"),
                    HTML('<div class="col-xs-6"><a id="new-org-button" href="#" class="btn btn-primary" data-target="#largeModal" data-toggle="modal" ><i class="fa fa-plus"></i>'+_(" Add New Organization ")+'</a></div>'),
                    css_class="row"
                ),
                Div(
                    Field('position', wrapper_class="col-xs-3", placeholder=_("Select value")),
                    css_class="row"
                ),
                css_class="org_row container-fluid"
            )
            )
    
        

OrganizationMemberFormSet = inlineformset_factory(Contact, OrganizationMember, form=OrganizationMemberForm,
                                       extra=1, min_num=1, max_num=1, validate_min=True, validate_max=True,
                                       can_delete=True,
                                       fields=('organization', 'position'))

class AddressCreateFormHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(AddressCreateFormHelper, self).__init__(*args, **kwargs)
        
        self.form_tag = False
        self.disable_csrf = True
        self.form_method = 'POST'
        self.form_id = 'id-addressForm'
        self.form_title = _("Address")
        self.layout = Layout(
                            Div(
                                Field('street', wrapper_class="col-xs-8"), # readonly: use 'readOnly="True"'
                                Field('apt', wrapper_class="col-xs-2"),
                                Field('entry_code', wrapper_class="col-xs-2"),      
                                css_class="row"
                                ),                                     
                                Div(
                                    Field('city', wrapper_class="col-xs-4"),
                                    Field('prov', wrapper_class="col-xs-2"),
                                    Field('zip_code', wrapper_class="col-xs-4"),      
                                    css_class="row"
                                ),
                                Div(
                                    Field('info', wrapper_class="col-xs-12", placeholder=_("Ex: corner of St Denis street")),     
                                    css_class="row"
                                )
                            )
        
class AddressEditFormHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(AddressEditFormHelper, self).__init__(*args, **kwargs)
        
        self.form_tag = False
        self.disable_csrf = True
        
        self.form_method = 'post'
        self.form_class = 'form-horizontal'
        self.label_class = 'col-lg-3'
        self.field_class = 'col-lg-9'
        self.layout = Layout(
                             'street', 'apt', 'entry_code', 'city', 'prov', 'zip_code', 'info')
 
class AddressForm(CoreModelForm):
    class Meta:
        model = Address
        fields = ['street', 'apt', 'entry_code', 'city', 'prov', 'zip_code', 'info']
        localized_fields = ('__all__')
                                            
    def __init__(self, *args, **kwargs):
        super(AddressForm, self).__init__(*args, **kwargs) 

        if self.edit:
            self.helper = AddressEditFormHelper(form=self)
        else:
            self.helper = AddressCreateFormHelper(form=self)
                                
class AddressFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(AddressFormSetHelper, self).__init__(*args, **kwargs)
        self.form_method = 'post'
        self.form_tag = False
        self.layout = Layout(
                Div(
                Field('street', wrapper_class="col-xs-8"), # readonly: use 'readOnly="True"'
                Field('apt', wrapper_class="col-xs-2"),
                Field('entry_code', wrapper_class="col-xs-2"),      
                css_class="row"
                ),                                     
                Div(
                    Field('city', wrapper_class="col-xs-4"),
                    Field('prov', wrapper_class="col-xs-2"),
                    Field('zip_code', wrapper_class="col-xs-4"),      
                    css_class="row"
                ),
                Div(
                    Field('info', wrapper_class="col-xs-12", placeholder=_("Ex: corner of St Denis street")),     
                    css_class="row"
                )
             )
        
AddressFormSet = inlineformset_factory(ContactInfo, Address, form=AddressForm,
                                       extra=1, min_num=1, max_num=1, validate_min=True, validate_max=True,
                                       can_delete=False,
                                       fields=('street', 'apt', 'entry_code', 'city', 'prov', 'zip_code', 'info'))

class PhoneForm(forms.ModelForm):
    class Meta:
        model = Phone
        fields = [ 'type', 'number', 'extension', 'info' ]
        localized_fields = ('__all__')
                                            
    def __init__(self, *args, **kwargs):
        super(PhoneForm, self).__init__(*args, **kwargs) 

        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.form_class = 'form-inline'
        self.helper.field_template = 'bootstrap3/layout/inline_field.html'
        self.helper.form_method = 'POST'
        self.helper.form_id = 'id-phoneForm'
        self.helper.form_title = _("Phone")
        self.helper.layout = Layout(
                            Div(
                                Field('id', type="hidden"),
                            #Field('DELETE', type="hidden"),
                                Field('type', wrapper_class="col-xs-2", placeholder=_("Type")),
                                Field('number',wrapper_class="col-xs-3", placeholder=_("Number (xxx-xxx-xxxx)")),  
                                Field('extension',wrapper_class="col-xs-2"),                            
                                Field('info', wrapper_class="col-xs-4", placeholder=_("Ex: extension, call PM only, ...")),
                                css_class="inline phone_row row")
                            )

class PhoneEditForm(forms.ModelForm):
    class Meta:
        model = Phone
        fields = [ 'type', 'number', 'extension', 'info' ]
        localized_fields = ('__all__')
                                            
    def __init__(self, *args, **kwargs):
        super(PhoneEditForm, self).__init__(*args, **kwargs) 

        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.form_class = 'form-inline'
        self.helper.field_template = 'bootstrap3/layout/inline_field.html'
        self.helper.form_method = 'POST'
        self.helper.form_id = 'id-phoneForm'
        self.helper.form_title = _("Phone")
        self.helper.layout = Layout(
                                Div(
                                    Div(
                                        Field('id', type="hidden"),
                                    #Field('DELETE', type="hidden"),
                                        Field('type', wrapper_class="col-xs-4", placeholder=_("Type")),
                                        Field('number',wrapper_class="col-xs-5", placeholder=_("Number (xxx-xxx-xxxx)")),  
                                        Field('extension',wrapper_class="col-xs-3"),                            
                                        css_class="inline row"),
                                    Div(
                                        Field('info', wrapper_class="col-xs-12", placeholder=_("Ex: extension, call PM only, ...")),
                                        css_class="inline row"),
                                    css_class="phone_row"
                                    )
                            )

class PhoneFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(PhoneFormSetHelper, self).__init__(*args, **kwargs)
        self.form_method = 'post'
        self.form_tag = False
        self.disable_csrf = True
        self.form_class = 'form-inline'
        self.field_template = 'bootstrap3/layout/inline_field.html'
        self.layout = Layout(
                            Div(
                            Field('id', type="hidden"),
                            #Field('DELETE', type="hidden"),
                            Field('type', wrapper_class="col-xs-2", placeholder=_("Type")),
                            Field('number',wrapper_class="col-xs-3", placeholder=_("Number (xxx-xxx-xxxx)")),  
                            Field('extension',wrapper_class="col-xs-2"),                            
                            Field('info', wrapper_class="col-xs-4", placeholder=_("Ex: extension, call PM only, ...")),
                            css_class="inline phone_row row")
                            )

class WorkPhoneInlineFormSet(CoreBaseInlineFormSet):
    def __init__(self, data=None, files=None, instance=None,
                 save_as_new=False, prefix=None, queryset=None, **kwargs):
        kwargs.update(initial=[
                       {'type': Phone.WORK,
                        }
                       ])
        super(WorkPhoneInlineFormSet, self).__init__( data, files, instance,
                 save_as_new, prefix, queryset, **kwargs)

WorkPhoneFormSet = inlineformset_factory(ContactInfo, Phone, form=PhoneEditForm, formset=WorkPhoneInlineFormSet, can_delete=True,
                                     extra=0, min_num=1, max_num=3, validate_min=True, validate_max=True,
                                     fields=( 'type', 'number', 'extension', 'info'))
  
PhoneFormSet = inlineformset_factory(ContactInfo, Phone, form=PhoneForm, can_delete=True,
                                     extra=1, min_num=1, max_num=3, validate_min=True, validate_max=True,
                                     fields=( 'type', 'number', 'extension', 'info'))

        
class HomePhoneInlineFormSet(CoreBaseInlineFormSet):
    def __init__(self, data=None, files=None, instance=None,
                 save_as_new=False, prefix=None, queryset=None, **kwargs):
        
        kwargs.update(initial=[
                       {'type': Phone.HOME,
                        }
                       ])
        super(HomePhoneInlineFormSet, self).__init__( data, files, instance,
                 save_as_new, prefix, queryset, **kwargs)
        
HomePhoneFormSet = inlineformset_factory(ContactInfo, Phone, form=PhoneEditForm, formset=HomePhoneInlineFormSet, can_delete=True,
                                     extra=0, min_num=1, max_num=3, validate_min=True, validate_max=True,
                                     fields=( 'type', 'number', 'extension', 'info'))

