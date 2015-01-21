from django.core.management.base import BaseCommand
from django.db import models

from editorsnotes.main.models.auth import LogActivity

from ... import get_index

class Command(BaseCommand):
    help = 'Rebuild elasticsearch activity index'
    def handle(self, *args, **kwargs):
        activity_index = get_index('activity')

        activity_index.delete()
        activity_index.create()

        qs = LogActivity.objects\
                .select_related('project', 'user', 'content_type')

        ct = qs.count()
        self.stdout.write('Indexing {} actions'.format(ct))

        i = 0
        for activity in qs:
            activity_index.handle_edit(activity, refresh=False)
            i += 1
            if (i % 100 == 0): self.stdout.write('{}/{}'.format(i, ct))
