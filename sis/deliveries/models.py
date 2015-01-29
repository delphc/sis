from django.db import models

# Create your models here.
class Route(models.Model):
    name_en = models.CharField(max_length=50)
    name_fr = models.CharField(max_length=50)
    
    def __unicode__(self):
        lg = translation.get_language()
        
        if lg == "en":
            return self.name_en
        else:
            return self.name_fr

