from django.urls import path
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
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
            'role': getattr(user, 'role', 'admin' if user.is_superuser else 'resident'),
            'phone': getattr(user, 'phone', ''),
            'address': getattr(user, 'address', ''),
            'profile_picture': user.profile_picture.url if hasattr(user, 'profile_picture') and user.profile_picture else None,
            'date_joined': user.date_joined
        })

# Vista para obtener todos los usuarios (solo admin)
class UsersListView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        if not request.user.is_superuser:
            return Response({'error': 'No tienes permisos'}, status=status.HTTP_403_FORBIDDEN)
        
        from backend.apps.users.models import User
        users = User.objects.all()
        users_data = []
        
        for user in users:
            users_data.append({
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'role': user.get_role_display(),
                'is_active': user.is_active,
                'date_joined': user.date_joined
            })
        
        return Response({'users': users_data, 'count': len(users_data)})

# Vista de status de la API
class APIStatusView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request):
        return Response({
            'status': 'ok',
            'message': 'Smart Condominium API funcionando correctamente',
            'version': '1.0',
            'endpoints': {
                'login': '/api/login/',
                'logout': '/api/logout/',
                'logout_all': '/api/logout-all/',
                'profile': '/api/me/',
                'profile_full': '/api/profile/',
                'change_password': '/api/profile/change-password/',
                'profile_picture': '/api/profile/picture/',
                'users': '/api/users/',
                'assign_role': '/api/users/<user_id>/assign-role/',
                'status': '/api/status/'
            }
        })

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='api_login'),
    path('logout/', views.LogoutView.as_view(), name='api_logout'),
    path('logout-all/', views.LogoutAllView.as_view(), name='api_logout_all'),
    path('me/', UserProfileView.as_view(), name='user-me'),
    path('users/', UsersListView.as_view(), name='users-list'),
    path('users/<int:user_id>/assign-role/', views.AssignRoleView.as_view(), name='assign-role'),
    path('status/', APIStatusView.as_view(), name='api-status'),
]