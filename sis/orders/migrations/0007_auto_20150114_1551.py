# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0006_remove_deliverydefault_sides'),
    ]

    operations = [
        migrations.CreateModel(
            name='DefaultMealSide',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('delivery', models.ForeignKey(to='orders.DeliveryDefault')),
                ('side', models.ForeignKey(to='orders.MealSide')),
            ],
            options={
                'ordering': ('-modified', '-created'),
                'abstract': False,
                'get_latest_by': 'modified',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='deliverydefault',
            name='sides',
            field=models.ManyToManyField(to='orders.MealSide', through='orders.DefaultMealSide'),
            preserve_default=True,
        ),
    ]
