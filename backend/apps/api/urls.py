from django.urls import path
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from . import views
from .populate_views import populate_database
from .database_status_views import database_status

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
    
    def put(self, request):
        """Actualizar perfil del usuario"""
        user = request.user
        data = request.data
        
        # Campos que se pueden actualizar
        allowed_fields = ['first_name', 'last_name', 'email', 'phone', 'address']
        
        try:
            updated = False
            for field in allowed_fields:
                if field in data:
                    setattr(user, field, data[field])
                    updated = True
            
            if updated:
                user.save()
                return Response({
                    'success': True,
                    'message': 'Perfil actualizado exitosamente',
                    'user': {
                        'id': user.id,
                        'username': user.username,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'phone': getattr(user, 'phone', ''),
                        'address': getattr(user, 'address', ''),
                        'role': getattr(user, 'role', 'resident')
                    }
                })
            else:
                return Response({
                    'success': False,
                    'message': 'No se encontraron campos para actualizar'
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            return Response({
                'success': False,
                'message': 'Error al actualizar perfil',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    def patch(self, request):
        """Actualización parcial del perfil"""
        return self.put(request)

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        user = request.user
        data = request.data
        
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        confirm_password = data.get('confirm_password')
        
        if not current_password or not new_password or not confirm_password:
            return Response({
                'success': False,
                'message': 'Todos los campos de contraseña son requeridos'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar contraseña actual
        if not user.check_password(current_password):
            return Response({
                'success': False,
                'message': 'La contraseña actual es incorrecta'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar que las nuevas contraseñas coincidan
        if new_password != confirm_password:
            return Response({
                'success': False,
                'message': 'Las nuevas contraseñas no coinciden'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Validar fortaleza de la nueva contraseña
        if len(new_password) < 8:
            return Response({
                'success': False,
                'message': 'La nueva contraseña debe tener al menos 8 caracteres'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            user.set_password(new_password)
            user.save()
            
            return Response({
                'success': True,
                'message': 'Contraseña cambiada exitosamente'
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'message': 'Error al cambiar la contraseña',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

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
    path('profile/change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('users/', UsersListView.as_view(), name='users-list'),
    path('users/<int:user_id>/assign-role/', views.AssignRoleView.as_view(), name='assign-role'),
    path('status/', APIStatusView.as_view(), name='api-status'),
    path('populate/', populate_database, name='populate-database'),  # Poblar BD
    path('db-status/', database_status, name='database-status'),    # Verificar BD
]