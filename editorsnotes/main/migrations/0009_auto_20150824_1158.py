# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import editorsnotes.main.fields


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0008_data_20150824_move_notes_to_markup'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='citationns',
            name='document',
        ),
        migrations.RemoveField(
            model_name='citationns',
            name='notesection_ptr',
        ),
        migrations.DeleteModel(
            name='CitationNS',
        ),
        migrations.RemoveField(
            model_name='notereferencens',
            name='note_reference',
        ),
        migrations.RemoveField(
            model_name='notereferencens',
            name='notesection_ptr',
        ),
        migrations.DeleteModel(
            name='NoteReferenceNS',
        ),
        migrations.AlterUniqueTogether(
            name='notesection',
            unique_together=None,
        ),
        migrations.RemoveField(
            model_name='notesection',
            name='creator',
        ),
        migrations.RemoveField(
            model_name='notesection',
            name='last_updater',
        ),
        migrations.RemoveField(
            model_name='notesection',
            name='note',
        ),
        migrations.RemoveField(
            model_name='textns',
            name='notesection_ptr',
        ),
        migrations.DeleteModel(
            name='NoteSection',
        ),
        migrations.DeleteModel(
            name='TextNS',
        ),
        migrations.RemoveField(
            model_name='note',
            name='content',
        ),
        migrations.RemoveField(
            model_name='note',
            name='sections_counter',
        ),
        migrations.AlterField(
            model_name='note',
            name='markup',
            field=models.TextField(),
        ),
        migrations.AlterField(
            model_name='note',
            name='markup_html',
            field=editorsnotes.main.fields.XHTMLField(null=True, editable=False, blank=True),
        ),
    ]
