from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    UserViewSet, 
    UserRegistrationView, 
    UserLogoutView,
    UserProfileView,
    UserPasswordChangeView,
    UserProfilePictureView,
    CustomTokenObtainPairView  # ← Vista personalizada
)

router = DefaultRouter()
router.register(r'users', UserViewSet)

urlpatterns = [
    # Endpoint específico para registro
    path('register/', UserRegistrationView.as_view(), name='user-register'),
    # Endpoint específico para logout
    path('logout/', UserLogoutView.as_view(), name='user-logout'),
    
    # Endpoints para gestión de perfil
    path('profile/', UserProfileView.as_view(), name='user-profile'),
    path('profile/change-password/', UserPasswordChangeView.as_view(), name='user-change-password'),
    path('profile/picture/', UserProfilePictureView.as_view(), name='user-profile-picture'),
    
    # ViewSet URLs
    path('', include(router.urls)),
    # JWT token URLs - Usar vista personalizada
    path('token/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),  # ← Vista personalizada
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
