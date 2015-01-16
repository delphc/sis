from django.contrib import admin

from orders.models import MealSide, StatusReasonCode

class StatusReasonCodeAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("desc_en",)}
 
class MealSideAdmin(admin.ModelAdmin):
   prepopulated_fields = {"slug": ("name_en",)}
    
admin.site.register(MealSide, MealSideAdmin)

admin.site.register(StatusReasonCode, StatusReasonCodeAdmin)
