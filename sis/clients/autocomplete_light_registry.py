import autocomplete_light
from models import Client, RelationType 

# This will generate a PersonAutocomplete class
autocomplete_light.register(Client,
    # Just like in ModelAdmin.search_fields
    search_fields=['^first_name', 'last_name'],
    attrs={
        # This will set the input placeholder attribute:
        'placeholder': 'Client name ?',
        # This will set the yourlabs.Autocomplete.minimumCharacters
        # options, the naming conversion is handled by jQuery
        'data-autocomplete-minimum-characters': 1,
    },
    # This will set the data-widget-maximum-values attribute on the
    # widget container element, and will be set to
    # yourlabs.Widget.maximumValues (jQuery handles the naming
    # conversion).
    widget_attrs={
        'data-widget-maximum-values': 4,
        # Enable modern-style widget !
        'class': 'modern-style',
    },
)


class AutoCompleteRelationType(autocomplete_light.AutocompleteModelBase):
    autocomplete_js_attributes={'placeholder': 'relation with client ...'}
    
    def choices_for_request(self):
        q = self.request.GET.get('q', '')
        contact_type = self.request.GET.get('contact_type', None)

        choices = self.choices.all()
        if q:
            choices = choices.filter(type_en__icontains=q)
        if contact_type:
            choices = choices.filter(contact_type=contact_type)

        return self.order_choices(choices)[0:self.limit_choices]

autocomplete_light.register(RelationType, AutoCompleteRelationType)