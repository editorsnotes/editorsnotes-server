# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.contrib.postgres.fields


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_auto_20151013_1106'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='legacytopic',
            name='merged_into',
        ),
        migrations.RemoveField(
            model_name='topicnode',
            name='creator',
        ),
        migrations.RemoveField(
            model_name='topicnode',
            name='last_updater',
        ),
        migrations.RemoveField(
            model_name='topicnode',
            name='merged_into',
        ),
        migrations.AddField(
            model_name='topic',
            name='same_as',
            field=django.contrib.postgres.fields.ArrayField(default=list, base_field=models.URLField(), size=None),
        ),
        migrations.AddField(
            model_name='topic',
            name='types',
            field=django.contrib.postgres.fields.ArrayField(default=list, base_field=models.URLField(), size=None),
        ),
        migrations.AlterUniqueTogether(
            name='topic',
            unique_together=set([('project', 'preferred_name')]),
        ),
        migrations.DeleteModel(
            name='LegacyTopic',
        ),
        migrations.RemoveField(
            model_name='topic',
            name='topic_node',
        ),
        migrations.DeleteModel(
            name='TopicNode',
        ),
    ]
