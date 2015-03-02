# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('food', '0003_auto_20150226_1409'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='foodcategory',
            options={'ordering': ['sort_order']},
        ),
        migrations.RemoveField(
            model_name='foodingredient',
            name='categories',
        ),
        migrations.AddField(
            model_name='foodingredient',
            name='category',
            field=models.ForeignKey(default=b'', to='food.FoodCategory'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='foodcategory',
            unique_together=set([('slug', 'sort_order')]),
        ),
    ]
