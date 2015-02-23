# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_auto_20150219_1302'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mealside',
            name='slug',
        ),
        migrations.AddField(
            model_name='mealdefault',
            name='nb_meal',
            field=models.PositiveIntegerField(default=0),
            preserve_default=True,
        ),
    ]
