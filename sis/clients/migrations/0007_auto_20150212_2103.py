# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0006_referralreason_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='client',
            name='native_lang',
            field=models.CharField(max_length=20, verbose_name='Native language'),
        ),
    ]
