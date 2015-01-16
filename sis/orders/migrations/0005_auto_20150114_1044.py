# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_auto_20150111_0933'),
    ]

    operations = [
        migrations.AlterField(
            model_name='orderstop',
            name='reason_other',
            field=models.CharField(max_length=100, blank=True),
        ),
    ]
