# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0009_auto_20150213_1132'),
    ]

    operations = [
        migrations.RenameField(
            model_name='relationship',
            old_name='type',
            new_name='rel_type',
        ),
        migrations.AddField(
            model_name='relationship',
            name='contact_type',
            field=models.CharField(default=b'N', max_length=1, choices=[(b'N', 'Next of kin'), (b'W', 'Reference')]),
            preserve_default=True,
        ),
    ]
