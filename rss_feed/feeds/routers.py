
from rest_framework.routers import SimpleRouter

from .views import FeedViewSet, ItemViewSet

app_name = "feeds"

router = SimpleRouter()
router.register('items', ItemViewSet, basename='items')
router.register('(?P<feed_id>\d+)/items', ItemViewSet, basename='feed_items')
router.register('', FeedViewSet, basename='feeds')

urlpatterns = [

] + router.urls
