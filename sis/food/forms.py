from django.forms.models import inlineformset_factory
from django.forms.widgets import CheckboxSelectMultiple
from django.utils.translation import ugettext as _

from crispy_forms.layout import Submit, Layout, Field, Div
from crispy_forms.bootstrap import (
    FormActions, InlineField, InlineCheckboxes)

from crispy_forms.layout import Layout, HTML

from core.forms import CoreInlineFormHelper, InlineSelectButtons, CoreModelForm, SetupFormHelper, ProfileEditFormHelper, CoreBaseInlineFormSet, Formset
from food.models import DietaryProfile, Restriction

class DietSetupFormHelper(SetupFormHelper):   
    
    def __init__(self, *args, **kwargs):
        super(DietSetupFormHelper, self).__init__(*args, **kwargs)
        
        html_service_status = '<div class="row form-group">'
        html_service_status += '<label class="control-label col-xs-2">'+_('Service status')+'</label>'
        html_service_status += '<label class="col-xs-10 form-readonly-field">{{ order.get_current_status_display }}</label>'
        html_service_status += '</div>'
        
        self.layout = Layout(
            Div(
                InlineSelectButtons('prep_mode', wrapper_class="col-xs-4"),
                css_class="row"
                ),                                    
            Div(
                HTML('<label class="control-label col-xs-2">'+_('Dietary Restrictions')+'</label>'),
                css_class="row"
                )
#            Div(
#                Formset("div_restrict_diabetic", _("Diabetic"), "restrictions_form"),
#                css_class="row")
           )

class DietEditFormHelper(ProfileEditFormHelper):   
    
    def __init__(self, *args, **kwargs):
        kwargs.update({'tab': 'diet'})
        kwargs.update({'label_class':'col-lg-2'})
        kwargs.update({'field_class':'col-lg-9'})
        
        super(DietEditFormHelper, self).__init__(*args, **kwargs)
        
        self.layout = Layout(
                             InlineSelectButtons('prep_mode')
                             
                             )


class DietForm(CoreModelForm):
    
    class Meta: 
        model = DietaryProfile
        fields = ['prep_mode' ]
        
    def __init__(self, *args, **kwargs):
        super(DietForm, self).__init__(*args, **kwargs)
        self.fields['prep_mode'].widget = CheckboxSelectMultiple()
        self.fields['prep_mode'].help_text = ""
        if self.edit:
            self.helper = DietEditFormHelper(form=self, **{'cancel_url': 'client_profile_diet' })
        else:
            self.helper = DietSetupFormHelper(self, **{'form_id': 'id-dietCreateForm', 'form_title': _('Dietary Restrictions'), 'show_form_title': False})

    
class RestrictionForm(CoreModelForm):
    
    class Meta: 
        model = Restriction
        fields = ['ingredient','allergy' ]
        
    def __init__(self, *args, **kwargs):
        super(RestrictionForm, self).__init__(*args, **kwargs)
        
        if self.edit:
            self.helper = ProfileEditFormHelper(form=self, **{'cancel_url': 'client_profile_diet' })
        else:
            self.helper = CoreInlineFormHelper(self)

        self.helper.layout = Layout(
                                    Div(
                                        Field('ingredient', wrapper_class="col-xs-7"),
                                        Div(
                                            Field('allergy'),
                                            css_class="col-xs-3"),
                                        
                                        css_class="restriction_row inline row"
                                        )
                                    )

RestrictionFormSet = inlineformset_factory(DietaryProfile, Restriction, form=RestrictionForm, formset=CoreBaseInlineFormSet, can_delete=True,
                                     extra=0, min_num=0, max_num=5, validate_min=True, validate_max=True,
                                     fields=( 'ingredient', 'allergy'))

        