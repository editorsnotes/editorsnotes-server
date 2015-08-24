# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import editorsnotes.main.fields


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0006_auto_20150728_0928'),
    ]

    operations = [
        migrations.AddField(
            model_name='note',
            name='markup',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='note',
            name='markup_html',
            field=editorsnotes.main.fields.XHTMLField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
