# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_auto_20150113_1217'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='confirmed',
            field=models.BooleanField(default=True),
            preserve_default=True,
        ),
    ]
