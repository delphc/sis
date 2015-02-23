# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0009_auto_20150205_1942'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='contactinfo',
            unique_together=set([('content_type', 'object_id')]),
        ),
    ]
