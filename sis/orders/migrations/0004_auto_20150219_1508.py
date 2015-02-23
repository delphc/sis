# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone
import django_extensions.db.fields


class Migration(migrations.Migration):

    dependencies = [
        ('orders', '0003_auto_20150219_1408'),
    ]

    operations = [
        migrations.CreateModel(
            name='MealDefaultMeal',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', django_extensions.db.fields.CreationDateTimeField(default=django.utils.timezone.now, verbose_name='created', editable=False, blank=True)),
                ('modified', django_extensions.db.fields.ModificationDateTimeField(default=django.utils.timezone.now, verbose_name='modified', editable=False, blank=True)),
                ('size', models.CharField(default=b'R', max_length=1, choices=[(b'H', 'Half'), (b'R', 'Regular')])),
                ('quantity', models.PositiveIntegerField(default=0)),
                ('meal', models.ForeignKey(to='orders.MealDefault')),
            ],
            options={
                'ordering': ('-modified', '-created'),
                'abstract': False,
                'get_latest_by': 'modified',
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='mealdefault',
            name='meal_type',
        ),
        migrations.RemoveField(
            model_name='mealdefault',
            name='nb_meal',
        ),

        migrations.AddField(
            model_name='mealdefault',
            name='order',
            field=models.ForeignKey(default=b'', to='orders.Order'),
            preserve_default=True,
        ),
    ]
