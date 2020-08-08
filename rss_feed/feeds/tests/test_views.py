import json
from unittest import mock

from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient, APITestCase

from rss_feed.users.tests.factories import UserFactory

from ..models import Feed, Item
from ..utils import prepare_feed_fields, prepare_feed_item_fields
from .factories import FeedFactory, ItemFactory
from .mocking import (
    correct_result, missing_all_entries_attr, missing_feed_attrs,
    missing_some_entries_attr, not_found,
)


class TestActualFeedAPIViewSet(APITestCase):
    """
    Test actual requests without mocking
    """

    def setUp(self):
        self.user = UserFactory()
        self.client = APIClient()
        token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        self.unauthorized_client = APIClient()

        self.main_api = '/api/v1/feeds/'
        self.obj_api = '/api/v1/feeds/{}/'

    def test_create_nu_feed(self):
        feed_count = Feed.objects.count()
        item_count = Item.objects.count()
        data = {
            "xml_url": "http://www.nu.nl/rss/Algemeen"
        }
        response = self.client.post(
            self.main_api,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        response = response.json()
        self.assertEqual(response.get('xml_url'), data.get('xml_url'))
        self.assertEqual(Feed.objects.count(), feed_count + 1)
        feed = Feed.objects.get(xml_url=data.get('xml_url'))
        self.assertEqual(Item.objects.count(), item_count + feed.items.count())

    def test_create_feedburner_feed(self):
        feed_count = Feed.objects.count()
        item_count = Item.objects.count()
        data = {
            "xml_url": "https://feeds.feedburner.com/tweakers/mixed"
        }
        response = self.client.post(
            self.main_api,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        response = response.json()
        self.assertEqual(response.get('xml_url'), data.get('xml_url'))
        self.assertEqual(Feed.objects.count(), feed_count + 1)
        feed = Feed.objects.get(xml_url=data.get('xml_url'))
        self.assertEqual(Item.objects.count(), item_count + feed.items.count())

    def test_create_reddit_feed(self):
        feed_count = Feed.objects.count()
        item_count = Item.objects.count()
        data = {
            "xml_url": "https://www.reddit.com/r/news/.rss"
        }
        response = self.client.post(
            self.main_api,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        response = response.json()
        self.assertEqual(response.get('xml_url'), data.get('xml_url'))
        self.assertEqual(Feed.objects.count(), feed_count + 1)
        feed = Feed.objects.get(xml_url=data.get('xml_url'))
        self.assertEqual(Item.objects.count(), item_count + feed.items.count())

    def test_create_cnn_feed(self):
        feed_count = Feed.objects.count()
        item_count = Item.objects.count()
        data = {
            "xml_url": "http://rss.cnn.com/rss/edition_world.rss",
        }
        response = self.client.post(
            self.main_api,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 201)
        response = response.json()
        self.assertEqual(response.get('xml_url'), data.get('xml_url'))
        self.assertEqual(Feed.objects.count(), feed_count + 1)
        feed = Feed.objects.get(xml_url=data.get('xml_url'))
        self.assertEqual(Item.objects.count(), item_count + feed.items.count())


class TestFeedAPIViewSet(APITestCase):
    """
    Test with mocking results
    """

    def setUp(self):
        self.user = UserFactory()
        self.client = APIClient()
        token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        self.unauthorized_client = APIClient()

        self.main_api = '/api/v1/feeds/'
        self.obj_api = '/api/v1/feeds/{}/'

        self.data = {
            "xml_url": "https://feeds.feedburner.com/tweakers/mixed"
        }

    @mock.patch('rss_feed.feeds.serializers.parse_rss_link', return_value=correct_result)
    def test_create_feed_with_correct_results(self, mocked_parser):
        self.assertEqual(mocked_parser.call_count, 0)
        response = self.client.post(
            self.main_api,
            data=json.dumps(self.data),
            content_type='application/json'
        )
        self.assertEqual(mocked_parser.call_count, 1)
        self.assertEqual(response.status_code, 201)
        response = response.json()
        self.assertEqual(response.get('xml_url'), self.data.get('xml_url'))
        # in the mock file, we created 1 feed and 3 items assigned to it
        self.assertEqual(Feed.objects.count(), 1)
        self.assertEqual(Item.objects.count(), 3)

        feed = Feed.objects.last()
        self.assertEqual(feed.xml_url, self.data.get('xml_url'))
        self.assertEqual(Feed.objects.get(**prepare_feed_fields(correct_result.get('feed'))).id, feed.id)

        for item_result in correct_result.get('entries'):
            self.assertTrue(Item.objects.filter(**prepare_feed_item_fields(item_result, feed)).exists())
            item = Item.objects.get(**prepare_feed_item_fields(item_result, feed))
            self.assertEqual(item.feed, feed)

    @mock.patch('rss_feed.feeds.serializers.parse_rss_link', return_value=not_found)
    def test_create_feed_with_not_found_link(self, mocked_parser):
        self.assertEqual(mocked_parser.call_count, 0)
        response = self.client.post(
            self.main_api,
            data=json.dumps(self.data),
            content_type='application/json'
        )
        self.assertEqual(mocked_parser.call_count, 1)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Feed.objects.count(), 0)
        self.assertEqual(Item.objects.count(), 0)
        response = response.json()
        self.assertIn('Found Malformed feed', response.get('non_field_errors')[0])

    @mock.patch('rss_feed.feeds.serializers.parse_rss_link', return_value=missing_feed_attrs)
    def test_create_feed_with_missing_feed_attrs(self, mocked_parser):
        self.assertEqual(mocked_parser.call_count, 0)
        response = self.client.post(
            self.main_api,
            data=json.dumps(self.data),
            content_type='application/json'
        )
        self.assertEqual(mocked_parser.call_count, 1)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Feed.objects.count(), 0)
        self.assertEqual(Item.objects.count(), 0)
        response = response.json()
        self.assertIn('has no title', response.get('non_field_errors')[0])
        self.assertIn('has no subtitle', response.get('non_field_errors')[0])
        self.assertIn('has no link', response.get('non_field_errors')[0])

    @mock.patch('rss_feed.feeds.serializers.parse_rss_link', return_value=missing_all_entries_attr)
    def test_create_feed_with_missing_all_feed_item_attrs(self, mocked_parser):
        self.assertEqual(mocked_parser.call_count, 0)
        response = self.client.post(
            self.main_api,
            data=json.dumps(self.data),
            content_type='application/json'
        )
        self.assertEqual(mocked_parser.call_count, 1)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(Feed.objects.count(), 0)
        self.assertEqual(Item.objects.count(), 0)
        response = response.json()
        self.assertIn("All items missing some of these attrs", response.get('non_field_errors')[0])

    @mock.patch('rss_feed.feeds.serializers.parse_rss_link', return_value=missing_some_entries_attr)
    def test_create_feed_with_missing_some_feed_item_attrs(self, mocked_parser):
        self.assertEqual(mocked_parser.call_count, 0)
        response = self.client.post(
            self.main_api,
            data=json.dumps(self.data),
            content_type='application/json'
        )
        self.assertEqual(mocked_parser.call_count, 1)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Feed.objects.count(), 1)
        # only 1 item is valid and 2 is not valid, so we will create a feed with this valid item
        self.assertEqual(Item.objects.count(), 1)

    def test_create_feed_with_empty_data(self):
        data = {}
        response = self.client.post(
            self.main_api,
            data=json.dumps(data),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)
        response = response.json()
        self.assertEqual(len(response.keys()), 1)
        self.assertEqual(response.get('xml_url'), ['This field is required.'])

    def test_list_feeds(self):
        feeds = FeedFactory.create_batch(5, created_by=self.user)
        FeedFactory.create_batch(3)
        response = self.client.get(
            self.main_api
        )
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertEqual(response.get('count'), len(feeds))
        for result in response.get('results'):
            self.assertEqual(len(result.keys()), 6)
            feed = Feed.objects.get(id=result.get('id'))
            self.assertIn(feed, feeds)
            self.assertEqual(result.get('title'), feed.title)
            self.assertEqual(result.get('xml_url'), feed.xml_url)
            self.assertEqual(result.get('link'), feed.link)
            self.assertEqual(result.get('description'), feed.description)
            self.assertIn('image', result)

    def test_retrieve_feed(self):
        feed = FeedFactory.create(created_by=self.user)
        response = self.client.get(
            self.obj_api.format(feed.id)
        )
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertEqual(len(response.keys()), 6)
        self.assertEqual(response.get('id'), feed.id)
        self.assertEqual(response.get('title'), feed.title)
        self.assertEqual(response.get('xml_url'), feed.xml_url)
        self.assertEqual(response.get('link'), feed.link)
        self.assertEqual(response.get('description'), feed.description)
        self.assertIn('image', response)

    def test_retrieve_feed_by_another_user(self):
        feed = FeedFactory.create()
        response = self.client.get(
            self.obj_api.format(feed.id)
        )
        self.assertEqual(response.status_code, 404)


class TestItemAPIViewSet(APITestCase):

    def setUp(self):
        self.user = UserFactory()
        self.client = APIClient()
        token, _ = Token.objects.get_or_create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)

        self.unauthorized_client = APIClient()

        self.feed = FeedFactory(created_by=self.user)
        self.unread_feed_items = ItemFactory.create_batch(3, feed=self.feed, state=Item.STATE_CHOICES.UNREAD)
        self.read_feed_items = ItemFactory.create_batch(2, feed=self.feed, state=Item.STATE_CHOICES.READ)
        self.unread_items = ItemFactory.create_batch(2, feed__created_by=self.user, state=Item.STATE_CHOICES.UNREAD)
        self.read_items = ItemFactory.create_batch(4, feed__created_by=self.user, state=Item.STATE_CHOICES.READ)
        ItemFactory.create_batch(2)

        self.feed_items_api = '/api/v1/feeds/{}/items/'.format(self.feed.id)
        self.items_api = '/api/v1/feeds/items/'

    def test_list_feed_items(self):
        response = self.client.get(
            self.feed_items_api
        )
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertEqual(response.get('count'), len(self.unread_feed_items) + len(self.read_feed_items))
        for result in response.get('results'):
            self.assertEqual(len(result.keys()), 7)
            item = Item.objects.get(id=result.get('id'))
            self.assertIn(item, self.unread_feed_items + self.read_feed_items)
            self.assertEqual(result.get('feed'), item.feed_id)
            self.assertEqual(result.get('title'), item.title)
            self.assertEqual(result.get('link'), item.link)
            self.assertEqual(result.get('published_time'), item.published_time)
            self.assertEqual(result.get('description'), item.description)
            self.assertEqual(result.get('modified'), item.modified.isoformat().replace('+00:00', 'Z'))

    def test_filter_feed_items_by_state(self):

        response = self.client.get(
            self.feed_items_api + "?state=UNREAD"
        )
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertEqual(response.get('count'), len(self.unread_feed_items))
        # validate it's ordered by the modified field
        results = response.get('results')
        for i, _ in enumerate(results):
            if i < len(self.unread_feed_items) - 1:
                self.assertTrue(results[i].get('modified') > results[i + 1].get('modified'))

        response = self.client.get(
            self.feed_items_api + "?state=READ"
        )
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertEqual(response.get('count'), len(self.read_feed_items))
        # validate it's ordered by the modified field
        results = response.get('results')
        for i, _ in enumerate(results):
            if i < len(self.read_feed_items) - 1:
                self.assertTrue(results[i].get('modified') > results[i + 1].get('modified'))

    def test_retrieve_feed_item(self):
        response = self.client.get(
            self.feed_items_api + "{}/".format(self.unread_feed_items[0].id)
        )
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertEqual(len(response.keys()), 7)
        item = Item.objects.get(id=response.get('id'))
        self.assertIn(item, self.unread_feed_items)
        self.assertEqual(response.get('feed'), item.feed_id)
        self.assertEqual(response.get('title'), item.title)
        self.assertEqual(response.get('link'), item.link)
        self.assertEqual(response.get('published_time'), item.published_time)
        self.assertEqual(response.get('description'), item.description)
        self.assertEqual(response.get('modified'), item.modified.isoformat().replace('+00:00', 'Z'))

    def test_list_all_items(self):
        response = self.client.get(
            self.items_api
        )
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertEqual(
            response.get('count'),
            len(self.unread_feed_items) + len(self.read_feed_items) + len(self.unread_items) + len(self.read_items))
        for result in response.get('results'):
            self.assertEqual(len(result.keys()), 7)
            item = Item.objects.get(id=result.get('id'))
            self.assertIn(item, self.unread_feed_items + self.read_feed_items + self.unread_items + self.read_items)
            self.assertEqual(result.get('feed'), item.feed_id)
            self.assertEqual(result.get('title'), item.title)
            self.assertEqual(result.get('link'), item.link)
            self.assertEqual(result.get('published_time'), item.published_time)
            self.assertEqual(result.get('description'), item.description)
            self.assertEqual(result.get('modified'), item.modified.isoformat().replace('+00:00', 'Z'))

    def test_filter_all_items_by_state(self):
        response = self.client.get(
            self.items_api + "?state=UNREAD"
        )
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertEqual(
            response.get('count'),
            len(self.unread_feed_items) + len(self.unread_items))
        # validate it's ordered by the modified field
        results = response.get('results')
        for i, _ in enumerate(results):
            if i < len(self.unread_feed_items) + len(self.unread_items) - 1:
                self.assertTrue(results[i].get('modified') > results[i + 1].get('modified'))

        response = self.client.get(
            self.items_api + "?state=READ"
        )
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertEqual(
            response.get('count'),
            len(self.read_feed_items) + len(self.read_items))
        # validate it's ordered by the modified field
        results = response.get('results')
        for i, _ in enumerate(results):
            if i < len(self.read_feed_items) + len(self.read_items) - 1:
                self.assertTrue(results[i].get('modified') > results[i + 1].get('modified'))

    def test_retrieve_item_globally(self):
        response = self.client.get(
            self.items_api + "{}/".format(self.unread_items[0].id)
        )
        self.assertEqual(response.status_code, 200)
        response = response.json()
        self.assertEqual(len(response.keys()), 7)
        item = Item.objects.get(id=response.get('id'))
        self.assertIn(item, self.unread_feed_items + self.unread_items)
        self.assertEqual(response.get('feed'), item.feed_id)
        self.assertEqual(response.get('title'), item.title)
        self.assertEqual(response.get('link'), item.link)
        self.assertEqual(response.get('published_time'), item.published_time)
        self.assertEqual(response.get('description'), item.description)
        self.assertEqual(response.get('modified'), item.modified.isoformat().replace('+00:00', 'Z'))

    def test_mark_items_as_read(self):
        item = self.unread_items[0]
        item2 = self.unread_feed_items[0]
        self.assertEqual(item.state, Item.STATE_CHOICES.UNREAD)
        self.assertEqual(item2.state, Item.STATE_CHOICES.UNREAD)
        data = {
            "ids": [item.id, item2.id]
        }
        response = self.client.post(
            self.items_api + "read/",
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        response = response.json()
        item.refresh_from_db()
        item2.refresh_from_db()
        self.assertEqual(item.state, Item.STATE_CHOICES.READ)
        self.assertEqual(item2.state, Item.STATE_CHOICES.READ)

    def test_mark_items_as_read_with_mix_of_state(self):
        item = self.unread_items[0]
        item2 = self.read_feed_items[0]
        data = {
            "ids": [item.id, item2.id]
        }
        response = self.client.post(
            self.items_api + "read/",
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        response = response.json()
        self.assertEqual(response.get('ids'), ["Some ids not found or its state is not correct"])

    def test_mark_items_as_read_with_non_existing_ids(self):
        item = self.unread_items[0]
        item2 = self.unread_feed_items[0]
        data = {
            "ids": [item.id, item2.id, 12345]
        }
        response = self.client.post(
            self.items_api + "read/",
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        response = response.json()
        self.assertEqual(response.get('ids'), ["Some ids not found or its state is not correct"])

    def test_mark_items_as_read_with_empty_payload(self):
        data = {}
        response = self.client.post(
            self.items_api + "read/",
            data=json.dumps(data),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 400)
        response = response.json()
        self.assertEqual(response.get('ids'), ['This field is required.'])
