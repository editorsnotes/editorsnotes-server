# -*- coding: utf-8 -*-


from django.db import migrations, models


def populate_usernames(apps, schema_editor):
    User = apps.get_model('main', 'User')
    for user in User.objects.all():
        if user.first_name or user.last_name:
            display_name = user.first_name + ' ' + user.last_name
            display_name = display_name.strip().rstrip()
        else:
            display_name = user.username

        user.display_name = display_name
        user.save()

class Migration(migrations.Migration):

    dependencies = [
        ('main', '0020_user_display_name'),
    ]

    operations = [
        migrations.RunPython(populate_usernames)
    ]
