# -*- coding: utf-8 -*-


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0014_auto_20151013_1209'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userfeedback',
            name='user',
        ),
        migrations.DeleteModel(
            name='UserFeedback',
        ),
    ]
