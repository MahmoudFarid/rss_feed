from django.urls import include, path

app_name = "api"

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('auth/', include('djoser.urls')),
    path('feeds/', include('rss_feed.feeds.routers')),
]
