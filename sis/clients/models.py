#-*- coding: utf-8 -*-
import datetime
from datetime import date

from django.db import models
from django.contrib.contenttypes.generic import GenericRelation
from django.core.urlresolvers import reverse_lazy
from django_extensions.db.models import TimeStampedModel
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy

from auditlog.registry import auditlog
from auditlog.models import AuditlogHistoryField
from diplomat.fields import LanguageChoiceField

from contacts.models import Address, ContactEntity, Contact, ContactInfo, SocialWorker
from users.models import User


# Contact informations

class ReferralReason(models.Model):
    reason_fr = models.CharField(max_length=100)
    reason_en = models.CharField(max_length=100)
    
    
class Client(ContactEntity):
        
    FEMALE='F'
    MALE='M'
    UNKNOWN='U'
    GENDER_CODES = (
        (FEMALE, _('Female')),
        (MALE, _('Male')),
        (UNKNOWN, _('Unknown gender')),
    )
    
    
    PENDING='P'
    ACTIVE='A'
    INACTIVE='I'

    STATUS_CODES= (
        (PENDING, _('Pending')),
        (ACTIVE, _('Active')),
        (INACTIVE, _('Inactive')),
        )
    
    
    gender = models.CharField(max_length=1, choices=GENDER_CODES, default=UNKNOWN)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    middle_name = models.CharField(max_length=50, blank=True)
    
    class Meta:
        unique_together = (('first_name', 'last_name'),)
     
    maiden_name = models.CharField(max_length=50, blank=True)
     
    birth_date  = models.DateField()
        
    status = models.CharField(max_length=1, choices=STATUS_CODES, default=PENDING)
    
    ENGLISH='EN'
    FRENCH='FR'
    BOTH='EF'
    LANGUAGE_CODES = (
        (ENGLISH, _('English')),
        (FRENCH, _('French')),
        (BOTH, _('English/French')),
    )
    #Native language
    #native_lang = LanguageChoiceField()
    native_lang =  models.CharField(_('Native language'),max_length=2, choices=LANGUAGE_CODES)
    #Preferred language for communication
    com_lang = models.CharField(_('Language for communication'),max_length=2, choices=LANGUAGE_CODES)
    # ** Behavioral issues impacting communication**
    #Expression difficulty
    cdif_exd = models.BooleanField(_('Expressive difficulty'), default=False)
    #Hard of hearing
    cdif_hoh = models.BooleanField(_('Hard of hearing'), default=False)
    # Analphabete
    cdif_anl = models.BooleanField(_('Analphabete'), default=False)
    # Cognitive loss
    cdif_cog = models.BooleanField(_('Cognitive loss'), default=False)
    
    YES_NO_CHOICES = (
        (True, _('Yes')),
        (False, _('No')),
    )
    direct_contact = models.BooleanField(default=True, choices=YES_NO_CHOICES,)
    contact_info = GenericRelation(ContactInfo)
    relationships = models.ManyToManyField(Contact, through='Relationship')
    
    directions = models.TextField(max_length=256, blank=True, default='')
    
    #TODO - need to figure out how to set nullable FK
    #main_client = models.ForeignKey('self', null=True)
    
    def __unicode__(self): # Python 3: def __str__(self):
        return self.get_full_name()
    
    def get_absolute_url(self):
        if self.status == self.PENDING:
            return reverse_lazy('client_setup_resume', kwargs={'pk':str(self.id)})
        else:
            return reverse_lazy('client_profile', kwargs={'tab': 'id', 'pk':str(self.id)})

    def get_gender_icon(self):
        if self.gender == self.MALE:
            return 'fa-male'
        elif self.gender == self.FEMALE:
            return 'fa-female'
        else:
            return 'fa-question'
        
#     def get_gender_display(self):
#         if self.gender == MALE:
#             return GENDER_CODES.MALE
#         elif self.gender == FEMALE:
#             return GENDER_CODES.FEMALE
#         else:
#             return GENDER_CODES.UNKNOWN
        
    def get_full_name(self):
        short_middle_name = ""
        if self.middle_name:
            short_middle_name = self.middle_name[0]+". "
        return self.first_name + " " + short_middle_name + self.last_name
    
   
    def get_age(self):
        today = date.today()
        return today.year - self.birth_date.year - ((today.month, today.day) < (self.birth_date.month, self.birth_date.day))
   
    def get_order(self):
        if self.order_set.count() == 0:
            return None
        else:
            return self.order_set.latest(field_name='start_date')
        
    def get_referral(self):
        if self.referral_set.count() == 0:
            return None
        else:
            return self.referral_set.latest(field_name='ref_date')

# class ClientProfile(models.Model):   
#     client = models.OneToOneField(Client)
#     
     
class Referral(models.Model):
    client = models.ForeignKey(Client)
    contact = models.ForeignKey(Contact)
    ref_date = models.DateField()
    reasons = models.ManyToManyField(ReferralReason)
    notes = models.TextField(max_length=250, blank=True, default='')

class RelationType(models.Model):
    
    
    contact_type = models.CharField(max_length=1, choices=Contact.CONTACT_TYPE_CODES, default=Contact.NEXT_OF_KIN)
    type_en = models.CharField(max_length=20)
    type_fr = models.CharField(max_length=20)
    
    def __unicode__(self):
        return self.type_en
    
class Relationship(TimeStampedModel):
    client = models.ForeignKey(Client)
    contact = models.ForeignKey(Contact)
    type = models.ForeignKey(RelationType, blank=True, null=True)

    emergency = models.BooleanField(_('Emergency contact'), default=False)
    follow_up = models.BooleanField(_('Follow-up'), default=False)
    info = models.CharField(max_length=100, blank=True, verbose_name=_('Additional information'))

    
auditlog.register(Client)
auditlog.register(Relationship)

