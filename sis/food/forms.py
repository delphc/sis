from django.utils.translation import ugettext as _

from crispy_forms.layout import Submit, Layout, Field, Div
from crispy_forms.bootstrap import (
    FormActions, InlineCheckboxes)

from crispy_forms.layout import Layout

from core.forms import CoreModelForm, SetupFormHelper, ProfileEditFormHelper
from food.models import DietaryProfile

class DietSetupFormHelper(SetupFormHelper):   
    
    def __init__(self, *args, **kwargs):
        super(DietSetupFormHelper, self).__init__(*args, **kwargs)
        
        self.layout = Layout(
            Div(
                Field('prep_mode', wrapper_class="col-xs-4"),
                css_class="row"
                ),                                    
            Div(
                Field('restrictions',css_class="col-xs-12"),
                css_class="row"
                )
           )

class DietEditFormHelper(ProfileEditFormHelper):   
    
    def __init__(self, *args, **kwargs):
        kwargs.update({'tab': 'diet'})
        kwargs.update({'label_class':'col-lg-2'})
        kwargs.update({'field_class':'col-lg-9'})
        
        super(DietEditFormHelper, self).__init__(*args, **kwargs)
        
        self.layout = Layout(
                             'prep_mode',
                             'restrictions'
                             )
        
        
class DietForm(CoreModelForm):
    
    class Meta: 
        model = DietaryProfile
        fields = ['restrictions', 'prep_mode' ]
        
    def __init__(self, *args, **kwargs):
        super(DietForm, self).__init__(*args, **kwargs)
        
        if self.edit:
            self.helper = DietEditFormHelper(form=self, **{'cancel_url': 'client_profile_diet' })
        else:
            self.helper = DietSetupFormHelper(self, **{'form_id': 'id-dietCreateForm', 'form_title': _('Dietary Restrictions'), 'show_form_title': False})
        