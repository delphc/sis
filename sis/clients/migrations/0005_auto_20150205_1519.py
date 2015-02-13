# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0004_auto_20150128_1412'),
    ]

    operations = [
        migrations.AlterField(
            model_name='referral',
            name='notes',
            field=models.TextField(default=b'', max_length=250, verbose_name='Referral notes', blank=True),
        ),
        migrations.AlterField(
            model_name='referral',
            name='reasons',
            field=models.ManyToManyField(db_constraint='Reasons for referral', to=b'clients.ReferralReason'),
        ),
        migrations.AlterField(
            model_name='referral',
            name='ref_date',
            field=models.DateField(verbose_name='Referral date'),
        ),
        migrations.AlterField(
            model_name='relationtype',
            name='contact_type',
            field=models.CharField(default=b'N', max_length=1, choices=[(b'N', 'Next of kin'), (b'W', 'Reference')]),
        ),
    ]
