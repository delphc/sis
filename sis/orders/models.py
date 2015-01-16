#-*- coding: utf-8 -*-
import datetime
from datetime import date

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.generic import GenericRelation
from django.core.urlresolvers import reverse_lazy
from django_extensions.db.models import TimeStampedModel
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy
from django.utils import translation


from auditlog.registry import auditlog
from auditlog.models import AuditlogHistoryField
from diplomat.fields import LanguageChoiceField

from clients.models import Client

# Contact informations

class StatusReasonCode(models.Model):
    OTHER = "other"
    
    slug = models.SlugField()
    desc_en = models.CharField(max_length=30)
    desc_fr = models.CharField(max_length=30)

    def __unicode__(self):
        lg = translation.get_language()
        
        if lg == "en":
            return self.desc_en
        else:
            return self.desc_fr
        

# HOW TO ADD A NEW DELIVERY DAY
# ----------------------------------
# 1. add a BooleanField to Order model (use monday field as example)
# 2. add a choice to DeliveryDefault.DELIVERY_DAYS 
# 3. add field to OrderForm (see orders/forms.py
# 4. add field to templates/clients/client_order.html
class Order(TimeStampedModel):
    history = AuditlogHistoryField()
    
    client = models.ForeignKey(Client)
    EPISODIC = 'E'
    ONGOING = 'O'
    ORDER_TYPES = (
        (EPISODIC, _('Episodic')),
        (ONGOING, _('Ongoing')),
        )
    type = models.CharField(max_length=1, choices=ORDER_TYPES, default=ONGOING)
    
    start_date = models.DateField()
    end_date = models.DateField(null=True)
    
    STATUS_ACTIVE = _('Active')
    STATUS_STOPPED = _('Stopped')
    STATUS_INACTIVE = _('Inactive')
    
    monday = models.BooleanField(default=False)
    tuesday = models.BooleanField(default=False)
    wednesday = models.BooleanField(default=False)
    friday = models.BooleanField(default=False)
    saturday = models.BooleanField(default=False)
     
    def __unicode__(self):
        return _(u'%(status)s / %(start)s') % {'status':self.get_current_status(), 'start': self.start_date }
    
    def is_active(self):
        return self.get_current_status() == self.STATUS_ACTIVE
    
    def is_stopped(self):
        return self.get_current_status() == self.STATUS_STOPPED
    
    def is_stopped(self):
        return self.get_current_status() == self.STATUS_INACTIVE
    
    def get_current_status(self):
        if (self.end_date != None):
            return self.STATUS_ACTIVE
        
        stops = self.orderstop_set.filter(
                    start_date__lt=datetime.datetime.now()).filter(
                    end_date__gt=datetime.datetime.now())
                    
        
        if (stops.count() != 0):
            return self.STATUS_STOPPED
        
        return self.STATUS_ACTIVE   
    
    def has_stop(self):
        stops = self.orderstop_set.filter(
                    end_date__gte=datetime.datetime.now())
        if stops.count() != 0:
            return True
        else:
            return False

    def get_stop(self):
        return self.orderstop_set.filter(
                    end_date__gte=datetime.datetime.now()).order_by('start_date').first()
                    
    def get_delivery_default(self):
        return self.deliverydefault_set.get(day=DeliveryDefault.ALL)

class OrderStop(models.Model):
    
    order = models.ForeignKey(Order)
    start_date = models.DateField()
    end_date = models.DateField()
    reason_code = models.ForeignKey(StatusReasonCode)
    reason_other = models.CharField(max_length=100, blank=True)
    
    def single_day(self):
        self.end_date=self.start_date
    
    def is_single_day(self):  
        return self.end_date == self.start_date
    
    def clean(self):       
        if (self.reason_code.slug == StatusReasonCode.OTHER and self.reason_other == ''):
            raise ValidationError({'reason_other': _('You must precise the reason for this change of status')})
        
    def display_dates(self):
        single_day = self.is_single_day()
        if single_day:
            return _(u'Order stopped on %(start)s') % { 'start' : self.start_date }
        else:
            return _(u'Order stopped from %(start)s to %(end)s') % { 'start' : self.start_date, 'end': self.end_date }
    
    def display_reason(self):
        lg = translation.get_language()
        if self.reason_other != '':
            return self.reason_other
        if lg == "en":
            return self.reason_code.desc_en
        else:
            return self.reason_code.desc_fr
        
    
      
class MealSide(models.Model):
    slug = models.SlugField()
    name_en = models.CharField(max_length=30)
    name_fr = models.CharField(max_length=30)
    
    def __unicode__(self):
        lg = translation.get_language()
        if lg == "en":
            return self.name_en
        else:
            return self.name_fr
         
    
class DeliveryDefault(TimeStampedModel):
    order = models.ForeignKey(Order)
    
    ALL = 'ALL'
    MON = 'MON'
    TUE = 'TUE'
    WED = 'WED'
    FRI = 'FRI'
    SAT = 'SAT'
    
    DELIVERY_DAYS = (
        (ALL, _('All days')),
        (MON, _('Monday')),
        (TUE, _('Tuesday')),
        (WED, _('Wednesday')),
        (FRI, _('Friday')),
        (SAT, _('Saturday')),
    )
    day = models.CharField(max_length=3, choices=DELIVERY_DAYS, default=ALL)
    
    nb_meal = models.PositiveIntegerField(default=1)

    sides = models.ManyToManyField(MealSide, through='DefaultMealSide')
    
    def __unicode__(self):
        return self.day
    

class DefaultMealSide(TimeStampedModel):
    delivery = models.ForeignKey(DeliveryDefault)
    side = models.ForeignKey(MealSide)
    quantity = models.PositiveIntegerField(default=1)
