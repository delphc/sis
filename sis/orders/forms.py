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
    FormActions, TabHolder, Tab, InlineRadios, InlineField, UneditableField)

from crispy_forms.layout import Layout, TEMPLATE_PACK
from crispy_forms.utils import flatatt

from models import Order, MealDefault, MealDefaultMeal, MealDefaultSide, ServiceDay
from core.forms import InlineSelectButtons, CoreInlineFormHelper, CoreModelForm, CoreBaseInlineFormSet, SetupFormHelper, ProfileEditFormHelper
   
    

            
class OrderSetupFormHelper(SetupFormHelper):   
    
    def __init__(self, *args, **kwargs):
        super(OrderSetupFormHelper, self).__init__(*args, **kwargs)
        
        self.layout = Layout(
            Div(
                Field('type', wrapper_class="col-xs-3"),
                
                css_class="row"
                ),                                    
            Div(
                InlineSelectButtons('days',css_class="col-xs-12"),
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

        
class OrderEditFormHelper(ProfileEditFormHelper):   
    
    def __init__(self, *args, **kwargs):
        kwargs.update({'tab': 'order'})
        kwargs.update({'label_class':'col-lg-2'})
        kwargs.update({'field_class':'col-lg-9'})
        
        super(OrderEditFormHelper, self).__init__(*args, **kwargs)
        
        self.form_tag = False
        
        html_service_status = '<div class="row form-group">'
        html_service_status += '<label class="control-label col-xs-2">'+_('Service status')+'</label>'
        html_service_status += '<label class="col-xs-10 form-readonly-field">{{ order.get_current_status_display }}</label>'
        html_service_status += '</div>'
        
        order    = self.form.instance
        self.form_action = reverse_lazy('client_profile_'+self.tab+'_edit', kwargs={'pk':str(order.client.id)})
        
        
        self.layout = Layout(
                             HTML(html_service_status),
                             Div('type', css_class="row"),
                             Div(InlineSelectButtons('days'), css_class="row"), 
                             Div(InlineRadios('meal_defaults_type'),css_class="row")
                             )

               
class OrderForm(CoreModelForm):
    
    meal_defaults_type = forms.ChoiceField(choices=Order.DEFAULTS_TYPE_CHOICES,
                                      widget=RadioSelect)
    class Meta: 
        model = Order
        fields = ['type', 'days' ]
        
    def __init__(self, *args, **kwargs):
        instance = kwargs.get('instance', None)
        if not instance:
            kwargs.update(initial={ "meal_defaults_type": Order.DEFAULTS_TYPE_EVERYDAY['code'] })
        else:
            kwargs.update(initial={ "meal_defaults_type": instance.get_meal_defaults_type_code() })
        super(OrderForm, self).__init__(*args, **kwargs)
        self.fields['days'].widget = CheckboxSelectMultiple()
        self.fields['days'].help_text = ""
        
        if self.edit:
            self.helper = OrderEditFormHelper(form=self, **{'cancel_url': 'client_profile_order' })
        else:
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

# This form does not actually serve for now
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
                #Field('id', type="hidden"),
                Field('quantity', wrapper_class="col-xs-3"),
                HTML('<div class="col-xs-2 form-label"><span>'+_("Meal")+'</span></div>'),
                Field('size', wrapper_class="col-xs-5"),
                
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
                #Field('id', type="hidden"),
                Field('quantity', wrapper_class="col-xs-4"),
                Field('side', wrapper_class="col-xs-6"),
                
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
                                     extra=0, min_num=0, max_num=3, validate_min=True, validate_max=True,
                                     fields=( 'side', 'quantity' ))

