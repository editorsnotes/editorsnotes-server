# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import editorsnotes.main.fields


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0010_delete_notesection'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='citation',
            name='content_type',
        ),
        migrations.RemoveField(
            model_name='citation',
            name='creator',
        ),
        migrations.RemoveField(
            model_name='citation',
            name='document',
        ),
        migrations.RemoveField(
            model_name='citation',
            name='last_updater',
        ),
        migrations.DeleteModel(
            name='Citation',
        ),
        migrations.AlterUniqueTogether(
            name='documentmetadata',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='documentmetadata',
            name='creator',
        ),
        migrations.RemoveField(
            model_name='documentmetadata',
            name='document',
        ),
        migrations.DeleteModel(
            name='DocumentMetadata',
        ),
        migrations.RemoveField(
            model_name='topic',
            name='summary',
        ),
        migrations.AddField(
            model_name='topic',
            name='markup',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='topic',
            name='markup_html',
            field=editorsnotes.main.fields.XHTMLField(null=True, editable=False, blank=True),
            preserve_default=True,
        ),
    ]
