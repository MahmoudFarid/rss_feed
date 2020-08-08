from django.utils import timezone

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet

from rss_feed.core.mixins import MultipleSerializerMixin

from .filters import FeedFilter, ItemFilter
from .models import Feed, Item
from .serializers import FeedSerializer, ItemSerializer, ItemStateSerializer
from .utils import prepare_feed_fields, prepare_feed_item_fields


class FeedViewSet(mixins.CreateModelMixin,
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  GenericViewSet):
    serializer_class = FeedSerializer
    filter_backends = (DjangoFilterBackend,)
    filterset_class = FeedFilter

    def get_queryset(self):
        return Feed.objects.filter(created_by=self.request.user)

    def perform_create(self, serializer):
        parsed = serializer.validated_data.pop('parsed')
        feed_fields = prepare_feed_fields(parsed.get('feed'))
        feed = Feed.objects.create(**feed_fields, **serializer.validated_data, last_update=timezone.now())
        for entry in parsed.get('entries'):
            item_fields = prepare_feed_item_fields(entry)
            Item.objects.create(feed=feed, last_update=timezone.now(), ** item_fields)

    @action(detail=True, methods=['post', 'delete'])
    def follow(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.method == 'POST':
            if instance.is_followed:
                raise ValidationError({"non_field_errors": ["You already followed this feed"]})
            instance.is_followed = True
        elif request.method == 'DELETE':
            if not instance.is_followed:
                raise ValidationError({"non_field_errors": ["You already unfollowed this feed"]})
            instance.is_followed = False
        instance.save()
        return Response(status=status.HTTP_200_OK, data=self.get_serializer(instance).data)


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
        return Item.objects.filter(**filter_kwargs).order_by('-last_update')

    @action(detail=False, methods=['post'])
    def read(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        Item.objects.filter(id__in=serializer.validated_data.get('ids')).update(state=Item.STATE_CHOICES.READ)
        return Response(status=status.HTTP_200_OK, data=serializer.data)
