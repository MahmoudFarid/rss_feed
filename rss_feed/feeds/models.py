from django.conf import settings
from django.db import models
from django.utils.translation import ugettext_lazy as _

from model_utils import Choices
from model_utils.models import TimeStampedModel


class Feed(TimeStampedModel):
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='feeds')
    title = models.TextField()
    xml_url = models.URLField()
    link = models.URLField()
    description = models.TextField()
    image = models.ImageField(null=True, blank=True)

    def __str__(self):
        return self.title


class Item(TimeStampedModel):
    STATE_CHOICES = Choices(
        (1, 'UNREAD', _('Unread')),
        (2, 'READ', _('Read')),
        (3, 'SAVED', _('Saved')),
    )
    feed = models.ForeignKey("Feed", on_delete=models.CASCADE, related_name='items')
    title = models.TextField()
    link = models.URLField()
    published_time = models.DateTimeField(null=True, blank=True)
    description = models.TextField()
    state = models.IntegerField(choices=STATE_CHOICES, default=STATE_CHOICES.UNREAD)

    class Meta:
        ordering = ['-modified']

    def __str__(self):
        return self.title
