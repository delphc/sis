# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('clients', '0010_auto_20150217_1442'),
    ]

    operations = [
        migrations.AlterField(
            model_name='relationship',
            name='contact_type',
            field=models.CharField(default=b'N', max_length=1, verbose_name='Contact type', choices=[(b'N', 'Next of kin'), (b'W', 'Reference')]),
        ),
#         migrations.AlterField(
#             model_name='relationship',
#             name='rel_type',
#             field=models.ForeignKey(to_field='Relation type', blank=True, to='clients.RelationType', null=True),
#         ),
    ]
