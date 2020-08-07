import logging
from datetime import datetime
from time import mktime

import feedparser

logger = logging.getLogger(__name__)


def parse_rss_link(link):
    return feedparser.parse(link)


def prepare_feed_fields(feed):

    fields = {
        "title": feed.get('title'),
        "link": feed.get('link'),
        "description": feed.get('subtitle'),
    }
    if feed.get('image'):
        fields['image'] = feed.get('image').get('href')
    return fields


def get_entry_published_time(entry):
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


def prepare_feed_item_fields(entry, feed):
    fields = {
        "feed": feed,
        "title": entry.get('title'),
        "link": entry.get('link'),
        "description": entry.get('summary'),
        "published_time": get_entry_published_time(entry)
    }
    return fields
