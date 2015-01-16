# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0014_auto_20141221_1445'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='direct_contact',
            field=models.BooleanField(default=True, choices=[(True, 'Yes'), (False, 'No')]),
        ),
    ]
