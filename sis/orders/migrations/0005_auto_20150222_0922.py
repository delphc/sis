# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0004_auto_20150219_1508'),
    ]

    operations = [
        migrations.AddField(
            model_name='serviceday',
            name='slug',
            field=models.SlugField(default=b'', unique=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='order',
            name='days',
            field=models.ManyToManyField(to=b'orders.ServiceDay', verbose_name='Service days'),
        ),
        migrations.AlterField(
            model_name='order',
            name='type',
            field=models.CharField(default=b'O', max_length=1, verbose_name='Service type', choices=[(b'E', 'Episodic'), (b'O', 'Ongoing')]),
        ),
    ]
