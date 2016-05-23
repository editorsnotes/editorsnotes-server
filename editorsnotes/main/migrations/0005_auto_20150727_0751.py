# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_user_confirmed'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='confirmed',
            field=models.BooleanField(default=False),
        ),
    ]
