# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0019_auto_20141230_1344'),
    ]

    operations = [
        migrations.RenameField(
            model_name='client',
            old_name='contacts',
            new_name='relationships',
        ),
    ]
