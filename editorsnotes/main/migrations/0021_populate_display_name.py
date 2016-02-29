# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def populate_usernames(apps, schema_editor):
    User = apps.get_model('main', 'User')
    for user in User.objects.all():
        user.display_name = user._get_display_name()
        user.save()

class Migration(migrations.Migration):

    dependencies = [
        ('main', '0020_user_display_name'),
    ]

    operations = [
        migrations.RunPython(populate_usernames)
    ]
