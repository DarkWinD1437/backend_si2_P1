from django.urls import path
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from . import views

# Vista para el endpoint /me/ - Obtiene datos REALES del usuario
class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        user = request.user
        return Response({
            'id': user.id,
            'username': user.username,
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'is_superuser': user.is_superuser,
            'is_staff': user.is_staff,
            # Rol basado en lógica simple (puedes mejorarlo después)
            'role': 'admin' if user.is_superuser else 'resident'
        })

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='api_login'),
    path('me/', UserProfileView.as_view(), name='user-me'),
]