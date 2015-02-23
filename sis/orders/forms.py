from django import forms

from django.core.urlresolvers import reverse_lazy
from django.forms.formsets import formset_factory
from django.forms.models import inlineformset_factory, BaseInlineFormSet
from django.forms.widgets import CheckboxSelectMultiple, RadioSelect
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, Fieldset, ButtonHolder, Div, HTML, Hidden
from crispy_forms.bootstrap import (
    FormActions, TabHolder, Tab, InlineCheckboxes, InlineRadios, InlineField, UneditableField)

from crispy_forms.layout import Layout, TEMPLATE_PACK
from crispy_forms.utils import flatatt

from models import Order, MealDefault, MealDefaultMeal, MealDefaultSide, ServiceDay
from core.forms import CoreInlineFormHelper, CoreModelForm, CoreBaseInlineFormSet
   
class SetupFormHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        self.form_id = kwargs.pop('form_id')
        self.form_title = kwargs.pop('form_title')
        show_form_title = kwargs.pop('show_form_title')
        
        super(SetupFormHelper, self).__init__(*args, **kwargs)
        self.form_method = 'post'
        self.form_tag = False
        self.disable_csrf = True
        
    
class DaysInlineButtons(InlineCheckboxes):
    """
    Layout object for rendering checkboxes inline::

        DaysInlineButtons('field_name')
    """
    template = "orders/days_selectmultiple_inline.html"

    def render(self, form, form_style, context, template_pack=TEMPLATE_PACK):
        context.update({'inline_class': 'inline'})
        return super(InlineCheckboxes, self).render(form, form_style, context)

            
class OrderSetupFormHelper(SetupFormHelper):   
    
    def __init__(self, *args, **kwargs):
        super(OrderSetupFormHelper, self).__init__(*args, **kwargs)
        
        self.layout = Layout(
            Div(
                Field('type', wrapper_class="col-xs-3"),
                
                css_class="row"
                ),                                    
            Div(
                DaysInlineButtons('days',css_class="col-xs-12"),
                css_class="row"
                ),
            Div(
                Div(
                    InlineRadios('meal_defaults_type'),
                    css_class="col-xs-4"
                ),
                css_class="row"
                )
           )

   
                   
class OrderForm(CoreModelForm):
    DEFAULTS_TYPE_EVERYDAY='A'
    DEFAULTS_TYPE_DAY='D'
    DEFAULTS_TYPE_CHOICES = (
                             (DEFAULTS_TYPE_EVERYDAY, _('Same for everyday')),
                             (DEFAULTS_TYPE_DAY, _('Day-specific'))
                             )
    meal_defaults_type = forms.ChoiceField(choices=DEFAULTS_TYPE_CHOICES,
                                      widget=RadioSelect)
    class Meta: 
        model = Order
        fields = ['type', 'days' ]
        
    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        if not instance:
            kwargs.update(initial={ "meal_defaults_type": self.DEFAULTS_TYPE_EVERYDAY })
        super(OrderForm, self).__init__(*args, **kwargs)
        self.fields['days'].widget = CheckboxSelectMultiple()
        self.fields['days'].help_text = ""
        self.helper = OrderSetupFormHelper(self, **{'form_id': 'id-orderCreateForm', 'form_title': _('Meal Default'), 'show_form_title': False})
        
        
class MealDefaultSetupFormHelper(SetupFormHelper):   
    
    def __init__(self, *args, **kwargs):
        super(MealDefaultSetupFormHelper, self).__init__(*args, **kwargs)
        
        self.layout = Layout(
            Div(
                Field('day', wrapper_class="col-xs-3"),
                Field('nb_meal', wrapper_class="col-xs-3"),
                Field('meal_type', wrapper_class="col-xs-3"),
                
                css_class="row"
                )
           )

        
class MealDefaultForm(CoreModelForm):
    class Meta:
        model = MealDefault
        fields = [ 'day' ]
    
    def __init__(self, *args, **kwargs):
        
        super(MealDefaultForm, self).__init__(*args, **kwargs)
        
        self.helper = MealDefaultSetupFormHelper(self, **{'form_id': 'id-orderCreateForm', 'form_title': 'Meal Service', 'show_form_title': False})


        

class MealDefaultMealSetupFormHelper(CoreInlineFormHelper):   
    
    def __init__(self, *args, **kwargs):
        super(MealDefaultMealSetupFormHelper, self).__init__(*args, **kwargs)
        
        formset_prefix = self.form.prefix.split('-')[0]
        self.layout = Layout(
            Div(
                Field('quantity', wrapper_class="col-xs-2"),
                HTML('<div class="col-xs-1 form-label"><span>'+_("Meal")+'</span></div>'),
                Field('size', wrapper_class="col-xs-3"),
                
                css_class="inline meal_row_"+formset_prefix+" row"
                )
           )

                   
class MealDefaultMealForm(CoreModelForm):
    class Meta:
        model = MealDefaultMeal
        fields = [ 'size', 'quantity' ]
    
    def __init__(self, *args, **kwargs):
        
        super(MealDefaultMealForm, self).__init__(*args, **kwargs)
        
        self.helper = MealDefaultMealSetupFormHelper(self)

MealDefaultMealFormSet = inlineformset_factory(MealDefault, MealDefaultMeal, form=MealDefaultMealForm, formset=CoreBaseInlineFormSet, can_delete=True,
                                     extra=0, min_num=1, max_num=2, validate_min=True, validate_max=True,
                                     fields=( 'size', 'quantity' ))



class MealDefaultSideSetupFormHelper(CoreInlineFormHelper):   
    
    def __init__(self, *args, **kwargs):
        super(MealDefaultSideSetupFormHelper, self).__init__(*args, **kwargs)
        
        formset_prefix = self.form.prefix.split('-')[0]
        self.layout = Layout(
            Div(
                Field('quantity', wrapper_class="col-xs-2"),
                Field('side', wrapper_class="col-xs-3"),
                
                css_class="inline side_row_"+formset_prefix +" row" 
                )
           )
        
class MealDefaultSideForm(CoreModelForm):
    class Meta:
        model = MealDefaultSide
        fields = [ 'side', 'quantity' ]
    
    def __init__(self, *args, **kwargs):
        
        super(MealDefaultSideForm, self).__init__(*args, **kwargs)
        
        self.helper = MealDefaultSideSetupFormHelper(self)
        
MealDefaultSideFormSet = inlineformset_factory(MealDefault, MealDefaultSide, form=MealDefaultSideForm, formset=CoreBaseInlineFormSet, can_delete=True,
                                     extra=0, min_num=1, max_num=3, validate_min=True, validate_max=True,
                                     fields=( 'side', 'quantity' ))

