# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0005_auto_20150120_1632'),
    ]

    operations = [
        migrations.CreateModel(
            name='Position',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('desc_en', models.CharField(max_length=30)),
                ('desc_fr', models.CharField(max_length=30)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterModelOptions(
            name='organizationmember',
            options={'ordering': ('-modified', '-created'), 'get_latest_by': 'modified'},
        ),
        migrations.RemoveField(
            model_name='organizationmember',
            name='end_date',
        ),
        migrations.RemoveField(
            model_name='organizationmember',
            name='start_date',
        ),
        migrations.RemoveField(
            model_name='organizationmember',
            name='position',
        ),
        migrations.AddField(
            model_name='organizationmember',
            name='created',
            field=django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='organizationmember',
            name='modified',
            field=django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='address',
            name='apt',
            field=models.CharField(default=b'', max_length=10, verbose_name='Apt. #', blank=True),
        ),
        migrations.AlterField(
            model_name='address',
            name='entry_code',
            field=models.CharField(default=b'', max_length=5, verbose_name='Entry code', blank=True),
        ),
        migrations.AlterField(
            model_name='contact',
            name='contact_type',
            field=models.CharField(default=b'N', max_length=1, choices=[(b'N', 'Next of kin'), (b'W', 'Reference')]),
        ),
        migrations.AlterField(
            model_name='contactinfo',
            name='email_address',
            field=models.EmailField(default=b'', max_length=75, blank=True),
        ),
#         migrations.AlterField(
#             model_name='organizationmember',
#             name='position',
#             field=models.ForeignKey(to='contacts.Position'),
#         ),
    ]
