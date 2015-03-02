# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0004_auto_20150227_0848'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='foodingredient',
            options={},
        ),
        migrations.RemoveField(
            model_name='foodingredient',
            name='created',
        ),
        migrations.RemoveField(
            model_name='foodingredient',
            name='modified',
        ),
    ]
