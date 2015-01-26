from django import forms

from django.core.urlresolvers import reverse_lazy
from django.forms.formsets import formset_factory
from django.forms.models import inlineformset_factory
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

class ContactInfoForm(forms.ModelForm):
    class Meta:
        model = ContactInfo
        fields = ['email_address']
        localized_fields = ('__all__')
        
    
class OrganizationMemberForm(forms.ModelForm):
    class Meta:
        model = OrganizationMember
        fields = ['organization', 'start_date', 'end_date', 'position']
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
        self.helper.layout = Layout(  
            Div(
                Field('organization', wrapper_class="col-xs-5"),
                HTML('<div style="margin-top:20px"><a id="new-org-button" href="#" class="btn btn-primary" data-target="#largeModal" data-toggle="modal" ><i class="fa fa-plus"></i>'+_(" Add New Organization ")+'</a></div>'),
                #HTML('<button id="new-org-button" class="btn btn-primary col-xs-2"><i class="fa fa-plus"></i>'+_(" Add Organization ")+'</button>'),
                css_class="row"
                ),                                    
            Div(
                Field('position', wrapper_class="col-xs-6", placeholder=_("Ex: nurse, nutritionist, ...")),
                Field('start_date', wrapper_class="col-xs-3"),
                Field('end_date', wrapper_class="col-xs-3"),
                css_class="row"
                )
            )
                
        
    def disable_fields(self):
        self.helper.filter(basestring, greedy=True).update_attributes(disabled=True)
    
#     def clean(self):
#         cleaned_data = super(ContactCreateForm, self).clean()
#         organization = cleaned_data['organization']
#         
#         if ((category == ContactType.NEXT_OF_KIN and not nok_type) or
#             (category == ContactType.CASE_WORKER and not cw_type)):
#             
#             raise forms.ValidationError(_("Type is a required field."))
#         
#         if (category == ContactType.CASE_WORKER and not organization ):
#             raise forms.ValidationError(_('Organization is a required field for contacts of this type.'))

    

    
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
        
AddressFormSet = inlineformset_factory(ContactInfo, Address, 
                                       extra=1, min_num=1, max_num=1, validate_min=True, validate_max=True,
                                       fields=('street', 'apt', 'entry_code', 'city', 'prov', 'zip_code', 'info'))

class PhoneFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(PhoneFormSetHelper, self).__init__(*args, **kwargs)
        self.form_method = 'post'
        self.form_tag = False
        self.disable_csrf = True
        self.form_class = 'form-inline'
        self.field_template = 'bootstrap3/layout/inline_field.html'
        self.disable_csrf = True
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
        
PhoneFormSet = inlineformset_factory(ContactInfo, Phone, can_delete=True,
                                     extra=1, min_num=1, max_num=3, validate_min=True, validate_max=True,
                                     fields=( 'type', 'number', 'extension', 'info'))

