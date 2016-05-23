# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-16 14:04


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0022_auto_20160229_0929'),
    ]

    operations = [
        migrations.AlterField(
            model_name='note',
            name='title',
            field=models.CharField(help_text=b'The title of the note.', max_length=80),
        ),
        migrations.AlterField(
            model_name='project',
            name='name',
            field=models.CharField(help_text=b'The name of the project.', max_length=80),
        ),
    ]
