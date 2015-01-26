# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='DefaultMealSide',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('quantity', models.PositiveIntegerField(default=1)),
            ],
            options={
                'ordering': ('-modified', '-created'),
                'abstract': False,
                'get_latest_by': 'modified',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DeliveryDefault',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('day', models.CharField(default=b'ALL', max_length=3, choices=[(b'ALL', 'All days'), (b'MON', 'Monday'), (b'TUE', 'Tuesday'), (b'WED', 'Wednesday'), (b'FRI', 'Friday'), (b'SAT', 'Saturday')])),
                ('nb_meal', models.PositiveIntegerField(default=1)),
            ],
            options={
                'ordering': ('-modified', '-created'),
                'abstract': False,
                'get_latest_by': 'modified',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MealSide',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField()),
                ('name_en', models.CharField(max_length=30)),
                ('name_fr', models.CharField(max_length=30)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('type', models.CharField(default=b'O', max_length=1, choices=[(b'E', 'Episodic'), (b'O', 'Ongoing')])),
                ('start_date', models.DateField()),
                ('end_date', models.DateField(null=True)),
                ('monday', models.BooleanField(default=False)),
                ('tuesday', models.BooleanField(default=False)),
                ('wednesday', models.BooleanField(default=False)),
                ('friday', models.BooleanField(default=False)),
                ('saturday', models.BooleanField(default=False)),
                ('client', models.ForeignKey(to='clients.Client')),
            ],
            options={
                'ordering': ('-modified', '-created'),
                'abstract': False,
                'get_latest_by': 'modified',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OrderStop',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('reason_other', models.CharField(max_length=100, blank=True)),
                ('order', models.ForeignKey(to='orders.Order')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='StatusReasonCode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField()),
                ('desc_en', models.CharField(max_length=30)),
                ('desc_fr', models.CharField(max_length=30)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='orderstop',
            name='reason_code',
            field=models.ForeignKey(to='orders.StatusReasonCode'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='deliverydefault',
            name='order',
            field=models.ForeignKey(to='orders.Order'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='deliverydefault',
            name='sides',
            field=models.ManyToManyField(to='orders.MealSide', through='orders.DefaultMealSide'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='defaultmealside',
            name='delivery',
            field=models.ForeignKey(to='orders.DeliveryDefault'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='defaultmealside',
            name='side',
            field=models.ForeignKey(to='orders.MealSide'),
            preserve_default=True,
        ),
    ]
