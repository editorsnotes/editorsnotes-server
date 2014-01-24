from django.core.management.base import BaseCommand
from django.db import models

from reversion.models import Version

from editorsnotes.main.models.base import Administered

from ... import activity_index

class Command(BaseCommand):
    help = 'Rebuild elasticsearch activity index'
    def handle(self, *args, **kwargs):
        activity_index.delete()
        activity_index.create()

        administered_models = list(
            m._meta.module_name for m in models.get_models()
            if issubclass(m, Administered))

        qs = Version.objects\
                .select_related('revision__user',
                                'revision__revisionproject__project',
                                'content_type')\
                .filter(content_type__model__in=administered_models)\
                .order_by('-revision__date_created')


        self.stdout.write('Indexing {} actions'.format(qs.count()))

        i = 0
        CHUNK_SIZE = 1000

        while True:
            chunk = qs[i:i + CHUNK_SIZE]
            if not chunk:
                break
            data = (activity_index.data_from_reversion_version(version)
                    for version in chunk)
            activity_index.es.bulk_index(activity_index.name, 'activity', data)
            i += CHUNK_SIZE

