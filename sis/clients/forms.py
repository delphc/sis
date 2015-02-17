import autocomplete_light
import datetime
import sys
from django import forms

from django.core.exceptions import NON_FIELD_ERRORS
from django.core.urlresolvers import reverse_lazy
from django.forms.fields import ChoiceField
from django.forms.models import ModelChoiceIterator
from django.forms.extras.widgets import SelectDateWidget
from django.forms.formsets import formset_factory
from django.contrib.contenttypes.forms import generic_inlineformset_factory, BaseGenericInlineFormSet
from django.template.loader import render_to_string
from django.utils import translation
from django.utils.translation import ugettext as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Button, Layout, Field, Fieldset, ButtonHolder, Div, HTML, Hidden, MultiWidgetField
from crispy_forms.bootstrap import (
    FormActions, StrictButton, InlineCheckboxes, InlineRadios, InlineField, UneditableField)

from crispy_forms.layout import LayoutObject, TEMPLATE_PACK
from crispy_forms.utils import flatatt

from diplomat.fields import LanguageChoiceField

from models import Client, Referral, ReferralReason
from contacts.models import Address, Phone
from deliveries.models import Route

from core.forms import PendForm, FormContainer, Cancel, CoreModelForm
from contacts.forms import ContactInfoForm, AddressFormSet, PhoneFormSet

import selectable.forms as selectable
from contacts.lookups import ContactLookup
    
# class ClientLookupForm(autocomplete_light.ModelForm):
#     class Meta:
#         model = Client
#         fields = [ 'first_name', 'last_name' ]
#     
#     name = autocomplete_light.ChoiceField('ClientAutocomplete')
#     
#     """
#     This form is used to get minimal information to check for client existency before creation
#     """
#     #route = forms.ModelChoiceField(queryset=Route.objects.all())
# 
#     def __init__(self, *args, **kwargs):
#         super(ClientLookupForm, self).__init__(*args, **kwargs)
#         
#         self.helper = FormHelper(self)
#         self.helper.form_method = 'POST'
#         self.helper.form_id = 'id-clientLookupForm'
#         #self.helper.form_action = reverse('client_create')
#         self.helper.form_title = 'Client Lookup'
#         self.helper.layout = Layout(
#             Div(HTML('<h4 class="page-header">{{ form_title }}'),
#                 css_class="row"),
#             Div(
#                 Field('first_name', wrapper_class="col-xs-3"),
#                 Field('last_name', wrapper_class="col-xs-3"),
#                 
#                 css_class="row"
#                 )
#             )  

class IdentificationCreateFormHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(IdentificationCreateFormHelper, self).__init__(*args)
        self.form_method = 'post'
        self.form_tag = False
        self.disable_csrf = True
        self.form_id = kwargs.pop('form_id')
        self.form_title = kwargs.pop('form_title')
        show_form_title = kwargs.pop('show_form_title')
        
        
        self.layout = Layout(
            Div(
                InlineRadios('gender', template="core/_custom_radioselect_inline.html"), #wrapper_class does not work with InlineRadios
                Field('first_name', wrapper_class="col-xs-3"),
                Field('middle_name', wrapper_class="col-xs-2"),
                Field('last_name', wrapper_class="col-xs-3"),
                
                css_class="row"
                ),                                    
            Div(
                Div(
                    MultiWidgetField('birth_date', attrs=({'style': 'width: 33%; display: inline-block; class:col-xs-1'})),   
                    css_class="col-xs-3"
                    ),
                    
                Field('maiden_name',wrapper_class="col-xs-3"),
                css_class="row"
                )
           )
        if show_form_title:
            self.layout.insert(0, 
                          Div(
                              HTML('<h4 class="page-header">{{ form_title }}'),
                              css_class="row")
                          
                          )        
        
                   
class ClientCreateForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['gender', 'first_name', 'middle_name', 'last_name', 'maiden_name', 
                  'birth_date']
        localized_fields = ('__all__')
        this_year = datetime.date.today().year
        widgets = {
            'birth_date' : SelectDateWidget(years=range(this_year - 130, this_year - 10))
        }
        
        error_messages = {
            NON_FIELD_ERRORS: {
                'unique_together': "%(model_name)s's %(field_labels)s are not unique.",
                }
            }
        
        
    def __init__(self, *args, **kwargs):
        super(ClientCreateForm, self).__init__(*args, **kwargs)
        
        self.helper = IdentificationCreateFormHelper(self, **{'form_id': 'id-clientCreateForm', 'form_title': 'Client Registration', 'show_form_title': True})
        
        
        

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

class ProfileForm(autocomplete_light.ModelForm):
    def __init__(self, *args, **kwargs):
        self.lang = kwargs.pop('lang', None)
        if 'edit' in kwargs:
            self.edit = kwargs.pop('edit')
        else:
            self.edit = False
        super(ProfileForm, self).__init__(*args, **kwargs)
        
    def is_valid(self):
        print >>sys.stderr, '*** data *** %s' % self.data
        return super(ProfileForm, self).is_valid()

class IdentificationEditFormHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(IdentificationEditFormHelper, self).__init__(*args, **kwargs)
        
        #cancel_url = reverse_lazy('client_profile_identification', kwargs={'pk':str(self.form.instance.id)})
        cancel_url = "{% url 'client_profile_identification' object.pk %}"
        
        self.form_tag = True
        self.form_method = 'post'
        self.form_action = reverse_lazy('client_profile_identification_edit', kwargs={'pk':str(self.form.instance.id)})
        self.form_class = 'form-horizontal'
        self.label_class = 'col-lg-3'
        self.field_class = 'col-lg-8'
        self.layout = Layout(
                                    'first_name', 
                                    'middle_name', 
                                    'last_name', 
                                    'gender', 
                                    'maiden_name', 
                                    MultiWidgetField('birth_date', attrs=({'style': 'width: 33%; display: inline-block;'})),   
                                    FormActions(
                                        Submit('save', 'Save changes'),
                                        HTML('<a class="btn btn-default" href="'+cancel_url+'" %}">'+_("Cancel")+"</a>"),
                                        css_class="form-actions pull-right"
                                        )
                                    )


                
class IdentificationForm(CoreModelForm):
    class Meta:
        model = Client
        fields = ['first_name', 'middle_name', 'last_name', 'gender', 'maiden_name', 'birth_date']
        localized_fields = ('__all__')
        this_year = datetime.date.today().year
        widgets = {
            'birth_date' : SelectDateWidget(years=range(this_year - 130, this_year - 10))
        }

    
    def __init__(self, *args, **kwargs):
        
        super(IdentificationForm, self).__init__(*args, **kwargs)
        
        if self.edit:
            self.helper = IdentificationEditFormHelper(form=self)
        else:
            self.helper = IdentificationCreateFormHelper(form=self, **{'form_id': 'id-form', 'form_title': 'Client Identification', 'show_form_title': False})
    

class CommunicationEditFormHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(CommunicationEditFormHelper, self).__init__(*args, **kwargs)
        
        cancel_url = "{% url 'client_profile_communication' object.pk %}"
        
        self.form_tag = True
        self.form_method = 'post'
        self.form_action = reverse_lazy('client_profile_communication_edit', kwargs={'pk':str(self.form.instance.id)})
        self.form_class = 'form-horizontal'
        self.label_class = 'col-lg-3'
        self.field_class = 'col-lg-8'
        self.layout = Layout(
                                    'com_lang', 
                                    'native_lang',
                                    'direct_contact',
                                    HTML('<h5>'+_("Is there anything that could hinder correspondance?")+'</h5>'),
                                    'cdif_exd', 
                                    'cdif_hoh',
                                    'cdif_anl', 
                                    'cdif_cog',
                                    FormActions(
                                        Submit('save', 'Save changes'),
                                        HTML('<a class="btn btn-default" href="'+cancel_url+'" %}">'+_("Cancel")+"</a>"),
                                        css_class="form-actions pull-right"
                                        )
                                    )

class CommunicationCreateFormHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(CommunicationCreateFormHelper, self).__init__(*args)
        self.form_method = 'post'
        self.form_tag = False
        self.form_id = kwargs.pop('form_id')
        self.form_title = kwargs.pop('form_title')
        show_form_title = kwargs.pop('show_form_title')
        
        
        self.layout = Layout(
            Div(
                Field('com_lang', wrapper_class="col-xs-4"),
                Field('native_lang', wrapper_class="col-xs-4"),
                css_class="row"
                ),                                    
            Div(
                Div(
                    InlineRadios('direct_contact'),  
                    css_class="col-xs-6"),
                css_class="row"
                ),
            Div(
                Div(
                    HTML('<h5>'+_("Is there anything that could hinder correspondance?")+'</h5>'),
                    css_class="col-xs-12"),
                css_class="row"),
            Div(
                Field("cdif_exd", wrapper_class="col-xs-offset-1 col-xs-6"),
                css_class="row"),
            Div(
                Field("cdif_hoh", wrapper_class="col-xs-offset-1 col-xs-6"),
                css_class="row"),
            Div(
                Field("cdif_anl", wrapper_class="col-xs-offset-1 col-xs-6"),
                css_class="row"),    
            Div(
                Field("cdif_cog", wrapper_class="col-xs-offset-1 col-xs-6"),
                css_class="row")
                
            )
            
        
class CommunicationForm(CoreModelForm):
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
#         self.fields['com_lang'].label=''
#         self.fields['native_lang'].label=''
#         self.fields['direct_contact'].label=''
        # NB: need to keep label for fields displayed as checkboxes
        
        self.fields['native_lang']=LanguageChoiceField()
        if self.edit:
            self.helper = CommunicationEditFormHelper(form=self)
        else:
            self.helper = CommunicationCreateFormHelper(form=self, **{'form_id': 'comm-form', 'form_title': _('Communication'), 'show_form_title': False})

        
        
                
class RefCategoryModelChoiceIterator(ModelChoiceIterator):
    def __init__(self, field, category):
        self.field = field
        self.queryset = field.queryset.filter(category=category)
        
class RefReasonsModelChoiceField(forms.ModelMultipleChoiceField):
    
    def label_from_instance(self, obj):
        lg = translation.get_language()
        if lg == "en":
            return obj.reason_en 
        else:
            return obj.reason_fr
        
    def _get_autonomyloss_choices(self):
        #if hasattr(self, '_choices'):
        #    return self._choices

        return RefCategoryModelChoiceIterator(self, ReferralReason.AUTONOMY_LOSS)

    autonomyloss = property(_get_autonomyloss_choices, ChoiceField._set_choices)
    
    def _get_socialisolation_choices(self):
        return RefCategoryModelChoiceIterator(self, ReferralReason.SOCIAL_ISOLATION)

    socialisolation = property(_get_socialisolation_choices, ChoiceField._set_choices)
    
    def _get_foodinsecurity_choices(self):
        return RefCategoryModelChoiceIterator(self, ReferralReason.FOOD_INSECURITY)

    foodinsecurity = property(_get_foodinsecurity_choices, ChoiceField._set_choices)


class ReferralCreateFormHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(ReferralCreateFormHelper, self).__init__(*args)
        self.form_method = 'post'
        self.form_tag = False
        self.form_id = kwargs.pop('form_id')
        self.form_title = kwargs.pop('form_title')
        show_form_title = kwargs.pop('show_form_title')
        
        self.layout = Layout(
            Div(
                Div(
                    MultiWidgetField('ref_date', attrs=({'style': 'width: 33%; display: inline-block; class:col-xs-1'})),   
                    css_class="col-xs-3"
                    ),
                css_class="row"
                ),
                                            
            Div(
                Field('reasons', template="clients/_client_ref_reasons_checkboxes.html"),
                css_class="row"),
            Div(
                Field('notes', wrapper_class="col-xs-12", rows="3"),
                css_class="row"),
            Div(
                Field('contact', wrapper_class="col-xs-6"),
                HTML('<div style="margin-top:20px"><a id="new-contact-button" href="#" class="btn btn-primary" data-target="#largeModal" data-toggle="modal" ><i class="fa fa-plus"></i>'+_(" Add New Contact ")+'</a></div>'),
                 
                css_class="row"),            
                )               

class ReferralEditFormHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(ReferralEditFormHelper, self).__init__(*args, **kwargs)
        
        cancel_url = "{% url 'client_profile_referral' object.pk %}"
        
        html_contact = '<div id="div_id_ref-contact-vo" class="form-group">'
        html_contact += '<label class="control-label col-lg-3 requiredField"> Contact</label>'
        html_contact += '<div class="form-readonly-field col-lg-9">'
        html_contact += '<label class="text-info"> Laura Smith</label>'
        html_contact += '</div>'
        html_contact += '</div>'
        
    

        self.form_tag = True
        self.form_method = 'post'
        self.form_action = reverse_lazy('client_profile_referral_edit', kwargs={'pk':str(self.form.instance.client.id)})
        self.form_class = 'form-horizontal'
        self.label_class = 'col-lg-3'
        self.field_class = 'col-lg-9'
        self.layout = Layout(MultiWidgetField('ref_date', attrs=({'style': 'width: 33%; display: inline-block;'})),                       
                             Div(
                                 Field('reasons', template="clients/_client_ref_reasons_checkboxes.html"),
                                 css_class="container-fluid"),
                             'notes', 
                             # referring contact cannot be modified
                             HTML(html_contact),
                             'contact', 
                             FormActions(
                                         Submit('save', 'Save changes'),
                                         HTML('<a class="btn btn-default" href="'+cancel_url+'" %}">'+_("Cancel")+"</a>"),
                                         css_class="form-actions pull-right"
                                         )
                            )
               
class ReferralForm(CoreModelForm):
    class Meta: 
        model = Referral
        fields = ['ref_date', 'reasons', 'notes', 'contact']
        autocomplete_fields = ('contact')
        
        this_year = datetime.date.today().year
        widgets = {
            'ref_date' : SelectDateWidget(years=range(this_year - 10, this_year)),
            #'contact': selectable.AutoComboboxSelectWidget(lookup_class=ContactLookup)
        }
        
#         reasonsAutonomyLoss = RefReasonsModelChoiceField(
#                                     queryset=ReferralReason.objects.filter(category=ReferralReason.AUTONOMY_LOSS).values('id', 'reason_en', 'category'), 
#                                     widget = forms.CheckboxSelectMultiple)
#         reasonsSocialIsolation = RefReasonsModelChoiceField(
#                                     queryset=ReferralReason.objects.filter(category=ReferralReason.SOCIAL_ISOLATION), 
#                                     widget = forms.CheckboxSelectMultiple)
#         reasonsFoodInsecurity = RefReasonsModelChoiceField(
#                                     queryset=ReferralReason.objects.filter(category=ReferralReason.FOOD_INSECURITY), 
#                                     widget = forms.CheckboxSelectMultiple)
#         widgets = {
#                    'contact': autocomplete_light.ChoiceWidget(
#                     'FlyAutocomplete', widget_attrs={'data-widget-bootstrap':
#                     'fly-widget'})
#                 }
        
    def __init__(self, *args, **kwargs):
        
        super(ReferralForm, self).__init__(*args, **kwargs)
        
        self.fields['reasons'] = RefReasonsModelChoiceField(
                                  queryset=ReferralReason.objects.all(), #.values('id', 'reason_en', 'category'),
                                  widget = forms.CheckboxSelectMultiple)
        
        if self.edit:
            self.helper = ReferralEditFormHelper(form=self)

        else:
            self.helper = ReferralCreateFormHelper(form=self, **{'form_id': 'ref-form', 'form_title': _('Referral'), 'show_form_title': False})
    
#         self.helper = FormHelper(self)
#         self.helper.form_method = 'POST'
#         self.helper.form_id = 'ref-form'
#         self.helper.form_tag = False
#         self.helper.form_title = _("Referral")
#         
#         self.fields['reasons'] = RefReasonsModelChoiceField(
#                                   queryset=ReferralReason.objects.all(), #.values('id', 'reason_en', 'category'),
#                                   widget = forms.CheckboxSelectMultiple)
#         #self.fields['contact'].empty_label=_('Select a contact')
#         
#         
#         
#         self.helper.layout = Layout(
#             Div(
#                 Div(
#                     MultiWidgetField('ref_date', attrs=({'style': 'width: 33%; display: inline-block; class:col-xs-1'})),   
#                     css_class="col-xs-3"
#                     ),
#                 css_class="row"
#                 ),
#                                             
#             Div(
#                 Field('reasons', template="clients/_client_ref_reasons_checkboxes.html"),
#                 css_class="row"),
#             Div(
#                 Field('notes', wrapper_class="col-xs-12", rows="3"),
#                 css_class="row"),
#             Div(
#                 Field('contact', wrapper_class="col-xs-6"),
#                 HTML('<div style="margin-top:20px"><a id="new-contact-button" href="#" class="btn btn-primary" data-target="#largeModal" data-toggle="modal" ><i class="fa fa-plus"></i>'+_(" Add New Contact ")+'</a></div>'),
#                  
#                 css_class="row"),            
#                 )               

        
        