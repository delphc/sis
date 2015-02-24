from django.db import models
from django.utils import translation

# Create your models here.
class PendedForm(models.Model):
    form_class = models.CharField(max_length=255)
    object_pk = models.PositiveIntegerField()

class PendedValue(models.Model):
    form = models.ForeignKey(PendedForm, related_name='data')
    name = models.CharField(max_length=255)
    value = models.TextField()
    
    
class TranslatedModel(models.Model):
    """
        Models inheriting of TranslatedModel can define couple of fields that hold english and french versions for the same item
        For instance, if you defined 2 fields name_en and name_fr to store english and french version of a name,
        you automatically get a method get_name that will return name_en or name_fr depending on current language in use
        
        Built-in methods get_name and get_description return fields named "name_en/name_fr" and "description_en/description_fr"
        
        If you need to call your field otherwise, you still can use the method get_translated_field( fieldrootname )
        Ex: for a couple of fields customname_en / customname_fr, simply call self.get_field_translated('custom_name')
        If your fields are named "name_en/name_fr" or "description_en/description"
        
    """
    
    class Meta:
        abstract = True
    
    def get_field_translated(self, field_name):
        
        lg = translation.get_language()
        
        if lg == "en":
            return getattr(self, field_name+'_en')
        else:
            return getattr(self, field_name+'_fr')
    
    def get_name(self):
        return self.get_field_translated('name') 
    
    def get_description(self):
        return self.get_field_translated('description') 