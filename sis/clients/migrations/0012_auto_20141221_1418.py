# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0011_auto_20141120_1932'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='cdif_anl',
            field=models.BooleanField(default=False, verbose_name='Analphabete'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='client',
            name='cdif_cog',
            field=models.BooleanField(default=False, verbose_name='Cognitive loss'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='client',
            name='com_lang',
            field=models.CharField(max_length=2, verbose_name='Language for communication', choices=[(b'EN', 'English'), (b'FR', 'French'), (b'E/F', 'English/French')]),
        ),
        migrations.AlterField(
            model_name='client',
            name='gender',
            field=models.CharField(default=b'U', max_length=1, choices=[(b'F', 'Female'), (b'M', 'Male'), (b'U', 'Unknown gender')]),
        ),
        migrations.AlterField(
            model_name='client',
            name='native_lang',
            field=models.CharField(max_length=2, verbose_name='Native language', choices=[(b'EN', 'English'), (b'FR', 'French'), (b'E/F', 'English/French')]),
        ),
    ]
