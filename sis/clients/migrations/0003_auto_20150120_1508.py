# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0002_auto_20150120_1413'),
    ]

    operations = [
        migrations.AlterField(
            model_name='relationtype',
            name='contact_type',
            field=models.CharField(default=b'N', max_length=1, choices=[(b'N', 'Next of kin'), (b'W', 'Social worker')]),
        ),
    ]
