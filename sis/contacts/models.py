#-*- coding: utf-8 -*-
import datetime
from datetime import date

from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.generic import GenericRelation
from django.core.urlresolvers import reverse_lazy
from django_extensions.db.models import TimeStampedModel, ActivatorModel
from django.utils.translation import ugettext_lazy as _
from django.utils.translation import pgettext_lazy
from django.utils import translation


from auditlog.registry import auditlog
from auditlog.models import AuditlogHistoryField
from diplomat.fields import LanguageChoiceField

from users.models import User

class ContactEntity(TimeStampedModel):
    class Meta:
        abstract = True

    def get_contact_info(self):
        if self.contact_info.count():
            return self.contact_info.all()[0]
        else:
            return None
    
class ContactInfo(models.Model):
    
    limit = models.Q(app_label = 'contacts', model = 'ContactEntity')
          
    content_type = models.ForeignKey(ContentType, limit_choices_to = limit)
    object_id = models.PositiveIntegerField(db_index=True)
    content_object = GenericForeignKey()
    
    # to enfore one-to-one relation
    class Meta:
        unique_together   = ('content_type', 'object_id')
        
    #owner = models.OneToOneField(ContactEntity)
    
    email_address = models.EmailField(blank=True, default='')

    def __unicode__(self):
        return self.email_address
    
    def get_address(self):
        return self.address_set.all()[0]
    
    def get_phones(self):
        return self.phone_set.all()
 
        
        
class Address(models.Model):
    history = AuditlogHistoryField()
    
#     limit = models.Q(app_label = 'contacts', model = 'Contact') | models.Q(app_label = 'contacts', model = 'Organization') | models.Q(app_label = 'clients', model = 'Client')
#          
#     content_type = models.ForeignKey(ContentType, limit_choices_to = limit)
#     object_id = models.PositiveIntegerField(db_index=True)
#     content_object = GenericForeignKey()
#
    contact_info = models.ForeignKey(ContactInfo)
    
    street = models.CharField(max_length=250, default='', verbose_name=_('Street name & number'))
    apt = models.CharField(max_length=10, blank=True, default='', verbose_name=_('Apt. #'))
    entry_code = models.CharField(max_length=5, blank=True, default='', verbose_name=_('Entry code'))
    zip_code = models.CharField(max_length=7)
    city = models.CharField(max_length=50, default=_('Montreal'))
    prov = models.CharField(max_length=30, default=_('Qc'))
    info = models.CharField(max_length=100, blank=True, verbose_name=_('Directions'))
    
    def __unicode__(self):
        return self.get_line_1() + " / " + self.get_line_2() + " / " +  self.get_line_3()
    
    def get_line_1(self):
        return self.street
    
    def get_line_2(self):
        if self.entry_code:
            line = _("Apt. %s (Entry code: %s)") % (self.apt, self.entry_code)
        else:
            line = _("Apt. %s (No entry code)") % (self.apt)
            
        return line
    
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
    
    contact_info = models.ForeignKey(ContactInfo)
    
    priority = models.PositiveIntegerField(blank=True, null=True)
    type = models.CharField(max_length=1, choices=PHONE_TYPE_CODES)
    number = models.CharField(max_length=20)
    extension = models.CharField(max_length=10, blank=True, default='')
    info = models.CharField(_('Additional information'), max_length=50, blank=True)
    
    def __unicode__(self):
        return self.number

    
class Organization(ContactEntity):
    
    name = models.CharField(max_length=100)
    contact_info = GenericRelation(ContactInfo)
    
    def __unicode__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse_lazy('org_update', kwargs={'pk':str(self.id)})
    
    
        

class Contact(ContactEntity):
        
    history = AuditlogHistoryField()
    
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    
    CLIENT = 'C'
    NEXT_OF_KIN='N'
    SOCIAL_WORKER='W'

    CONTACT_TYPE_CODES= (
        (NEXT_OF_KIN, _('Next of kin')),
        (SOCIAL_WORKER, _('Reference')),
        )
    contact_type = models.CharField(max_length=1, choices=CONTACT_TYPE_CODES, default=NEXT_OF_KIN)
    
    contact_info = GenericRelation(ContactInfo)
    
    work = models.ManyToManyField(Organization, through='OrganizationMember')
    
    @property
    def full_name(self):  
        return self.first_name + " " + self.last_name
    
    def __unicode__(self):
        return self.full_name
    
    def get_absolute_url(self):
        return reverse_lazy('contact_update', kwargs={'pk':str(self.id)})
    
    
    def get_organization(self):
        """
        Returns latest instance of OrganizationMember if there is one defined 
        """
        if (self.contact_type == self.NEXT_OF_KIN):
            return None
        else:
            return self.organizationmember_set.latest(field_name='activate_date')

    

class NextOfKin(Contact):
    class Meta:
        proxy = True
    
    #email_address optional
    #phones mandatory - min 1 max 3
    #adress mandatory - min 1 max 1
    #work optional
    
class SocialWorker(Contact):
    class Meta:
        proxy = True
    
    #email_address optional
    #phones mandatory - min 1 max 3
    #adress mandatory - min 1 max 1
    #work optional

class Position(models.Model):
    
    desc_en = models.CharField(max_length=30)
    desc_fr = models.CharField(max_length=30)

    def __unicode__(self):
        lg = translation.get_language()
        
        if lg == "en":
            return self.desc_en
        else:
            return self.desc_fr 
        
class OrganizationMember(ActivatorModel):
    organization = models.ForeignKey(Organization)
    social_worker = models.ForeignKey(Contact)
    position = models.ForeignKey(Position)
    
    def deactivate(self):
        self.deactivate_date(datetime.now())
        self.status = ActivatorModel.INACTIVE_STATUS
    
auditlog.register(NextOfKin)

auditlog.register(SocialWorker)

auditlog.register(Organization)

auditlog.register(Address)

auditlog.register(Phone)
