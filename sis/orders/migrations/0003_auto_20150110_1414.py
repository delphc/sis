# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0002_auto_20150109_1454'),
    ]

    operations = [
        migrations.RenameField(
            model_name='statusreasoncode',
            old_name='code_en',
            new_name='desc_en',
        ),
        migrations.RenameField(
            model_name='statusreasoncode',
            old_name='code_fr',
            new_name='desc_fr',
        ),
    ]
