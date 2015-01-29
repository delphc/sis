try:
    from hashlib import md5
except:
    from md5 import new as md5

from django import forms

from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, Fieldset, ButtonHolder, Div, HTML, Hidden
from crispy_forms.layout import LayoutObject, TEMPLATE_PACK

from models import PendedForm

class Formset(LayoutObject):
    """
    Layout object. It renders an entire formset, as though it were a Field.

    Example::

    Formset("attached_files_formset")
    """

    template = "core/formset.html" 

    def __init__(self, div_id, formset_name_in_context, template=None):
        self.div_id = div_id
        self.formset_name_in_context = formset_name_in_context
                    
        # crispy_forms/layout.py:302 requires us to have a fields property
        self.fields = []

        # Overrides class variable with an instance level variable
        if template:
            self.template = template
            
#     def div_id(self):
#         return self.div_id
    
    def render(self, form, form_style, context, template_pack=TEMPLATE_PACK):
        formset = context[self.formset_name_in_context]
        return render_to_string(self.template, {'wrapper': self,
                                                    'formset': formset})
    
class PendForm(forms.Form):
    def __init__(self, *args, **kwargs):
        self.object_pk = kwargs.pop('object_pk', None)
        super(PendForm, self).__init__(*args, **kwargs)
            
    @classmethod
    def get_import_path(cls):
        return '%s.%s' % (cls.__module__, cls.__name__)

#     def hash_data(self):
#         content = ','.join('%s:%s' % (n, self.data[n]) for n in self.fields.keys())
#         return md5(content).hexdigest()

    def pend(self):
        import_path = self.get_import_path()
        form_object_pk = self.object_pk
        pended_form = PendedForm.objects.get_or_create(form_class=import_path,
                                                       object_pk=object_pk)
        for name in self.fields:
            pended_form.data.get_or_create(name=name, value=self.data[name])
        return form_hash  
    
        
    @classmethod
    def resume(cls, form_hash):
        import_path = cls.get_import_path()
        form = models.PendForm.objects.get(form_class=import_path, object_pk=object_pk)
        data = dict((d.name, d.value) for d in form.data.all())
        return cls(data)