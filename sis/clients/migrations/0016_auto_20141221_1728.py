# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0015_auto_20141221_1454'),
    ]

    operations = [
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
        migrations.AddField(
            model_name='client',
            name='referralReasons',
            field=models.ManyToManyField(to='clients.ReferralReason'),
            preserve_default=True,
        ),
    ]
