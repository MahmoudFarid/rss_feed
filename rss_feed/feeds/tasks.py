import json
import logging

from django.conf import settings

from celery import group, shared_task
from celery.exceptions import MaxRetriesExceededError

from .models import Feed
from .utils import parse_rss_link, send_notification_to_user, update_feeds_and_items
from .validators import validate_rss_link

logger = logging.getLogger(__name__)


@shared_task
def periodic_update_feeds_and_items():
    # only update any feed that followed by any user or auto updated
    feeds_ids = Feed.objects.filter(is_followed=True, is_auto_updated=True).values_list('id', flat=True)
    group(update_multiple_feeds_in_parallel.s(feed_id) for feed_id in feeds_ids).apply_async()


@shared_task(default_retry_delay=settings.RETRY_DELAY_IN_SECONDS, max_retries=settings.MAX_RETRY_FEED_UPDATE)
def update_multiple_feeds_in_parallel(feed_id):
    feed = Feed.objects.get(id=feed_id)
    parsed = parse_rss_link(feed.xml_url)
    error = validate_rss_link(parsed)
    if error:
        try:
            logger.warning(error)
            update_multiple_feeds_in_parallel.retry()
        except MaxRetriesExceededError as e:
            feed.is_auto_updated = False
            feed.save()
            send_notification_to_user(feed)
            logger.error("Can't auto update Feed: {}".format(feed.xml_url))
            raise e

    total_item_created = update_feeds_and_items(feed, parsed)

    return json.dumps({'detail': 'Updated Feed: {}, Adding {} new items'.format(feed.xml_url, total_item_created)})
