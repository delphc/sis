from django.db import models

from django_extensions.db.models import TimeStampedModel
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy

from auditlog.registry import auditlog
from auditlog.models import AuditlogHistoryField

# Create your models here.
class FoodCategory(TimeStampedModel):
    history = AuditlogHistoryField()
    
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=250, blank=True)

class FoodIngredient(TimeStampedModel):
    history = AuditlogHistoryField()
    
    name = models.CharField(max_length=100)
    category = models.ForeignKey(FoodCategory)
    
auditlog.register(FoodCategory)
auditlog.register(FoodIngredient)

