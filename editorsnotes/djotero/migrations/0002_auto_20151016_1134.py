# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djotero', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='zoterolink',
            name='cached_archive',
        ),
        migrations.RemoveField(
            model_name='zoterolink',
            name='cached_creator',
        ),
        migrations.DeleteModel(
            name='CachedArchive',
        ),
        migrations.DeleteModel(
            name='CachedCreator',
        ),
    ]
