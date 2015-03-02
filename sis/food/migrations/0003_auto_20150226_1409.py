# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0002_auto_20150226_1350'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='restriction',
            name='reason',
        ),
        migrations.RemoveField(
            model_name='restriction',
            name='reason_info',
        ),
        migrations.AddField(
            model_name='restriction',
            name='allergy',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
    ]
