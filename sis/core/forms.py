try:
    from hashlib import md5
except:
    from md5 import new as md5

import autocomplete_light

from django import forms
from django.db.models.fields import BLANK_CHOICE_DASH

from django.core.urlresolvers import reverse_lazy
from django.forms import models
from django.forms.formsets import BaseFormSet

from django.forms.models import inlineformset_factory, BaseInlineFormSet
from django.template.loader import render_to_string
from django.utils.datastructures import SortedDict, MultiValueDict
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, Fieldset, ButtonHolder, Div, HTML, Hidden
from crispy_forms.layout import LayoutObject, BaseInput, TEMPLATE_PACK
from crispy_forms.bootstrap import InlineCheckboxes


from models import PendedForm

class CoreInlineFormHelper(FormHelper):   
    
    def __init__(self, *args, **kwargs):
        super(CoreInlineFormHelper, self).__init__(*args, **kwargs)
        self.form_method = 'post'
        self.form_tag = False
        self.disable_csrf = True
        self.form_class = 'form-inline'
        self.field_template = 'bootstrap3/layout/inline_field.html'

class SetupFormHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        self.form_id = kwargs.pop('form_id')
        self.form_title = kwargs.pop('form_title')
        show_form_title = kwargs.pop('show_form_title')
        
        super(SetupFormHelper, self).__init__(*args, **kwargs)
        self.form_method = 'post'
        self.form_tag = False
        self.disable_csrf = True
        
        
class ProfileEditFormHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        if 'label_class' in kwargs:      
            label_class = kwargs.pop('label_class')
        else:
            label_class = 'col-lg-3'
        if 'field_class' in kwargs:      
            field_class = kwargs.pop('field_class')
        else:
            field_class = 'col-lg-9'
        
        self.tab = kwargs.pop('tab')
        self.cancel_url = kwargs.pop('cancel_url')
        
        super(ProfileEditFormHelper, self).__init__(*args, **kwargs)
        
        
        self.label_class = label_class
        self.field_class = field_class
        self.form_tag = True
        self.form_method = 'post'
        self.form_class = 'form-horizontal'
        
    def add_form_actions(self):
        self.layout.append(
                 FormActions(
                             Submit('save', 'Save changes'),
                             HTML('<a class="btn btn-default" href="'+self.cancel_url+'">'+_("Cancel")+"</a>"),
                             css_class="form-actions pull-right"
                             )
                )
        
class CoreModelForm(autocomplete_light.ModelForm):
    """
        edit attribute indicates whether the form is used for update (edit=True) or creation (edit=False)
        It is set to False by default, if not provided within kwargs
    """ 
    def __init__(self, *args, **kwargs):
        self.lang = kwargs.pop('lang', None)
        if 'edit' in kwargs:
            self.edit = kwargs.pop('edit')
        else:
            self.edit = False
        super(CoreModelForm, self).__init__(*args, **kwargs)
        
class CoreBaseInlineFormSet(BaseInlineFormSet):
    def __init__(self, data=None, files=None, instance=None,
                 save_as_new=False, prefix=None, queryset=None, **kwargs):
        if 'edit' in kwargs:
            self.edit = kwargs.pop('edit')
        else:
            self.edit = False
        super(CoreBaseInlineFormSet, self).__init__( data, files, instance,
                 save_as_new, prefix, queryset, **kwargs)

    
class FormContainerMetaclass(type):
    def __new__(cls, name, bases, attrs):
        form_classes = SortedDict(
            (prefix, attrs.pop(prefix))
            for prefix, form_class in attrs.items()
            if isinstance(form_class, type) and issubclass(form_class, (forms.BaseForm, BaseFormSet))
        )

        new_class = super(FormContainerMetaclass, cls).__new__(cls, name, bases, attrs)

        new_class.form_classes = form_classes

        # Making the form container look like a form, for the
        # sake of the FormWizard.
        new_class.base_fields = {}
        for prefix, form_class in new_class.form_classes.items():
            if issubclass(form_class, BaseFormSet):
                new_class.base_fields.update(form_class.form.base_fields)
            else:
                new_class.base_fields.update(form_class.base_fields)

        return new_class


class FormContainer(object):
    __metaclass__ = FormContainerMetaclass

    def __init__(self, prefix, **kwargs):
        self._errors = {}
        self.forms = SortedDict()
        container_prefix = prefix #kwargs.pop('prefix', '')

        # Instantiate all the forms in the container
        for form_prefix, form_class in self.form_classes.items():
            self.forms[form_prefix] = form_class(
                build_prefix='-'.join(p for p in [container_prefix, form_prefix] if p),
                **self.get_form_kwargs(form_prefix, **kwargs)
            )

    def get_form_kwargs(self, prefix, **kwargs):
        """Return per-form kwargs for instantiating a specific form

        By default, just returns the kwargs provided. prefix is the
        label for the form in the container, allowing you to specify
        extra (or less) kwargs for each form in the container.
        """
        return kwargs

    def __unicode__(self):
        "Render all the forms in the container"
        return mark_safe(u''.join([f.as_table() for f in self.forms.values()]))

    def __iter__(self):
        "Return each of the forms in the container"
        for prefix in self.forms:
            yield self[prefix]

    def __getitem__(self, prefix):
        "Return a specific form in the container"
        try:
            form = self.forms[prefix]
        except KeyError:
            raise KeyError('Prefix %r not found in Form container' % prefix)
        return form

    def is_valid(self):
        return all(f.is_valid() for f in self.forms.values())

    @property
    def data(self):
        "Return a compressed dictionary of all data from all subforms"
        all_data = MultiValueDict()
        for prefix, form in self.forms.items():
            for key in form.data:
                all_data.setlist(key, form.data.getlist(key))
        return all_data

    @property
    def files(self):
        "Return a compressed dictionary of all files from all subforms"
        all_files = MultiValueDict()
        for prefix, form in self.forms.items():
            for key in form.files:
                all_files.setlist(key, form.files.getlist(key))
        return all_files

    @property
    def errors(self):
        "Return a compressed dictionary of all errors form all subforms"
        return dict((prefix, form.errors) for prefix, form in self.forms.items())

    def save(self, *args, **kwargs):
        "Save each of the subforms"
        return [f.save(*args, **kwargs) for f in self.forms.values()]

    def save_m2m(self):
        """Save any related objects -- e.g., m2m entries or inline formsets

        This is needed if the original form collection was saved with commit=False
        """
        for prefix, form in self.forms.items():
            try:
                for subform in form.saved_forms:
                    # Because the related instance wasn't saved at the time the
                    # form was created, the new PK value hasn't propegated to
                    # the inline object on the formset. We need to re-set the
                    # instance to update the _id attribute, which will allow the
                    # inline form instance to save.
                    setattr(subform.instance, form.fk.name, form.instance)
                    subform.instance.save()
            except AttributeError:
                pass

            try:
                form.save_m2m()
            except AttributeError:
                pass
            
# And now, an EXAMPLE OF USAGE :
# Assuming you have a UserDetailsForm, and an AddressesFormSet...

# class UserFormsContainer(FormContainer):
#     user = UserDetailForm
#     addresses = AddressesFormSet
    
class Cancel(BaseInput):
    """
    Used to create a Submit button descriptor for the {% crispy %} template tag::

        submit = Submit('Search the Site', 'search this site')

    .. note:: The first argument is also slugified and turned into the id for the submit button.
    """
    input_type = 'cancel'
    field_classes = 'cancel cancelButton' if TEMPLATE_PACK == 'uni_form' else 'btn btn-default'

class InlineSelectButtons(InlineCheckboxes):
    """
    Layout object for rendering checkboxes inline::

        DaysInlineButtons('field_name')
    """
    template = "orders/days_selectmultiple_inline.html"

    def render(self, form, form_style, context, template_pack=TEMPLATE_PACK):
        context.update({'inline_class': 'inline'})
        return super(InlineCheckboxes, self).render(form, form_style, context)

class Formset(LayoutObject):
    """
    Layout object. It renders an entire formset, as though it were a Field.

    Example::

    Formset("attached_files_formset")
    """

    template = "core/formset.html" 

    def __init__(self, div_id, formset_title, formset_name_in_context, template=None):
        self.div_id = div_id
        self.formset_title = formset_title
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