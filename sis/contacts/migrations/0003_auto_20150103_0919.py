# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contacts', '0002_auto_20141230_1408'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContactType',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('contact_type', models.CharField(default=b'N', max_length=1, choices=[(b'N', 'Next of kin'), (b'W', 'Case worker')])),
                ('type_en', models.CharField(max_length=20)),
                ('type_fr', models.CharField(max_length=20)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='contact',
            name='contact_type',
        ),
        migrations.AddField(
            model_name='contact',
            name='category',
            field=models.CharField(default=b'N', max_length=1, choices=[(b'N', 'Next of kin'), (b'W', 'Case worker')]),
            preserve_default=True,
        ),
    ]
