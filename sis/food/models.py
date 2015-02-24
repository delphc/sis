from django.db import models

from django_extensions.db.models import TimeStampedModel
from django.utils import translation
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy

from auditlog.registry import auditlog
from auditlog.models import AuditlogHistoryField

from core.models import TranslatedModel

from clients.models import Client


    
        
# Create your models here.
class FoodCategory(TimeStampedModel, TranslatedModel):
    history = AuditlogHistoryField()
    slug = models.SlugField(default='')
    name_en = models.CharField(max_length=100, default='')
    name_fr = models.CharField(max_length=100, default='')
    description_en = models.CharField(max_length=250, blank=True, default='')
    description_fr = models.CharField(max_length=250, blank=True, default='')
    sort_order = models.PositiveIntegerField(default=0)
    
    def __unicode__(self):
        return self.get_name()
        
        
class FoodIngredient(TimeStampedModel):
    history = AuditlogHistoryField()
    slug = models.SlugField(default='')
    name_en = models.CharField(max_length=100, default='')
    name_fr = models.CharField(max_length=100, default='')
    categories = models.ManyToManyField(FoodCategory)

    def __unicode__(self):
        return self.get_name()
    
    

class FoodPreparationMode(TranslatedModel):
    slug = models.SlugField()
    
    name_en = models.CharField(max_length=100)
    name_fr = models.CharField(max_length=100)
    desc_en = models.CharField(max_length=100)
    desc_fr = models.CharField(max_length=100)

    def __unicode__(self):
        return self.get_name()
    
class DietaryProfile(TimeStampedModel):
    history = AuditlogHistoryField()
    
    client = models.OneToOneField(Client)
    
    restrictions = models.ManyToManyField(FoodIngredient, through="Restriction")
    
    prep_mode = models.ManyToManyField(FoodPreparationMode, verbose_name=_('Preparation'))

class RestrictionReason(TranslatedModel):
    slug = models.SlugField(default='')
    name_en = models.CharField(max_length=100, default='')
    name_fr = models.CharField(max_length=100, default='')
    
    def __unicode__(self):
        return self.get_name()
    
class Restriction(TimeStampedModel):
    diet = models.ForeignKey(DietaryProfile)
    ingredient = models.ForeignKey(FoodIngredient)
    reason = models.ForeignKey(RestrictionReason)
    reason_info = models.CharField(_('Details'), max_length=50)
    
    def __unicode__(self):
        str = self.ingredient.get_name() + "(" + self.reason.get_name()
        if self.reason_info:
            str += " - " +self.reason_info
        str += ")"
        return str
    
    
auditlog.register(FoodCategory)
auditlog.register(FoodIngredient)

auditlog.register(DietaryProfile)

auditlog.register(Restriction)


