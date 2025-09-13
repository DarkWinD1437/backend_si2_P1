from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RegistroAuditoriaViewSet, SesionUsuarioViewSet, EstadisticasAuditoriaViewSet

# Crear router para las APIs
router = DefaultRouter()
router.register(r'registros', RegistroAuditoriaViewSet, basename='registros-auditoria')
router.register(r'sesiones', SesionUsuarioViewSet, basename='sesiones-usuario')
router.register(r'estadisticas', EstadisticasAuditoriaViewSet, basename='estadisticas-auditoria')

urlpatterns = [
    path('', include(router.urls)),
]