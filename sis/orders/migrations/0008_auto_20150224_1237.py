# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0007_auto_20150224_1134'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='serviceday',
            options={'ordering': ['sort_order']},
        ),
        migrations.RenameField(
            model_name='serviceday',
            old_name='position',
            new_name='sort_order',
        ),
        migrations.AlterUniqueTogether(
            name='serviceday',
            unique_together=set([('service_type', 'sort_order')]),
        ),
    ]
