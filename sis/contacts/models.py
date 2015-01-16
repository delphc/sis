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

from auditlog.registry import auditlog
from auditlog.models import AuditlogHistoryField
from diplomat.fields import LanguageChoiceField

from users.models import User


# Contact informations

class Address(models.Model):
    history = AuditlogHistoryField()
    
    limit = models.Q(app_label = 'contacts', model = 'Contact') | models.Q(app_label = 'contacts', model = 'Organization') | models.Q(app_label = 'clients', model = 'Client')
        
    content_type = models.ForeignKey(ContentType, limit_choices_to = limit)
    object_id = models.PositiveIntegerField(db_index=True)
    content_object = GenericForeignKey()
    
    street = models.CharField(max_length=250, default='', verbose_name=_('Street name & number'))
    apt = models.CharField(max_length=10, default='', verbose_name=_('Apt. #'))
    entry_code = models.CharField(max_length=5, default='', verbose_name=_('Entry code'))
    zip_code = models.CharField(max_length=7)
    city = models.CharField(max_length=50, default=_('Montreal'))
    prov = models.CharField(max_length=30, default=_('Qc'))
    info = models.CharField(max_length=100, blank=True, verbose_name=_('Additional information'))
    
    def __unicode__(self):
        return self.get_line_1() + " / " + self.get_line_2() + " / " +  self.get_line_3()
    
    def get_line_1(self):
        return self.street
    
    def get_line_2(self):
        return "Apt. "+self.apt+", Entry code. "+self.entry_code
    
    def get_line_3(self):
        return self.city+", "+self.prov+", "+self.zip_code
    

class Phone(models.Model):
    history = AuditlogHistoryField()

    HOME='H'
    CELL='C'
    WORK='W'
    HOME_DESC=pgettext_lazy("Phone type home", "Home")
    PHONE_TYPE_CODES = (
        (HOME, HOME_DESC),
        (CELL, _('Cellular')),
        (WORK, _('Work')),
    )
    
    limit = models.Q(app_label = 'contacts', model = 'Contact') | models.Q(app_label = 'contacts', model = 'Organization') | models.Q(app_label = 'clients', model = 'Client')
    
    content_type = models.ForeignKey(ContentType, limit_choices_to = limit)
    object_id = models.PositiveIntegerField(db_index=True)
    content_object = GenericForeignKey()
    
    
    priority = models.PositiveIntegerField(blank=True, null=True)
    type = models.CharField(max_length=1, choices=PHONE_TYPE_CODES)
    number = models.CharField(max_length=20)
    info = models.CharField(max_length=128, blank=True)
    
    def __unicode__(self):
        return self.number

class Person(TimeStampedModel):
    class Meta:
        abstract = True
        
    history = AuditlogHistoryField()
    
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    
    email_address = models.EmailField(blank=True)
    
    phones = GenericRelation(Phone, related_query_name='phones')
    address = GenericRelation(Address, related_query_name='address')

    def get_full_name(self):
        return self.first_name + " " + self.last_name

    def __unicode__(self):
        return self.get_full_name()
    
class Organization(TimeStampedModel):
    
    name = models.CharField(max_length=100)
    phones = GenericRelation(Phone, related_query_name='phones')
    address = GenericRelation(Address, related_query_name='address')
    
    def __unicode__(self):
        return self.name

class ContactType(models.Model):
    NEXT_OF_KIN='N'
    CASE_WORKER='W'

    CATEGORY_CODES= (
        (NEXT_OF_KIN, _('Next of kin')),
        (CASE_WORKER, _('Case worker')),
        )
    
    category = models.CharField(max_length=1, choices=CATEGORY_CODES, default=NEXT_OF_KIN)
    type_en = models.CharField(max_length=20)
    type_fr = models.CharField(max_length=20)
    
    def __unicode__(self):
        return self.type_en
    
class Contact(Person):
    
    category = models.CharField(max_length=1, choices=ContactType.CATEGORY_CODES, default=ContactType.NEXT_OF_KIN)
    type = models.ForeignKey(ContactType, blank=True, null=True)
    
    organization = models.ForeignKey(Organization, blank=True, null=True)
    
    referring = models.BooleanField(_('Referring contact'), default=False)
    emergency = models.BooleanField(_('Emergency contact'), default=False)
    
    def get_absolute_url(self):
        return reverse_lazy('contact_update', kwargs={'pk':str(self.id)})



auditlog.register(Contact)

auditlog.register(Organization)

auditlog.register(Address)

auditlog.register(Phone)
