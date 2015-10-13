from django.core.management.base import BaseCommand

from .. import items

class Command(BaseCommand):
    help = 'Rebuild elasticsearch index'
    def handle(self, *args, **kwargs):
        en_index = items.index
        en_index.delete()
        en_index.create()
        for doc_type in en_index.document_types.values():
            ct = doc_type.model.objects.count()
            self.stdout.write(u'Creating {:,} "{}" documents'.format(
                ct, doc_type.type_label))
            doc_type.update_all()
