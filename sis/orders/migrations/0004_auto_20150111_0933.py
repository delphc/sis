# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_auto_20150110_1414'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderStop',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('reason_other', models.CharField(max_length=100)),
                ('order', models.ForeignKey(to='orders.Order')),
                ('reason_code', models.ForeignKey(to='orders.StatusReasonCode')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='orderstatus',
            name='order',
        ),
        migrations.RemoveField(
            model_name='orderstatus',
            name='reason_code',
        ),
        migrations.DeleteModel(
            name='OrderStatus',
        ),
        migrations.AddField(
            model_name='order',
            name='end_date',
            field=models.DateField(null=True),
            preserve_default=True,
        ),
    ]
