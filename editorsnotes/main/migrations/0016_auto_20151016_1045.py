# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import editorsnotes.main.fields


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0015_auto_20151015_1504'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='project',
            name='description',
        ),
        migrations.RemoveField(
            model_name='user',
            name='zotero_key',
        ),
        migrations.RemoveField(
            model_name='user',
            name='zotero_uid',
        ),
        migrations.AddField(
            model_name='project',
            name='markup',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='project',
            name='markup_html',
            field=editorsnotes.main.fields.XHTMLField(null=True, editable=False, blank=True),
        ),
        migrations.AddField(
            model_name='user',
            name='profile',
            field=models.CharField(max_length=1000, null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='note',
            name='markup',
            field=models.TextField(null=True, blank=True),
        ),
    ]
