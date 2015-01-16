# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('address1', models.CharField(max_length=50)),
                ('address2', models.CharField(max_length=50, null=True, blank=True)),
                ('zip_code', models.CharField(max_length=7)),
                ('city', models.CharField(max_length=50)),
                ('prov', models.CharField(max_length=30)),
                ('info', models.CharField(max_length=100, null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('middle_name', models.CharField(max_length=50, null=True, blank=True)),
                ('email_address', models.EmailField(max_length=75)),
                ('create_date', models.DateTimeField(default=datetime.datetime.now, editable=False)),
                ('update_date', models.DateTimeField(default=datetime.datetime.now)),
                ('delete_date', models.DateTimeField(null=True, blank=True)),
                ('maiden_name', models.CharField(max_length=50)),
                ('birth_date', models.DateField()),
                ('gender', models.CharField(max_length=1, choices=[(b'F', 'Female'), (b'M', 'Male'), (b'U', 'Unknown')])),
                ('native_lang', models.CharField(max_length=2, verbose_name='Native Language', choices=[(b'EN', 'English'), (b'FR', 'French')])),
                ('com_lang', models.CharField(max_length=2, verbose_name='Language for communication', choices=[(b'EN', 'English'), (b'FR', 'French')])),
                ('cdif_exd', models.BooleanField(default=False, verbose_name='Expressive difficulty')),
                ('cdif_hoh', models.BooleanField(default=False, verbose_name='Hard of hearing')),
                ('directions', models.CharField(max_length=256, null=True, blank=True)),
                ('address', models.ForeignKey(to='clients.Address')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Phone',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('type', models.CharField(max_length=1, choices=[(b'H', 'Home'), (b'C', 'Cellular'), (b'W', 'Work')])),
                ('number', models.CharField(max_length=20)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='PhoneList',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField()),
                ('priority', models.PositiveIntegerField()),
                ('info', models.CharField(max_length=128, null=True, blank=True)),
                ('owner_type', models.ForeignKey(to='contenttypes.ContentType')),
                ('phone', models.ForeignKey(to='clients.Phone')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
