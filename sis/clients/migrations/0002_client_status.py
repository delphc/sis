# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='status',
            field=models.CharField(default=b'P', max_length=1, choices=[(b'P', 'Pending'), (b'A', 'Active'), (b'I', 'Inactive')]),
            preserve_default=True,
        ),
    ]
