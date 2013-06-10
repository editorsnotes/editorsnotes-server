from rest_framework.decorators import api_view
from rest_framework.generics import (
    ListCreateAPIView, RetrieveUpdateDestroyAPIView)
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from rest_framework.reverse import reverse

class BaseListAPIView(ListCreateAPIView):
    paginate_by = 50
    paginate_by_param = 'page_size'
    permission_classes = (IsAuthenticatedOrReadOnly,)
    def pre_save(self, obj):
        obj.creator = obj.last_updater = self.request.user

class BaseDetailView(RetrieveUpdateDestroyAPIView):
    permission_classes = (IsAuthenticatedOrReadOnly,)
    def pre_save(self, obj):
        obj.last_updater = self.request.user


@api_view(('GET',))
def root(request):
    return Response({
        'auth-token': reverse('obtain-auth-token'),
        'notes': reverse('api-notes-list'),
        'topics': reverse('api-topics-list'),
        'documents': reverse('api-documents-list')
    })
