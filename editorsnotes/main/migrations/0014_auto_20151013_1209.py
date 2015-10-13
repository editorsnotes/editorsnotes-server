# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0013_auto_20151013_1155'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='alternatename',
            unique_together=set([]),
        ),
        migrations.RemoveField(
            model_name='alternatename',
            name='creator',
        ),
        migrations.RemoveField(
            model_name='alternatename',
            name='topic',
        ),
        migrations.AddField(
            model_name='topic',
            name='alternate_names',
            field=django.contrib.postgres.fields.ArrayField(default=list, base_field=models.CharField(max_length=200), size=None),
        ),
        migrations.DeleteModel(
            name='AlternateName',
        ),
    ]
