from django.contrib import admin

from contacts.models import Address, Phone, ContactInfo, Contact, Organization, Position, OrganizationMember

from django.contrib.contenttypes.admin import GenericTabularInline

class AddressInline(admin.TabularInline):
    model = Address

class ContactInfoAdmin(admin.ModelAdmin):
    model = ContactInfo
    inlines = [ AddressInline,
                ]
class ContactInfoInline(GenericTabularInline):
    model = ContactInfo

class OrganizationMemberInline(admin.TabularInline):
    model = OrganizationMember
    
class ContactAdmin(admin.ModelAdmin):
    inlines = [
        ContactInfoInline, OrganizationMemberInline
    ]
    
# Register your models here.
admin.site.register(Address)
admin.site.register(Phone)
admin.site.register(Position)
admin.site.register(ContactInfo, ContactInfoAdmin)
admin.site.register(Contact, ContactAdmin)
admin.site.register(Organization)





