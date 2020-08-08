from unittest import mock

from django.test import TestCase
from django.utils import timezone

from celery.exceptions import MaxRetriesExceededError, Retry
from pytest import raises

from ..tasks import periodic_update_feeds_and_items
from ..utils import prepare_feed_fields
from .factories import FeedFactory, ItemFactory
from .mocking import correct_result, missing_feed_attrs

FAKE_DATE = timezone.make_aware(
    timezone.datetime(2018, 1, 1),
    timezone=timezone.utc
)


class TestTasks(TestCase):

    def setUp(self):
        self.feed = FeedFactory(is_followed=True, is_auto_update=True)
        ItemFactory.create_batch(4, feed=self.feed)
        self.not_followed_feed = FeedFactory(is_followed=False, is_auto_update=True)
        ItemFactory.create_batch(3, feed=self.not_followed_feed)
        self.not_auto_updated_feed = FeedFactory(is_followed=True, is_auto_update=False)
        ItemFactory.create_batch(2, feed=self.not_auto_updated_feed)

    @mock.patch('rss_feed.feeds.tasks.parse_rss_link', return_value=correct_result)
    @mock.patch('rss_feed.feeds.tasks.send_notification_to_user')
    @mock.patch('django.utils.timezone.now', return_value=FAKE_DATE)
    def test_periodic_update_feeds_and_items_with_correct_results(self, _, mock_send_notification, mocked_parser):
        self.assertEqual(mocked_parser.call_count, 0)
        self.assertEqual(mock_send_notification.call_count, 0)

        self.assertTrue(self.feed.is_auto_update)
        self.assertNotEqual(self.feed.last_update, FAKE_DATE)
        # before run the task, the existing feed will not equal the mocked data
        fields = prepare_feed_fields(correct_result.get('feed'))
        for key, value in fields.items():
            self.assertNotEqual(getattr(self.feed, key), value)
        self.assertEqual(self.feed.items.count(), 4)

        periodic_update_feeds_and_items.delay()
        # validate it calls one time only, that's mean it run only for self.feed and not other feeds
        self.assertEqual(mocked_parser.call_count, 1)
        self.assertEqual(mock_send_notification.call_count, 0)

        self.feed.refresh_from_db()
        self.assertTrue(self.feed.is_auto_update)
        self.assertEqual(self.feed.last_update, FAKE_DATE)
        # after run the task, the existing feed will be updated to the mocked data
        fields = prepare_feed_fields(correct_result.get('feed'))
        for key, value in fields.items():
            self.assertEqual(getattr(self.feed, key), value)
        self.assertEqual(self.feed.items.count(), 7)  # add new 3 items from the mock

    @mock.patch('rss_feed.feeds.tasks.parse_rss_link', return_value=missing_feed_attrs)
    @mock.patch('rss_feed.feeds.tasks.update_multiple_feeds_in_parallel.retry')
    def test_periodic_update_feeds_and_items_with_invalid_data_with_raising_retry_exception(
            self, task_retry, mocked_parser):

        self.assertTrue(self.feed.is_auto_update)
        self.assertEqual(mocked_parser.call_count, 0)
        task_retry.side_effect = Retry()

        with raises(Retry):
            periodic_update_feeds_and_items.delay()
        self.assertEqual(mocked_parser.call_count, 1)
        self.assertTrue(self.feed.is_auto_update)

    @mock.patch('rss_feed.feeds.tasks.parse_rss_link', return_value=missing_feed_attrs)
    @mock.patch('rss_feed.feeds.tasks.update_multiple_feeds_in_parallel.retry')
    @mock.patch('rss_feed.feeds.tasks.send_notification_to_user')
    def test_periodic_update_feeds_and_items_with_invalid_data_with_raising_max_retry_exception(
            self, mock_send_notification, task_retry, mocked_parser):

        task_retry.side_effect = MaxRetriesExceededError()
        self.assertTrue(self.feed.is_auto_update)
        self.assertEqual(mocked_parser.call_count, 0)
        self.assertEqual(mock_send_notification.call_count, 0)

        with raises(MaxRetriesExceededError):
            periodic_update_feeds_and_items.delay()

        self.feed.refresh_from_db()
        self.assertEqual(mocked_parser.call_count, 1)
        self.assertEqual(mock_send_notification.call_count, 1)
        self.assertFalse(self.feed.is_auto_update)
