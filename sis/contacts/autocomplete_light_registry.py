import autocomplete_light
from models import Contact

# This will generate a ContactAutocomplete class
autocomplete_light.register(Contact,
    name="Reference",
    # Just like in ModelAdmin.search_fields
    search_fields=['^first_name', 'last_name'],
    attrs={
        # This will set the input placeholder attribute:
        'placeholder': 'Contact name ?',
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
    add_another_url_name='add_another_contact_create'
    #choices = Contact.objects.filter(contact_type=Contact.SOCIAL_WORKER)
)
