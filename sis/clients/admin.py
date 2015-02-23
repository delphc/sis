from django.contrib import admin

from clients.models import Client, ReferralReason, Referral, RelationType, Relationship
from food.models import FoodCategory, FoodIngredient
from contacts.admin import ContactInfoInline

class ClientAdmin(admin.ModelAdmin):
    inlines = [
        ContactInfoInline,
    ]
    
# Register your models here.

admin.site.register(Client, ClientAdmin)
admin.site.register(FoodCategory)
admin.site.register(FoodIngredient)

admin.site.register(ReferralReason)
admin.site.register(Referral)

admin.site.register(RelationType)
admin.site.register(Relationship)
