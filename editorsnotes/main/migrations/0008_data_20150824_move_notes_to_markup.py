# -*- coding: utf-8 -*-


from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0007_auto_20150824_1044'),
    ]

    # Use this migration to:
    #   1. Move notes' content fields to markup + html fields
    #   2. Move topics' summary fields to markup + html fields
    #
    # Remember that citations will be deleted, so they must be turned into
    # empty document blocks.
    operations = [
    ]
