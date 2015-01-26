# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Client',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('gender', models.CharField(default=b'U', max_length=1, choices=[(b'F', 'Female'), (b'M', 'Male'), (b'U', 'Unknown gender')])),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('middle_name', models.CharField(max_length=50, blank=True)),
                ('maiden_name', models.CharField(max_length=50, blank=True)),
                ('birth_date', models.DateField()),
                ('status', models.CharField(default=b'P', max_length=1, choices=[(b'P', 'Pending'), (b'A', 'Active'), (b'I', 'Inactive')])),
                ('native_lang', models.CharField(max_length=2, verbose_name='Native language', choices=[(b'EN', 'English'), (b'FR', 'French'), (b'EF', 'English/French')])),
                ('com_lang', models.CharField(max_length=2, verbose_name='Language for communication', choices=[(b'EN', 'English'), (b'FR', 'French'), (b'EF', 'English/French')])),
                ('cdif_exd', models.BooleanField(default=False, verbose_name='Expressive difficulty')),
                ('cdif_hoh', models.BooleanField(default=False, verbose_name='Hard of hearing')),
                ('cdif_anl', models.BooleanField(default=False, verbose_name='Analphabete')),
                ('cdif_cog', models.BooleanField(default=False, verbose_name='Cognitive loss')),
                ('direct_contact', models.BooleanField(default=True, choices=[(True, 'Yes'), (False, 'No')])),
                ('directions', models.TextField(default=b'', max_length=256, blank=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Referral',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ref_date', models.DateField()),
                ('notes', models.TextField(default=b'', max_length=250, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ReferralReason',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('reason_fr', models.CharField(max_length=100)),
                ('reason_en', models.CharField(max_length=100)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Relationship',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('emergency', models.BooleanField(default=False, verbose_name='Emergency contact')),
                ('follow_up', models.BooleanField(default=False, verbose_name='Follow-up')),
                ('info', models.CharField(max_length=100, verbose_name='Additional information', blank=True)),
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
            name='RelationType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('contact_type', models.CharField(default=b'N', max_length=1, choices=[(b'N', 'Next of kin'), (b'W', 'Case worker')])),
                ('type_en', models.CharField(max_length=20)),
                ('type_fr', models.CharField(max_length=20)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
