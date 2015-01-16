# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0003_auto_20150103_0919'),
    ]

    operations = [
        migrations.AddField(
            model_name='contact',
            name='emergency',
            field=models.BooleanField(default=False, verbose_name='Emergency contact'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='contact',
            name='referring',
            field=models.BooleanField(default=False, verbose_name='Referring contact'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='contact',
            name='type',
            field=models.ForeignKey(blank=True, to='contacts.ContactType', null=True),
            preserve_default=True,
        ),
    ]
