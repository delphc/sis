# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0010_auto_20141110_0748'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='address',
            name='address',
        ),
        migrations.AddField(
            model_name='address',
            name='apt',
            field=models.CharField(default=b'', max_length=10, verbose_name='Apt. #'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='address',
            name='entry_code',
            field=models.CharField(default=b'', max_length=5, verbose_name='Entry code'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='address',
            name='street',
            field=models.CharField(default=b'', max_length=250, verbose_name='Street name & number'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='address',
            name='info',
            field=models.CharField(max_length=100, verbose_name='Additional information', blank=True),
        ),
        migrations.AlterField(
            model_name='client',
            name='gender',
            field=models.CharField(default=b'U', max_length=1, choices=[(b'F', b'female'), (b'M', b'male'), (b'U', b'question')]),
        ),
        migrations.AlterField(
            model_name='client',
            name='native_lang',
            field=models.CharField(max_length=2, verbose_name='Native language', choices=[(b'EN', 'English'), (b'FR', 'French')]),
        ),
    ]
