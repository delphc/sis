from django.contrib import admin

from clients.models import Client, ReferralReason, Referral, Relationship
from food.models import FoodCategory, FoodIngredient
# Register your models here.

admin.site.register(Client)
admin.site.register(FoodCategory)
admin.site.register(FoodIngredient)

admin.site.register(ReferralReason)
admin.site.register(Referral)

admin.site.register(Relationship)
