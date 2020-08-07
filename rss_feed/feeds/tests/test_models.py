from django.test import TestCase

from ..models import Feed, Item
from .factories import FeedFactory, ItemFactory


class TestFeedModel(TestCase):

    def test_create_feed_model(self):
        self.assertEqual(Feed.objects.count(), 0)
        feed = FeedFactory()
        self.assertIsInstance(feed, Feed)
        self.assertEqual(Feed.objects.count(), 1)


class TestItemModel(TestCase):

    def test_create_item_model(self):
        self.assertEqual(Item.objects.count(), 0)
        item = ItemFactory()
        self.assertIsInstance(item, Item)
        self.assertEqual(Item.objects.count(), 1)
