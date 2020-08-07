from rest_framework import mixins
from rest_framework.viewsets import GenericViewSet

from .models import Feed, Item
from .serializers import FeedSerializer
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
