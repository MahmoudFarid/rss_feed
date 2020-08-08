from django_filters import rest_framework as filters

from .models import Item, Feed


class FeedFilter(filters.FilterSet):

    class Meta:
        model = Feed
        fields = ['is_followed']


class ItemFilter(filters.FilterSet):

    class Meta:
        model = Item
        fields = ['state']
