# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0016_auto_20141221_1728'),
    ]

    operations = [
        migrations.AddField(
            model_name='client',
            name='referralNotes',
            field=models.TextField(default=b'', max_length=250, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='client',
            name='directions',
            field=models.TextField(default=b'', max_length=256, blank=True),
        ),
    ]
