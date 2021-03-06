# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-06-28 09:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0024_topic_ld'),
    ]

    operations = [
        migrations.AlterField(
            model_name='note',
            name='is_private',
            field=models.BooleanField(default=False, help_text="If true, will only be be viewable to users who belong to the note's project."),
        ),
    ]
