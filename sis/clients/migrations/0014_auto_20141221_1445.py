# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0013_client_direct_contact'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='direct_contact',
            field=models.BooleanField(default=True),
        ),
    ]
