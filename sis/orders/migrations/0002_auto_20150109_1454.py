# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='orderstatus',
            name='type',
        ),
        migrations.AddField(
            model_name='order',
            name='type',
            field=models.CharField(default=b'O', max_length=1, choices=[(b'E', 'Episodic'), (b'O', 'Ongoing')]),
            preserve_default=True,
        ),
    ]
