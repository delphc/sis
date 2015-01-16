# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0012_auto_20141221_1418'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='direct_contact',
            field=models.BooleanField(default=True, verbose_name='Possible to contact client directly ?'),
            preserve_default=True,
        ),
    ]
