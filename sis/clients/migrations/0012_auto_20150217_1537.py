# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0011_auto_20150217_1534'),
    ]

    operations = [
        migrations.AlterField(
            model_name='relationship',
            name='rel_type',
            field=models.ForeignKey(verbose_name='Relation type', blank=True, to='clients.RelationType', null=True),
        ),
    ]
