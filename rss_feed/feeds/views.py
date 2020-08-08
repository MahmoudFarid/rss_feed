from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from rss_feed.core.mixins import MultipleSerializerMixin

from .filters import ItemFilter
from .models import Feed, Item
from .serializers import FeedSerializer, ItemSerializer, ItemStateSerializer
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


class ItemViewSet(MultipleSerializerMixin,
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  GenericViewSet):
    filter_backends = (DjangoFilterBackend,)
    filterset_class = ItemFilter
    action_serializer_classes = {
        'default': ItemSerializer,
        'read': ItemStateSerializer,
    }

    def get_queryset(self):
        filter_kwargs = {"feed__created_by": self.request.user}
        if self.kwargs.get('feed_id'):
            filter_kwargs['feed_id'] = self.kwargs.get('feed_id')
        return Item.objects.filter(**filter_kwargs).order_by('-modified')

    @action(detail=False, methods=['post'])
    def read(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        Item.objects.filter(id__in=serializer.validated_data.get('ids')).update(state=Item.STATE_CHOICES.READ)
        return Response(status=status.HTTP_200_OK, data=serializer.data)
