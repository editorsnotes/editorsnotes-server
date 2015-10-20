# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.postgres.fields
import editorsnotes.main.fields


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0017_auto_20151016_1233'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='documentlink',
            name='creator',
        ),
        migrations.RemoveField(
            model_name='documentlink',
            name='document',
        ),
        migrations.RemoveField(
            model_name='footnote',
            name='creator',
        ),
        migrations.RemoveField(
            model_name='footnote',
            name='last_updater',
        ),
        migrations.RemoveField(
            model_name='footnote',
            name='transcript',
        ),
        migrations.AlterModelOptions(
            name='document',
            options={'ordering': ['-last_updated']},
        ),
        migrations.RemoveField(
            model_name='document',
            name='collection',
        ),
        migrations.RemoveField(
            model_name='document',
            name='edtf_date',
        ),
        migrations.RemoveField(
            model_name='document',
            name='import_id',
        ),
        migrations.RemoveField(
            model_name='document',
            name='language',
        ),
        migrations.RemoveField(
            model_name='document',
            name='ordering',
        ),
        migrations.RemoveField(
            model_name='transcript',
            name='content',
        ),
        migrations.AddField(
            model_name='document',
            name='links',
            field=django.contrib.postgres.fields.ArrayField(default=list, base_field=models.CharField(max_length=1000), size=None),
        ),
        migrations.AddField(
            model_name='transcript',
            name='markup',
            field=models.TextField(null=True, blank=True),
        ),
        migrations.AddField(
            model_name='transcript',
            name='markup_html',
            field=editorsnotes.main.fields.XHTMLField(null=True, editable=False, blank=True),
        ),
        migrations.DeleteModel(
            name='DocumentLink',
        ),
        migrations.DeleteModel(
            name='Footnote',
        ),
    ]
