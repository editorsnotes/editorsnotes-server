# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-16 16:49


import django.contrib.postgres.fields.jsonb
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0023_auto_20160316_1404'),
    ]

    operations = [
        migrations.AddField(
            model_name='topic',
            name='ld',
            field=django.contrib.postgres.fields.jsonb.JSONField(default=dict),
        ),
    ]
