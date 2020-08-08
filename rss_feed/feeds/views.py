from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from .filters import ItemFilter
from .models import Feed, Item
from .serializers import FeedSerializer, ItemSerializer
from .utils import prepare_feed_fields, prepare_feed_item_fields


class FeedViewSet(mixins.CreateModelMixin,
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  GenericViewSet):
    serializer_class = FeedSerializer

    def get_queryset(self):
        return Feed.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        parsed = serializer.validated_data.pop('parsed')
        feed_fields = prepare_feed_fields(parsed.get('feed'))
        feed = Feed.objects.create(**feed_fields, **serializer.validated_data)
        for entry in parsed.get('entries'):
            item_fields = prepare_feed_item_fields(entry, feed)
            Item.objects.create(**item_fields)


class ItemViewSet(mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  GenericViewSet):
    serializer_class = ItemSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ItemFilter

    def get_queryset(self):
        filter_kwargs = {"feed__created_by": self.request.user}
        if self.kwargs.get('feed_id'):
            filter_kwargs['feed_id'] = self.kwargs.get('feed_id')
        return Item.objects.filter(**filter_kwargs).order_by('-modified')
