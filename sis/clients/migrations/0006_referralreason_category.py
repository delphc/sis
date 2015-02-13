# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0005_auto_20150205_1519'),
    ]

    operations = [
        migrations.AddField(
            model_name='referralreason',
            name='category',
            field=models.CharField(default=b'AL', max_length=3, choices=[(b'AL', 'Loss of Autonomy'), (b'SI', 'Social isolation'), (b'FI', 'Food insecurity')]),
            preserve_default=True,
        ),
    ]
