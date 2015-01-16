# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0004_auto_20150103_0926'),
    ]

    operations = [
        migrations.RenameField(
            model_name='contacttype',
            old_name='contact_type',
            new_name='category',
        ),
    ]
