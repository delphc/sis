# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0005_auto_20150114_1044'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='deliverydefault',
            name='sides',
        ),
    ]
