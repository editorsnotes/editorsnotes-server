# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_auto_20150824_1204'),
    ]

    operations = [
        migrations.DeleteModel(
            name='NoteSection',
        ),
    ]
