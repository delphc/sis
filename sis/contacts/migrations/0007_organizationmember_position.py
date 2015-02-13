# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0006_auto_20150205_1519'),
    ]

    operations = [
        migrations.AddField(
            model_name='organizationmember',
            name='position',
            field=models.ForeignKey(default=b'', blank=True, to='contacts.Position'),
            preserve_default=True,
        ),
    ]
