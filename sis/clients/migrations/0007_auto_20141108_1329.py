# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0006_phone_client'),
    ]

    operations = [
        migrations.AlterField(
            model_name='phone',
            name='client',
            field=models.ForeignKey(to='clients.Client'),
        ),
    ]
