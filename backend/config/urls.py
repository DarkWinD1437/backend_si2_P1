"""URL Configuration for Smart Condominium project."""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

api_v1_patterns = [
    path('users/', include('apps.users.urls')),
    path('finances/', include('apps.finances.urls')),
    path('security/', include('apps.security.urls')),
    path('communications/', include('apps.communications.urls')),
    path('reservations/', include('apps.reservations.urls')),
    path('maintenance/', include('apps.maintenance.urls')),
    path('analytics/', include('apps.analytics.urls')),
]

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/v1/', include(api_v1_patterns)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += [path('__debug__/', include('debug_toolbar.urls'))]
