# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0013_auto_20150219_1302'),
    ]

    operations = [
        migrations.CreateModel(
            name='DietaryProfile',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('client', models.OneToOneField(to='clients.Client')),
            ],
            options={
                'ordering': ('-modified', '-created'),
                'abstract': False,
                'get_latest_by': 'modified',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FoodCategory',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('slug', models.SlugField(default=b'')),
                ('name_en', models.CharField(default=b'', max_length=100)),
                ('name_fr', models.CharField(default=b'', max_length=100)),
                ('description_en', models.CharField(default=b'', max_length=250, blank=True)),
                ('description_fr', models.CharField(default=b'', max_length=250, blank=True)),
                ('sort_order', models.PositiveIntegerField(default=0)),
            ],
            options={
                'ordering': ('-modified', '-created'),
                'abstract': False,
                'get_latest_by': 'modified',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FoodIngredient',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('slug', models.SlugField(default=b'')),
                ('name_en', models.CharField(default=b'', max_length=100)),
                ('name_fr', models.CharField(default=b'', max_length=100)),
                ('categories', models.ManyToManyField(to='food.FoodCategory')),
            ],
            options={
                'ordering': ('-modified', '-created'),
                'abstract': False,
                'get_latest_by': 'modified',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FoodPreparationMode',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField()),
                ('name_en', models.CharField(max_length=100)),
                ('name_fr', models.CharField(max_length=100)),
                ('desc_en', models.CharField(max_length=100)),
                ('desc_fr', models.CharField(max_length=100)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Restriction',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('reason_info', models.CharField(max_length=50, verbose_name='Details')),
                ('diet', models.ForeignKey(to='food.DietaryProfile')),
                ('ingredient', models.ForeignKey(to='food.FoodIngredient')),
            ],
            options={
                'ordering': ('-modified', '-created'),
                'abstract': False,
                'get_latest_by': 'modified',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RestrictionReason',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('slug', models.SlugField(default=b'')),
                ('name_en', models.CharField(default=b'', max_length=100)),
                ('name_fr', models.CharField(default=b'', max_length=100)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='restriction',
            name='reason',
            field=models.ForeignKey(to='food.RestrictionReason'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='dietaryprofile',
            name='prep_mode',
            field=models.ManyToManyField(to='food.FoodPreparationMode', verbose_name='Preparation'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='dietaryprofile',
            name='restrictions',
            field=models.ManyToManyField(to='food.FoodIngredient', through='food.Restriction'),
            preserve_default=True,
        ),
    ]
