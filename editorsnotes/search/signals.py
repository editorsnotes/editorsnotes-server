from django.apps import apps as django_apps
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from . import activity, items

main = django_apps.get_app_config('main')
en_index = items.index
activity_index = activity.index

@receiver(post_save, sender=main.get_model('LogActivity'))
def update_activity_index(sender, instance, created, **kwargs):
    activity.handle_edit(instance)

@receiver(post_save)
def update_elastic_search_handler(sender, instance, created, **kwargs):
    klass = instance.__class__
    if klass in en_index.document_types:
        document_type = en_index.document_types[klass]
        if created:
            document_type.index(instance)
        else:
            document_type.update(instance)

@receiver(post_delete)
def delete_es_document_handler(sender, instance, **kwargs):
    klass = instance.__class__
    if klass in en_index.document_types:
        document_type = en_index.document_types[klass]
        document_type.remove(instance)
