from django.core import mail
from django.test import TestCase

from rss_feed.feeds.tests.factories import FeedFactory

from ..utils import send_notification_to_user


class TestTasks(TestCase):

    def test_send_notification_to_user(self):
        feed = FeedFactory()
        send_notification_to_user(feed)
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject, 'Feed Auto Update Failed!')
        self.assertEqual(mail.outbox[0].to[0], feed.created_by.email)
        self.assertIn("will not be auto updated due to some errors.", mail.outbox[0].body)
