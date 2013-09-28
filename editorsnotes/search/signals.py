from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from editorsnotes.main.models.notes import NoteSection

from .index import en_index

@receiver(post_save)
def update_elastic_search_handler(sender, instance, created, **kwargs):
    klass = instance.__class__
    if klass in en_index.document_types:
        document_type = en_index.document_types[klass]
        if created:
            document_type.index(instance)
        else:
            document_type.update(instance)
    elif isinstance(klass, NoteSection):
        update_elastic_search_handler(sender, instance.note, False)

@receiver(post_delete)
def delete_es_document_handler(sender, instance, **kwargs):
    klass = instance.__class__
    if klass in en_index.document_types:
        document_type = en_index.document_types[klass]
        document_type.remove(instance)
