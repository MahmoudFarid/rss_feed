
from rest_framework.routers import SimpleRouter

from .views import FeedViewSet

app_name = "feeds"

router = SimpleRouter()
router.register('', FeedViewSet, basename='feeds')


urlpatterns = [

] + router.urls
