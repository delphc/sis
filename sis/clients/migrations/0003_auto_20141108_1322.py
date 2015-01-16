# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0002_client_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='phonelist',
            name='owner_type',
        ),
        migrations.RemoveField(
            model_name='phonelist',
            name='phone',
        ),
        migrations.DeleteModel(
            name='PhoneList',
        ),
        migrations.RemoveField(
            model_name='client',
            name='address',
        ),
        migrations.AddField(
            model_name='phone',
            name='info',
            field=models.CharField(max_length=128, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='phone',
            name='priority',
            field=models.PositiveIntegerField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
