# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_auto_20141021_0716'),
    ]

    operations = [
        migrations.AlterField(
            model_name='note',
            name='title',
            field=models.CharField(max_length=b'80'),
        ),
        migrations.AlterUniqueTogether(
            name='note',
            unique_together=set([('title', 'project')]),
        ),
    ]
