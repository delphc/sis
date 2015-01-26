# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('contenttypes', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('street', models.CharField(default=b'', max_length=250, verbose_name='Street name & number')),
                ('apt', models.CharField(default=b'', max_length=10, verbose_name='Apt. #')),
                ('entry_code', models.CharField(default=b'', max_length=5, verbose_name='Entry code')),
                ('zip_code', models.CharField(max_length=7)),
                ('city', models.CharField(default='Montreal', max_length=50)),
                ('prov', models.CharField(default='Qc', max_length=30)),
                ('info', models.CharField(max_length=100, verbose_name='Directions', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('contact_type', models.CharField(default=b'N', max_length=1, choices=[(b'N', 'Next of kin'), (b'W', 'Case worker')])),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ContactInfo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('object_id', models.PositiveIntegerField(db_index=True)),
                ('email_address', models.EmailField(max_length=75, blank=True)),
                ('content_type', models.ForeignKey(to='contenttypes.ContentType')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Organization',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('name', models.CharField(max_length=100)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OrganizationMember',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('position', models.CharField(max_length=20)),
                ('organization', models.ForeignKey(to='contacts.Organization')),
                ('social_worker', models.ForeignKey(to='contacts.Contact')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Phone',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('priority', models.PositiveIntegerField(null=True, blank=True)),
                ('type', models.CharField(max_length=1, choices=[(b'H', 'Home'), (b'C', 'Cellular'), (b'W', 'Work')])),
                ('number', models.CharField(max_length=20)),
                ('extension', models.CharField(default=b'', max_length=10, blank=True)),
                ('info', models.CharField(max_length=50, verbose_name='Additional information', blank=True)),
                ('contact_info', models.ForeignKey(to='contacts.ContactInfo')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='contact',
            name='work',
            field=models.ManyToManyField(to='contacts.Organization', through='contacts.OrganizationMember'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='address',
            name='contact_info',
            field=models.ForeignKey(to='contacts.ContactInfo'),
            preserve_default=True,
        ),
        migrations.CreateModel(
            name='NextOfKin',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('contacts.contact',),
        ),
        migrations.CreateModel(
            name='SocialWorker',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('contacts.contact',),
        ),
    ]
