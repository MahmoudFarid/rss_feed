from django.urls import include, path

app_name = "api"

urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('auth/', include('djoser.urls')),
]
