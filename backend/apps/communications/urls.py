from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AvisoViewSet

# Router para los ViewSets
router = DefaultRouter()
router.register(r'avisos', AvisoViewSet, basename='aviso')

urlpatterns = [
    path('api/communications/', include(router.urls)),
]