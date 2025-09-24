from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

from rest_framework.authtoken.views import obtain_auth_token
from backend.apps.users.views import CustomTokenObtainPairView  # ← Importar vista personalizada

urlpatterns = [
    path('admin/', admin.site.urls),
    # JWT URLs - Usar vista personalizada directamente
    path('api/token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),  # ← Vista directa
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/auth-token/', obtain_auth_token, name='api_token_auth'),
    # API URLs
    path('api/', include('backend.apps.api.urls')),
    # Users URLs (sin duplicar token)
    path('api/', include('backend.apps.users.urls')),  # ← Comentado para evitar duplicación
    # Finances URLs
    path('api/finances/', include('backend.apps.finances.urls')),
    # Communications URLs
    path('', include('backend.apps.communications.urls')),
    # Reservations URLs
    path('api/reservations/', include('backend.apps.reservations.urls')),
    # Audit URLs
    path('api/audit/', include('backend.apps.audit.urls')),
]

# Servir archivos media en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)