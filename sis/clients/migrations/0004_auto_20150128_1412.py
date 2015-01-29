# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0003_auto_20150120_1508'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='client',
            unique_together=set([('first_name', 'last_name')]),
        ),
    ]
