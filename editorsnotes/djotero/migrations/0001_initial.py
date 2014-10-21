# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CachedArchive',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='CachedCreator',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ZoteroLink',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('zotero_url', models.URLField(blank=True)),
                ('date_information', models.TextField(blank=True)),
                ('modified', models.DateTimeField(editable=False)),
                ('last_synced', models.DateTimeField(null=True, blank=True)),
                ('cached_archive', models.ForeignKey(blank=True, to='djotero.CachedArchive', null=True)),
                ('cached_creator', models.ManyToManyField(to='djotero.CachedCreator', null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
