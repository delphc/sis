# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0007_organizationmember_position'),
    ]

    operations = [
        migrations.AlterField(
            model_name='organizationmember',
            name='position',
            field=models.ForeignKey(to='contacts.Position'),
        ),
    ]
