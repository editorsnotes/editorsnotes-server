from django.core.management.base import BaseCommand

from ... import items_index

class Command(BaseCommand):
    help = 'Rebuild elasticsearch index'
    def handle(self, *args, **kwargs):
        items_index.delete()
        items_index.initialize()

        for doc_type in items_index.document_types.values():
            ct = doc_type.model.objects.count()
            self.stdout.write(u'Creating {:,} "{}" documents'.format(
                ct, doc_type.type_label))
            doc_type.update_all()
