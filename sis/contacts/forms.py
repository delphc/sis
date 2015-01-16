from django import forms

from django.core.urlresolvers import reverse_lazy
from django.forms.formsets import formset_factory
from django.contrib.contenttypes.forms import generic_inlineformset_factory, BaseGenericInlineFormSet
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, Fieldset, ButtonHolder, Div, HTML, Hidden
from crispy_forms.bootstrap import (
    FormActions, TabHolder, Tab, InlineRadios, InlineField, UneditableField)

from crispy_forms.layout import LayoutObject, TEMPLATE_PACK
from crispy_forms.utils import flatatt

from models import Contact, ContactType, Address, Phone
        
class ContactTypeModelChoiceField(forms.ModelChoiceField):
    lang = None
    
    def label_from_instance(self, obj):
        if self.lang == "en":
            return obj.type_en 
        else:
            return obj.type_fr
        
class ContactCreateForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = ['first_name', 'last_name', 'email_address', 'category', 'organization']
        localized_fields = ('__all__')
        
    nok_type = ContactTypeModelChoiceField(
                    label=_('Type'),
                    required=False,
                    queryset=ContactType.objects.filter(category=ContactType.NEXT_OF_KIN))
    cw_type = ContactTypeModelChoiceField( 
                    label=_('Type'),
                    required=False,
                    queryset=ContactType.objects.filter(category=ContactType.CASE_WORKER))
    
    def __init__(self, *args, **kwargs):
        super(ContactCreateForm, self).__init__(*args, **kwargs)
    
        self.helper = FormHelper(self)
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        self.helper.form_method = 'POST'
        self.helper.form_id = 'id-contactCreateForm'
        self.helper.form_title = 'New contact'
        self.helper.layout = Layout(
            Div(HTML('<h4 class="page-header">{{ form_title }}'),
                css_class="row"),
           
            Div(
                Field('first_name', wrapper_class="col-xs-3"),
                Field('last_name', wrapper_class="col-xs-3"),
                
                css_class="row"
                ),                                    
            Div(
                Field('category', wrapper_class="col-xs-3"),
                Field('nok_type', wrapper_class="col-xs-3"),
                Field('cw_type', wrapper_class="col-xs-3"),
                css_class="row"
                ),  
            Div(
                Field('organization', wrapper_class="col-xs-6"),
                css_class="row"
                ),
            Div(
                Field('email_address', wrapper_class="col-xs-6"),
                css_class="row"
                )
            )
            
    def use_for_update(self):
        
        self.helper.form_action = 'contact_update'
        self.helper.form_title = 'Contact Update'
        
        
    def disable_fields(self):
        self.helper.filter(basestring, greedy=True).update_attributes(disabled=True)
    
    def clean(self):
        cleaned_data = super(ContactCreateForm, self).clean()
        category = cleaned_data['category']
        nok_type = cleaned_data['nok_type']
        cw_type = cleaned_data['cw_type']
        organization = cleaned_data['cw_type']
        
        if ((category == ContactType.NEXT_OF_KIN and not nok_type) or
            (category == ContactType.CASE_WORKER and not cw_type)):
            
            raise forms.ValidationError(_("Type is a required field."))
        
        if (category == ContactType.CASE_WORKER and not organization ):
            raise forms.ValidationError(_('Organization is a required field for contacts of this type.'))

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
                    Field('info', wrapper_class="col-xs-12"),     
                    css_class="row"
                )
             )
        

AddressFormSet = generic_inlineformset_factory(Address, 
                                       formset=BaseGenericInlineFormSet, 
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
                            Field('type', wrapper_class="col-xs-3", placeholder=_("Type")),
                            Field('number',wrapper_class="col-xs-4", placeholder=_("Number (xxx-xxx-xxxx)")),                                        
                            Field('info', wrapper_class="col-xs-5", placeholder=_("Additionnal information")),
                            css_class="inline phone_row")
        
        
# class PhoneInlineFormSet(BaseGenericInlineFormSet):
#     def __init__(self, *args, **kwargs):
#         super(PhoneInlineFormSet, self).__init__(*args, **kwargs)
#         self.phone_helper = FormHelper()
#         self.phone_helper.form_tag = False
#         self.phone_helper.form_class = 'form-inline'
#         self.phone_helper.field_template = 'bootstrap3/layout/inline_field.html'
#         self.phone_helper.disable_csrf = True
#         self.phone_helper.layout = Layout(
#                                     Div(
#                                     Field('id', type="hidden"),
#                                     Field('DELETE', type="hidden"),
#                                     Field('type', wrapper_class="col-xs-3", placeholder=_("Type")),
#                                     Field('number',wrapper_class="col-xs-4", placeholder=_("Number (xxx-xxx-xxxx)")),                                        
#                                     Field('info', wrapper_class="col-xs-5", placeholder=_("Additionnal information")),
#                                     css_class="row")
                                            
                                        )
PhoneFormSet = generic_inlineformset_factory(Phone,
                                     formset=BaseGenericInlineFormSet,
                                     extra=1, min_num=1, max_num=3, validate_min=True, validate_max=True,
                                     fields=('type', 'number', 'info'))

