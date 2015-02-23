# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MealDefault',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('meal_type', models.CharField(default=b'R', max_length=1, choices=[(b'H', 'Half'), (b'R', 'Regular')])),
            ],
            options={
                'ordering': ('-modified', '-created'),
                'abstract': False,
                'get_latest_by': 'modified',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MealDefaultSide',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('quantity', models.PositiveIntegerField(default=1)),
                ('meal', models.ForeignKey(to='orders.MealDefault')),
                ('side', models.ForeignKey(to='orders.MealSide')),
            ],
            options={
                'ordering': ('-modified', '-created'),
                'abstract': False,
                'get_latest_by': 'modified',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OrderStatusChange',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('date', models.DateField()),
                ('order', models.ForeignKey(to='orders.Order')),
                ('reason_code', models.ForeignKey(to='orders.StatusReasonCode')),
            ],
            options={
                'ordering': ('-modified', '-created'),
                'abstract': False,
                'get_latest_by': 'modified',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ServiceDay',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name_en', models.CharField(max_length=30)),
                ('name_fr', models.CharField(max_length=30)),
                ('service_type', models.CharField(default=b'M', max_length=1, choices=[(b'M', 'Meal')])),
                ('active', models.BooleanField(default=False)),
                ('position', models.PositiveIntegerField()),
            ],
            options={
                'ordering': ['position'],
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='defaultmealside',
            name='delivery',
        ),
        migrations.RemoveField(
            model_name='defaultmealside',
            name='side',
        ),
        migrations.RemoveField(
            model_name='deliverydefault',
            name='order',
        ),
        migrations.RemoveField(
            model_name='deliverydefault',
            name='sides',
        ),
        migrations.DeleteModel(
            name='DefaultMealSide',
        ),
        migrations.DeleteModel(
            name='DeliveryDefault',
        ),
        migrations.RemoveField(
            model_name='orderstop',
            name='order',
        ),
        migrations.RemoveField(
            model_name='orderstop',
            name='reason_code',
        ),
        migrations.DeleteModel(
            name='OrderStop',
        ),
        migrations.AlterUniqueTogether(
            name='serviceday',
            unique_together=set([('service_type', 'position')]),
        ),
        migrations.AddField(
            model_name='mealdefault',
            name='day',
            field=models.ForeignKey(to='orders.ServiceDay'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mealdefault',
            name='sides',
            field=models.ManyToManyField(to='orders.MealSide', through='orders.MealDefaultSide'),
            preserve_default=True,
        ),
        migrations.RemoveField(
            model_name='order',
            name='end_date',
        ),
        migrations.RemoveField(
            model_name='order',
            name='friday',
        ),
        migrations.RemoveField(
            model_name='order',
            name='monday',
        ),
        migrations.RemoveField(
            model_name='order',
            name='saturday',
        ),
        migrations.RemoveField(
            model_name='order',
            name='start_date',
        ),
        migrations.RemoveField(
            model_name='order',
            name='tuesday',
        ),
        migrations.RemoveField(
            model_name='order',
            name='wednesday',
        ),
        migrations.AddField(
            model_name='order',
            name='days',
            field=models.ManyToManyField(to='orders.ServiceDay'),
            preserve_default=True,
        ),
    ]
