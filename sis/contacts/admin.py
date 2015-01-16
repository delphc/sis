from django.contrib import admin

from contacts.models import Address, Phone, Contact, ContactType, Organization

# Register your models here.
admin.site.register(Address)
admin.site.register(Phone)

admin.site.register(ContactType)
admin.site.register(Contact)
admin.site.register(Organization)





