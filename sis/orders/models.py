#-*- coding: utf-8 -*-
import datetime
import sys
from datetime import date

from django.db import models
from django.db.models import Q
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

from core.models import TranslatedModel
from clients.models import Client

# Contact informations

class StatusReasonCode(TranslatedModel):
    OTHER = "other"
    
    slug = models.SlugField()
    desc_en = models.CharField(max_length=30)
    desc_fr = models.CharField(max_length=30)

    def __unicode__(self):
        return self.get_translated_field('desc')

class ServiceDayManager(models.Manager):
    
    def get_meal_service_days(self):
        return super(ServiceDayManager, self).get_queryset().filter(service_type=ServiceDay.MEAL).filter(active=True)
    
    def get_days_for_meal_defaults(self):
        """
            Returns active service days + 'everyday' service day
            in order to build forms to get meal defaults
        """
        return super(ServiceDayManager, self).filter(
            Q(service_type=ServiceDay.MEAL),
            Q(active=True) | Q(slug=ServiceDay.SLUG_EVERYDAY)
            )
    
    def get_meal_service_everyday(self):
        return super(ServiceDayManager, self).filter(service_type=ServiceDay.MEAL).get(slug=ServiceDay.SLUG_EVERYDAY)
    
class ServiceDay(TranslatedModel):
    SLUG_EVERYDAY="everyday_meal" # DO NOT CHANGE
    MEAL='M'
    SERVICE_TYPE = (
                  (MEAL, _('Meal')),
                  )
    slug = models.SlugField(unique=True, default='')
    name_en = models.CharField(max_length=30)
    name_fr = models.CharField(max_length=30)
    service_type = models.CharField(max_length=1, choices=SERVICE_TYPE, default=MEAL)
    active = models.BooleanField(default=False)
    sort_order = models.PositiveIntegerField()
    
    objects = ServiceDayManager()
    
    class Meta:
        unique_together = ("service_type", "sort_order")
        ordering = ['sort_order']
        
    def __unicode__(self):
        return self.get_name()

class OrderManager(models.Manager):
    def get_latest_order_for_client(self, client):
        qs = OrderStatusChange.objects.filter(order__client=client).order_by("-date")
                
        latest_entry = list(qs[:1])
        if latest_entry:
            return latest_entry[0].order
        else:
            return None
        
class Order(TimeStampedModel):
    objects = OrderManager()
    history = AuditlogHistoryField()
    
    client = models.ForeignKey(Client)
    
    EPISODIC = 'E'
    ONGOING = 'O'
    ORDER_TYPES = (
        (EPISODIC, _('Episodic')),
        (ONGOING, _('Ongoing')),
        )
    type = models.CharField(_("Service type"),max_length=1, choices=ORDER_TYPES, default=ONGOING)
    
    #start_date = models.DateField()
    #end_date = models.DateField(null=True)
    
    STATUS_ACTIVE = _('Active')
    STATUS_STOPPED = _('Stopped')
    STATUS_INACTIVE = _('Inactive')
    
    days = models.ManyToManyField(ServiceDay, verbose_name=_("Service days"), limit_choices_to={'active': True, 'service_type':ServiceDay.MEAL})
    
    
    DEFAULTS_TYPE_EVERYDAY= { 'code' :'A', 'display':_('Same for everyday') }
    DEFAULTS_TYPE_DAY= { 'code' :'D', 'display':_('Day-specific') }
    DEFAULTS_TYPE_CHOICES = (
                             (DEFAULTS_TYPE_EVERYDAY['code'], DEFAULTS_TYPE_EVERYDAY['display']),
                             (DEFAULTS_TYPE_DAY['code'], DEFAULTS_TYPE_DAY['display'])
                             )
    
    
    def __unicode__(self):
        return _(u'%(status)s') % {'status':self.get_current_status_code() }
    
    def is_pending(self):
        return self.get_current_status_code() == OrderStatusChange.PENDING
    
    def is_active(self):
        return self.get_current_status_code() == OrderStatusChange.ACTIVE
    
    def is_stopped(self):
        return self.get_current_status_code() == OrderStatusChange.STOPPED
    
    def is_deactivated(self):
        return self.get_current_status_code() == OrderStatusChange.DEACTIVATED
    
    def get_current_status_code(self):
        return self.get_current_status()[0]
    
    def get_current_status_display(self):
        return self.get_current_status()[1]

    def get_current_status(self):
        qs = self.status.filter(date__lte=date.today()).order_by('-date')
         
        active_entry = list(qs[:1])
        if active_entry:
            return OrderStatusChange.ORDER_STATUS[active_entry[0].type]
        else:
            return OrderStatusChange.ORDER_STATUS[OrderStatusChange.NO_ENTRY]
    
    def _get_meal_defaults_type(self):
        # default is meal_defaults_type
        if not hasattr(self, 'meal_defaults_type'):
            print >>sys.stderr, '***  INIT meal_defaults_type ***'
            mealdefaults = self.get_meal_defaults()
            if mealdefaults.count() == 1:
                mealdefault = mealdefaults[0]
                if mealdefault.day.slug == ServiceDay.SLUG_EVERYDAY:
                    self.meal_defaults_type = self.DEFAULTS_TYPE_EVERYDAY
                else:
                    self.meal_defaults_type = self.DEFAULTS_TYPE_DAY 
            else:
                self.meal_defaults_type = self.DEFAULTS_TYPE_DAY
        else:
            print >>sys.stderr, '***  ALREADY SET meal_defaults_type ***'
                    
        return self.meal_defaults_type
    
    def get_meal_defaults_type_display(self):
        return self._get_meal_defaults_type()['display']
    
    def get_meal_defaults_type_code(self):
        return self._get_meal_defaults_type()['code']
            
    def get_meal_defaults(self):
        return self.mealdefault_set.order_by('day__sort_order').all()
    
    
    
#     
#     def has_stop(self):
#         stops = self.orderstop_set.filter(
#                     end_date__gte=datetime.datetime.now())
#         if stops.count() != 0:
#             return True
#         else:
#             return False
# 
#     def get_stop(self):
#         return self.orderstop_set.filter(
#                     end_date__gte=datetime.datetime.now()).order_by('start_date').first()
#                     
#     def get_delivery_default(self):
#         return self.deliverydefault_set.get(day=DeliveryDefault.ALL)


        
class OrderStatusChange(TimeStampedModel):
    order = models.ForeignKey(Order, related_name='status')
    
    ACTIVATE = 'A' # initial start
    STOP = 'P'  # temporary stop
    RESUME = 'R' # resume after temporary stop
    END = 'E' # final stop (order cannot be reactivated past this status change
    CHANGE_TYPES = (
                    (ACTIVATE,_('Activate')),
                    (STOP, _('Stop')),
                    (RESUME, _('Resume')),
                    (END, _('Stop'))
                    )
    # Order status corresponing to the current OrderStatusChange active (ie. date < today)
    NO_ENTRY='NO_ENTRY'
    PENDING='P'
    ACTIVE='A'
    STOPPED='S'
    DEACTIVATED='D'
    ORDER_STATUS = {
                    NO_ENTRY: (PENDING, _('Pending')),
                    ACTIVATE: (ACTIVE, _('Active')),
                    STOP: (STOPPED, _('Stopped')),
                    RESUME: (ACTIVE, _('Active')),
                    END: (DEACTIVATED, _('Deactivated'))
                    }
    type = models.CharField(max_length=1, choices=CHANGE_TYPES, default=ACTIVATE)
    date = models.DateField()
    reason_code = models.ForeignKey(StatusReasonCode)
    
    class Meta:
        unique_together = ('order', 'type', 'date')
        ordering = ['date']
    
      
class MealSide(models.Model):
    name_en = models.CharField(max_length=30)
    name_fr = models.CharField(max_length=30)
    
    def __unicode__(self):
        lg = translation.get_language()
        if lg == "en":
            return self.name_en
        else:
            return self.name_fr
         
class MealDefault(TimeStampedModel):
    order = models.ForeignKey(Order, default='')
    day = models.ForeignKey(ServiceDay, limit_choices_to={'active': True, 'service_type':ServiceDay.MEAL})
    
    sides = models.ManyToManyField(MealSide, through='MealDefaultSide')
    
    def __unicode__(self):
        return self.day.name_en

class MealDefaultMeal(TimeStampedModel):   
    meal = models.ForeignKey(MealDefault, related_name='meals')
    
    HALF = 'H'
    REG = 'R'
    MEAL_SIZES = (
        (HALF, _('Half')),
        (REG, _('Regular')),
    )
    size = models.CharField(max_length=1, choices=MEAL_SIZES, default=REG)
    
    quantity = models.PositiveIntegerField(default=0)
    
class MealDefaultSide(TimeStampedModel):
    meal = models.ForeignKey(MealDefault)
    side = models.ForeignKey(MealSide)
    quantity = models.PositiveIntegerField(default=1)
    
