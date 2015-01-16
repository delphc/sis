# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0009_auto_20141109_1558'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='client',
            options={'ordering': ('-modified', '-created'), 'get_latest_by': 'modified'},
        ),
        migrations.RemoveField(
            model_name='address',
            name='address1',
        ),
        migrations.RemoveField(
            model_name='address',
            name='address2',
        ),
        migrations.RemoveField(
            model_name='client',
            name='create_date',
        ),
        migrations.RemoveField(
            model_name='client',
            name='created_by',
        ),
        migrations.RemoveField(
            model_name='client',
            name='delete_date',
        ),
        migrations.RemoveField(
            model_name='client',
            name='update_date',
        ),
        migrations.AddField(
            model_name='address',
            name='address',
            field=models.CharField(default=b'', max_length=250),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='client',
            name='created',
            field=django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='client',
            name='modified',
            field=django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='address',
            name='city',
            field=models.CharField(default='Montreal', max_length=50),
        ),
        migrations.AlterField(
            model_name='address',
            name='info',
            field=models.CharField(max_length=100, blank=True),
        ),
        migrations.AlterField(
            model_name='address',
            name='prov',
            field=models.CharField(default='Qc', max_length=30),
        ),
        migrations.AlterField(
            model_name='client',
            name='directions',
            field=models.CharField(max_length=256, blank=True),
        ),
        migrations.AlterField(
            model_name='client',
            name='email_address',
            field=models.EmailField(max_length=75, blank=True),
        ),
        migrations.AlterField(
            model_name='client',
            name='maiden_name',
            field=models.CharField(max_length=50, blank=True),
        ),
        migrations.AlterField(
            model_name='client',
            name='middle_name',
            field=models.CharField(max_length=50, blank=True),
        ),
        migrations.AlterField(
            model_name='phone',
            name='info',
            field=models.CharField(max_length=128, blank=True),
        ),
    ]
