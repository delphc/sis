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

from models import Order, OrderStop, DeliveryDefault, DefaultMealSide
from clients.forms import ProfileForm
   
class RefReasonsModelChoiceField(forms.ModelMultipleChoiceField):
    lang = None
    
    def label_from_instance(self, obj):
        if self.lang == "en":
            return obj.reason_en 
        else:
            return obj.reason_fr
    
class OrderForm(ProfileForm):
    create_or_update_stop = forms.BooleanField(
                                         initial = False,
                                         label = '',
                                         required = False,
                                         widget = forms.HiddenInput
                                         )
    remove_stop = forms.BooleanField(
                                         initial = False,
                                         label = '',
                                         required = False,
                                         widget = forms.HiddenInput
                                         )
    class Meta: 
        model = Order
        fields = ['start_date', 'type', 'monday', 'tuesday', 'wednesday', 'friday', 'saturday']
        
    def __init__(self, *args, **kwargs):
        
        super(OrderForm, self).__init__(*args, **kwargs)
        
        
        self.helper = FormHelper(self)
        self.helper.form_method = 'POST'
        self.helper.form_id = 'order-form'
        
        self.fields['start_date'].label = ''
        self.fields['type'].label=''
        self.fields['monday'].label = ''
        self.fields['monday'].widget = forms.HiddenInput()
        self.fields['tuesday'].label = ''
        self.fields['tuesday'].widget = forms.HiddenInput()
        self.fields['wednesday'].label = ''
        self.fields['wednesday'].widget = forms.HiddenInput()
        self.fields['friday'].label = ''
        self.fields['friday'].widget = forms.HiddenInput()
        self.fields['saturday'].label = ''
        self.fields['saturday'].widget = forms.HiddenInput()
        
        
class OrderStopForm(forms.ModelForm):
    class Meta:
        model = OrderStop
        fields = ['start_date', 'end_date', 'reason_code', 'reason_other' ]
        localized_fields = ('__all__')
       
    def __init__(self, *args, **kwargs):
        super(OrderStopForm, self).__init__(*args, **kwargs)
 
        self.fields['start_date'].label=_('From')
        self.fields['end_date'].label=_('To')
        self.fields['reason_code'].label=_('Reason')
        self.fields['reason_other'].label=_('Precise reason')
          
    def save(self, commit=True):
        instance = super(OrderStopForm, self).save(commit=False)
        instance.end_date = self.cleaned_data['end_date'] 
        if (instance.end_date == None):
            instance.end_date = self.cleaned_date['start_date']
         
        if commit:
            instance.save()
             
        return instance
  
class OrderStopFormHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super(OrderStopFormHelper, self).__init__(*args, **kwargs)
        self.form_method = 'post'
        self.form_id = 'order-status-form'
        self.form_tag = True
        self.disable_csrf = True
        self.form_class = 'form-inline'
        self.field_template = 'bootstrap3/layout/inline_field.html'
        self.disable_csrf = True
        self.layout = Layout(
                            Div(
                                Div(
                                    Field('start_date', wrapper_class="col-xs-6"), 
                                    Field('end_date', wrapper_class="col-xs-6"), 
                                    css_class="row"),
                                Div(
                                    Field('reason_code', wrapper_class="col-xs-4"),
                                    Field('reason_other', wrapper_class="col-xs-8"),
                                    css_class="row"),
                                css_class="status_row")
                            )

class DeliveryDefaultForm (forms.ModelForm):
    class Meta:
        model = DeliveryDefault
        fields = ['nb_meal']
        localized_fields = ('__all__')
       
    def __init__(self, *args, **kwargs):
        super(DeliveryDefaultForm, self).__init__(*args, **kwargs)
 
        self.fields['nb_meal'].label=_('Meals')
        
        self.helper = FormHelper(self)
        self.helper.form_method = 'POST'
        self.helper.form_id = 'deliv-form'
        self.helper.form_tag = False
        self.helper.disable_csrf = False
        
        

DefaultMealSideFormSet=inlineformset_factory(DeliveryDefault, DefaultMealSide,
                                             extra=0, min_num=0, max_num=4, validate_min=True, validate_max=True,
                                             fields=('quantity', 'side')
                                             )
