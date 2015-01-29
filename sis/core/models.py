from django.db import models

# Create your models here.
class PendedForm(models.Model):
    form_class = models.CharField(max_length=255)
    object_pk = models.PositiveIntegerField()

class PendedValue(models.Model):
    form = models.ForeignKey(PendedForm, related_name='data')
    name = models.CharField(max_length=255)
    value = models.TextField()