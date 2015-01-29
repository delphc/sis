import autocomplete_light
from django import forms

from django.core.exceptions import NON_FIELD_ERRORS
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

from models import Client, Referral, ReferralReason
from contacts.models import Address, Phone
from deliveries.models import Route

from core.forms import PendForm
from contacts.forms import AddressFormSet, PhoneFormSet

    
class ClientLookupForm(autocomplete_light.ModelForm):
    class Meta:
        model = Client
        fields = [ 'first_name', 'last_name' ]
    
    name = autocomplete_light.ChoiceField('ClientAutocomplete')
    
    """
    This form is used to get minimal information to check for client existency before creation
    """
    #route = forms.ModelChoiceField(queryset=Route.objects.all())

    def __init__(self, *args, **kwargs):
        super(ClientLookupForm, self).__init__(*args, **kwargs)
        
        self.helper = FormHelper(self)
        self.helper.form_method = 'POST'
        self.helper.form_id = 'id-clientLookupForm'
        #self.helper.form_action = reverse('client_create')
        self.helper.form_title = 'Client Lookup'
        self.helper.layout = Layout(
            Div(HTML('<h4 class="page-header">{{ form_title }}'),
                css_class="row"),
            Div(
                Field('first_name', wrapper_class="col-xs-3"),
                Field('last_name', wrapper_class="col-xs-3"),
                
                css_class="row"
                )
            )  
         
class ClientCreateForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['gender', 'first_name', 'middle_name', 'last_name', 'maiden_name', 
                  'birth_date' ]
        localized_fields = ('__all__')
        
        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': "%(model_name)s's %(field_labels)s are not unique.",
                }
            }
        
    #email_address = forms.CharField()
    
        
    def __init__(self, *args, **kwargs):
        super(ClientCreateForm, self).__init__(*args, **kwargs)
        
        self.helper = FormHelper(self)
        self.helper.form_method = 'POST'
        self.helper.form_id = 'id-clientCreateForm'
        #self.helper.form_action = reverse('client_create')
        self.helper.form_title = 'Client Registration'
        self.helper.layout = Layout(
            Div(HTML('<h4 class="page-header">{{ form_title }}'),
                css_class="row"),
            Div(
                #Field('gender', wrapper_class="col-xs-2"),
                InlineRadios('gender', template="core/_custom_radioselect_inline.html"), #wrapper_class does not work with InlineRadios
                Field('first_name', wrapper_class="col-xs-3"),
                Field('middle_name', wrapper_class="col-xs-2"),
                Field('last_name', wrapper_class="col-xs-3"),
                
                css_class="row"
                ),                                    
            Div(
                Field('birth_date', wrapper_class="col-xs-2"),   
                Field('maiden_name',wrapper_class="col-xs-3"),
                css_class="row"
                )
 
            )   
        

    def use_for_update(self):
        
        self.helper.form_action = 'client_update'
        self.helper.form_title = 'Client Update'
        self.helper[2] = FormActions(Submit('update', 'update', css_class='btn-primary'),
                        css_class="col-xs-12")
        
    def disable_fields(self):
        self.helper.filter(basestring, greedy=True).update_attributes(disabled=True)
         
    def clean(self):
        cleaned_data = super(ClientCreateForm, self).clean()
        gender = cleaned_data.get("gender", "")
        maiden_name = cleaned_data.get("maiden_name", "")
        
        if gender == Client.FEMALE and not maiden_name:   
            msg = u"Maiden name has to be filled out"
            raise forms.ValidationError(msg)
        
        return cleaned_data

class ClientSetupForm(PendForm):
    birth_date = forms.DateField()
    
    def __init__(self, *args, **kwargs):
        super(ClientSetupForm, self).__init__(*args, **kwargs)
        
        self.helper = FormHelper(self)
        self.helper.form_method = 'POST'
        self.helper.form_id = 'id-clientSetupForm'
        self.helper.form_title = 'Client Profile Setup'
        self.helper.form_tag = False

class ProfileForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.lang = kwargs.pop('lang', None)
        
        super(ProfileForm, self).__init__(*args, **kwargs)
        
class IdentificationForm(ProfileForm):
    class Meta:
        model = Client
        fields = ['first_name', 'middle_name', 'last_name', 'gender', 'maiden_name', 'birth_date', 'status']
        localized_fields = ('__all__')

    
    def __init__(self, *args, **kwargs):
        super(IdentificationForm, self).__init__(*args, **kwargs)
        
        # need the following because
        #   self.helper.form_show_labels = False
        # does not work
        self.fields['first_name'].label=''
        self.fields['middle_name'].label=''
        self.fields['last_name'].label=''
        self.fields['maiden_name'].label=''
        self.fields['gender'].label=''
        self.fields['birth_date'].label=''
        self.fields['status'].label=''
        
        self.helper = FormHelper(self)
        self.helper.form_method = 'POST'
        self.helper.form_id = 'id-form'
        
class CommunicationForm(ProfileForm):
    class Meta:
        model = Client
        fields = ['com_lang', 'native_lang', 'direct_contact', 'cdif_exd', 'cdif_hoh', 'cdif_anl', 'cdif_cog']
        localized_fields = ('__all__')
        widgets = {
            'direct_contact' : forms.RadioSelect
        }
    
    def __init__(self, *args, **kwargs):
        super(CommunicationForm, self).__init__(*args, **kwargs)
        
        # need the following because
        #   self.helper.form_show_labels = False
        # does not work
        self.fields['com_lang'].label=''
        self.fields['native_lang'].label=''
        self.fields['direct_contact'].label=''
        # NB: need to keep label for fields displayed as checkboxes
       
        
        self.helper = FormHelper(self)
        self.helper.form_method = 'POST'
        self.helper.form_id = 'comm-form'

class RefReasonsModelChoiceField(forms.ModelMultipleChoiceField):
    lang = None
    
    def label_from_instance(self, obj):
        if self.lang == "en":
            return obj.reason_en 
        else:
            return obj.reason_fr
    
class ReferralForm(ProfileForm):
    class Meta: 
        model = Referral
        fields = ['ref_date', 'reasons', 'notes', 'contact']
        
    def __init__(self, *args, **kwargs):
        
        super(ReferralForm, self).__init__(*args, **kwargs)
        
        self.helper = FormHelper(self)
        self.helper.form_method = 'POST'
        self.helper.form_id = 'ref-form'
        
        self.fields['reasons'] = RefReasonsModelChoiceField(
                                    queryset=ReferralReason.objects.all(), 
                                    widget = forms.CheckboxSelectMultiple)
        
        self.fields['reasons'].label=''
        self.fields['reasons'].lang=self.lang
        
        self.fields['notes'].label=''
        self.fields['ref_date'].label=''
        self.fields['contact'].label=''
        self.fields['contact'].empty_label=_('Add new contact')
        self.fields['contact'].required = False
        
        