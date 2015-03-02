# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0001_initial'),
    ]

    operations = [
        migrations.RenameField(
            model_name='foodpreparationmode',
            old_name='desc_en',
            new_name='description_en',
        ),
        migrations.RenameField(
            model_name='foodpreparationmode',
            old_name='desc_fr',
            new_name='description_fr',
        ),
    ]
