from django.apps import apps as django_apps
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from .activity.helpers import handle_activity_edit
from . import items_index

main = django_apps.get_app_config('main')


@receiver(post_save, sender=main.get_model('LogActivity'))
def update_activity_index(sender, instance, created, **kwargs):
    handle_activity_edit(instance)


@receiver(post_save)
def update_elastic_search_handler(sender, instance, created, **kwargs):
    model = instance.__class__
    document_type = items_index.document_types.get(model, None)

    if document_type:
        if created:
            document_type.index(instance)
        else:
            document_type.update(instance)


@receiver(post_delete)
def delete_es_document_handler(sender, instance, **kwargs):
    model = instance.__class__
    document_type = items_index.document_types.get(model, None)

    if document_type:
        document_type.remove(instance)
