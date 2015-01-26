# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0001_initial'),
        ('contacts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='relationship',
            name='contact',
            field=models.ForeignKey(to='contacts.Contact'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='relationship',
            name='type',
            field=models.ForeignKey(blank=True, to='clients.RelationType', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='referral',
            name='client',
            field=models.ForeignKey(to='clients.Client'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='referral',
            name='contact',
            field=models.ForeignKey(to='contacts.Contact'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='referral',
            name='reasons',
            field=models.ManyToManyField(to='clients.ReferralReason'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='client',
            name='relationships',
            field=models.ManyToManyField(to='contacts.Contact', through='clients.Relationship'),
            preserve_default=True,
        ),
    ]
