# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0012_auto_20150217_1537'),
    ]

    operations = [
        migrations.AlterField(
            model_name='referral',
            name='contact',
            field=models.ForeignKey(verbose_name='Referred by', to='contacts.Contact'),
        ),
    ]
