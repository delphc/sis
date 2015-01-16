# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0005_auto_20141108_1328'),
    ]

    operations = [
        migrations.AddField(
            model_name='phone',
            name='client',
            field=models.ForeignKey(blank=True, to='clients.Client', null=True),
            preserve_default=True,
        ),
    ]
