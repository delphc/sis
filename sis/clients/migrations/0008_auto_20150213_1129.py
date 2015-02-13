# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('diplomat', '__first__'),
        ('clients', '0007_auto_20150212_2103'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='native_lg',
            field=models.ForeignKey(default=123, to='diplomat.ISOLanguage'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='client',
            name='cdif_anl',
            field=models.BooleanField(default=False, verbose_name='Illiterate'),
        ),
    ]
