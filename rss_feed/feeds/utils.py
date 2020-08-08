import logging
from datetime import datetime
from time import mktime

from django.core.mail import send_mail
from django.utils import timezone

import feedparser

from .models import Item

logger = logging.getLogger(__name__)


def parse_rss_link(link):
    '''
    Parameters:
        link (URL): Any xml url that need to be parsed.

    Returns:
        parsed (dict): Parsed object for this RSS link.
    '''
    return feedparser.parse(link)


def prepare_feed_fields(feed):
    '''
    Prepare Feed fields based scraped feed attrs

    Parameters:
        feed (dict): Object from feedparser.FeedParserDict

    Returns:
        fields (dict): All needed fields to create a Feed object
    '''
    fields = {
        "title": feed.get('title'),
        "link": feed.get('link'),
        "description": feed.get('subtitle'),
    }
    if feed.get('image'):
        fields['image'] = feed.get('image').get('href')
    return fields


def get_entry_published_time(entry):
    '''
    Try to parse published_time from the scraped item data from published_parsed attr.
    In case we can't parse this value, will try to parse published attr.

    Parameters:
        entry (dict): Object from feedparser.FeedParserDict

    Returns:
        published_time (datetime)(option): parsed datetime obj or None
    '''
    published_time = None
    try:
        published_time = datetime.fromtimestamp(mktime(entry.get("published_parsed")))
    except TypeError:
        try:
            logger.warning("Can't parse published_parsed value > %s" % (entry.get("published_parsed")))
            published_time = datetime.strptime(entry.get("published"), "%a, %d %b %Y %H:%M:%S GMT")
        except (ValueError, TypeError):
            logger.warning("Can't parse published value > %s" % (entry.get("published")))

    return published_time


def prepare_feed_item_fields(entry):
    '''
    Prepare Item fields based scraped item attrs

    Parameters:
        entry (dict): Object from feedparser.FeedParserDict

    Returns:
        fields (dict): All needed fields to create an Item object
    '''
    fields = {
        "title": entry.get('title'),
        "link": entry.get('link'),
        "description": entry.get('summary'),
        "published_time": get_entry_published_time(entry)
    }
    return fields


def update_feeds_and_items(feed, parsed):
    '''
    Update feed object with its items based on the scraped data.
    Will create new items if it's not exists or update the existing ones.

    Parameters:
        feed (obj): Feed object
        parsed (dict): Object from feedparser.parse

    Returns:
        fields (dict): All needed fields to create an Item object
    '''
    for field, value in prepare_feed_fields(parsed.get('feed')).items():
        setattr(feed, field, value)
    feed.last_update = timezone.now()
    feed.save()

    total_item_created = 0
    for item in parsed.get('entries'):
        fields = prepare_feed_item_fields(item)
        fields['last_update'] = timezone.now()
        _, created = Item.objects.update_or_create(link=fields.pop('link'), feed=feed, defaults=fields)
        if created:
            total_item_created += 1
    return total_item_created


def send_notification_to_user(feed):
    '''
    Send email notification to the user

    Parameters:
        feed (obj): Feed object

    Returns:
        (bool): Success or Failure
    '''
    return send_mail(
        'Feed Auto Update Failed!',
        'This Feed: %s will not be auto updated due to some errors.' % (feed.xml_url),
        'noreply@example.com',
        [feed.created_by.email],
        fail_silently=False,
    )
