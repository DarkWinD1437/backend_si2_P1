from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Crear router para ViewSets
router = DefaultRouter()
router.register(r'rostros', views.RostroRegistradoViewSet, basename='rostros')
router.register(r'vehiculos', views.VehiculoRegistradoViewSet, basename='vehiculos')
router.register(r'accesos', views.AccesoViewSet, basename='accesos')

# URLs específicas para funcionalidades de IA
urlpatterns = [
    # Incluir rutas del router
    path('', include(router.urls)),

    # Endpoints de IA
    path('reconocimiento-facial/', views.reconocimiento_facial, name='reconocimiento-facial'),
    path('lectura-placa/', views.lectura_placa, name='lectura-placa'),
    path('login-facial/', views.login_facial, name='login-facial'),
]