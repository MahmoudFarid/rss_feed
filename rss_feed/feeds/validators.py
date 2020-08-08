import logging

logger = logging.getLogger(__name__)


def validate_rss_link(parsed):
    '''
    Returns an error in case an Exception raised during the validation.

    Parameters:
        parsed (dict): Object from feedparser.parse

    Returns:
        error (str)(option): The error message
    '''
    try:
        validate_feed_attrs(parsed)
        validate_feed_items_attrs(parsed)
        return None
    except Exception as e:
        return e


def validate_feed_attrs(parsed):
    '''
    Validate the feed that has all the required attrs.

    Parameters:
        parsed (dict): Object from feedparser.parse

    Returns:
        error (Exception)(option): The error message
    '''
    if 'bozo_exception' in parsed:
        # Malformed feed
        msg = 'Found Malformed feed, "%s": %s' % (parsed.get('href'), parsed.get('bozo_exception'))
        logger.warning(msg)
        raise Exception(msg)

    errors = []
    feed = parsed.get('feed')
    for attr in ['title', 'subtitle', 'link']:
        if attr not in feed:
            msg = 'Feed "%s" has no %s' % (parsed.get('href'), attr)
            logger.error(msg)
            errors.append(msg)

    if errors:
        raise Exception(errors)


def validate_feed_items_attrs(parsed):
    '''
    - Validate the feed items that have all the required attrs.
    - Will ignore any item missed any attr.
    - In case no valid items will raise an exception otherwise will not raise an exception
        and will override the parsed items with the valid one.

    Parameters:
        parsed (dict): Object from feedparser.parse

    Returns:
        error (Exception)(option): The error message
    '''
    missing_attrs = []
    valid_entries = []
    for entry in parsed.get('entries'):
        is_valid_entry = True
        for attr in ['title', 'link', 'summary']:
            if attr not in entry:
                msg = 'Item "%s" has no %s' % (entry.get('link'), attr)
                logger.error(msg)
                missing_attrs.append(attr)
                is_valid_entry = False

        if is_valid_entry:
            valid_entries.append(entry)

    if valid_entries:
        parsed['entries'] = valid_entries
    else:
        raise Exception('All items missing some of these attrs: %s' % set(missing_attrs))
