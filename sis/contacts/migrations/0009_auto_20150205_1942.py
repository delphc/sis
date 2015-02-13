# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0008_auto_20150205_1853'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='organizationmember',
            options={'ordering': ('status', '-activate_date')},
        ),
        migrations.RemoveField(
            model_name='organizationmember',
            name='created',
        ),
        migrations.RemoveField(
            model_name='organizationmember',
            name='modified',
        ),
        migrations.AddField(
            model_name='organizationmember',
            name='activate_date',
            field=models.DateTimeField(help_text='keep empty for an immediate activation', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='organizationmember',
            name='deactivate_date',
            field=models.DateTimeField(help_text='keep empty for indefinite activation', null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='organizationmember',
            name='status',
            field=models.IntegerField(default=1, verbose_name='status', choices=[(0, 'Inactive'), (1, 'Active')]),
            preserve_default=True,
        ),
    ]
