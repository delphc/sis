# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0005_auto_20150222_0922'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='orderstatuschange',
            options={'ordering': ['date']},
        ),
        migrations.AddField(
            model_name='orderstatuschange',
            name='type',
            field=models.CharField(default=b'A', max_length=1, choices=[(b'A', 'Activate'), (b'P', 'Stop'), (b'R', 'Resume'), (b'E', 'Stop')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='orderstatuschange',
            name='order',
            field=models.ForeignKey(related_name=b'status', to='orders.Order'),
        ),
        migrations.AlterUniqueTogether(
            name='orderstatuschange',
            unique_together=set([('order', 'type', 'date')]),
        ),
    ]
