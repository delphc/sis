from django.contrib import admin

from contacts.models import Address, Phone, Contact, Organization

# Register your models here.
admin.site.register(Address)
admin.site.register(Phone)

admin.site.register(Contact)
admin.site.register(Organization)





