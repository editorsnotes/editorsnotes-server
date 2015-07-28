# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0005_auto_20150727_0751'),
    ]

    operations = [
        migrations.AlterField(
            model_name='project',
            name='default_license',
            field=models.ForeignKey(default=1, to='licensing.License', help_text=b'Default license for project notes. Licenses can also be set on a note-by-note basis.'),
        ),
        migrations.AlterField(
            model_name='project',
            name='slug',
            field=models.SlugField(help_text=b'Used for project-specific URLs and groups. Valid characters: letters, numbers, or _-', unique=True),
        ),
    ]
