# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0004_auto_20150120_1620'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organizationmember',
            name='end_date',
            field=models.DateField(null=True, blank=True),
        ),
    ]
