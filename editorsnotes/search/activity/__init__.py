from django.utils.functional import SimpleLazyObject

from ..index import ElasticSearchIndex

index = SimpleLazyObject(lambda: ActivityIndex())


class ActivityIndex(ElasticSearchIndex):
    name = 'activitylog'
