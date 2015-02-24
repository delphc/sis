# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0006_auto_20150223_1523'),
    ]

    operations = [
        migrations.AlterField(
            model_name='mealdefaultmeal',
            name='meal',
            field=models.ForeignKey(related_name=b'meals', to='orders.MealDefault'),
        ),
    ]
