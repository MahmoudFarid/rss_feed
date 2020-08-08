from celery.schedules import crontab


def setup_periodic_tasks(app):
    app.conf.beat_schedule = {
        'update-feeds-and-items': {
            'task': 'rss_feed.feeds.tasks.periodic_update_feeds_and_items',
            'schedule': crontab(minute='*/30'),  # every 30 minutes
        }
    }
