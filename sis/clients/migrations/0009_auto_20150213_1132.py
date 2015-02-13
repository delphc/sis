# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0008_auto_20150213_1129'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='client',
            name='native_lg',
        ),
        migrations.AlterField(
            model_name='client',
            name='native_lang',
            field=models.ForeignKey(default=123, to='diplomat.ISOLanguage'),
        ),
    ]
