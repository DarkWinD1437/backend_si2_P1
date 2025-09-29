from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Crear router para ViewSets
router = DefaultRouter()
router.register(r'dispositivos', views.DispositivoViewSet, basename='dispositivos')
router.register(r'preferencias', views.PreferenciasNotificacionViewSet, basename='preferencias')
router.register(r'notificaciones', views.NotificacionViewSet, basename='notificaciones')

# URLs específicas
urlpatterns = [
    # Incluir rutas del router
    path('', include(router.urls)),

    # Endpoints específicos
    path('enviar-push/', views.enviar_notificacion_push, name='enviar-push'),
    path('crear-notificacion/', views.crear_notificacion, name='crear-notificacion'),

    # Endpoint de prueba (solo para desarrollo)
    path('test/', views.test_notificaciones, name='test-notificaciones'),
]