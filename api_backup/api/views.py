from django.contrib.auth import authenticate, get_user_model
from rest_framework.decorators import api_view, permission_classes
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token
from rest_framework import status

User = get_user_model()

try:
    from rest_framework_simplejwt.tokens import RefreshToken
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False

class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        
        if username is None or password is None:
            return Response({
                'error': 'Por favor proporcione usuario y contraseña'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = authenticate(username=username, password=password)
        
        if not user:
            return Response({
                'error': 'Credenciales inválidas'
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        token, _ = Token.objects.get_or_create(user=user)
        
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'username': user.username,
            'is_superuser': user.is_superuser
        })

class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Eliminar el token de autenticación tradicional
            if hasattr(request.user, 'auth_token'):
                request.user.auth_token.delete()
            
            # Para JWT, intentar blacklistear el refresh token si se proporciona
            refresh_token = request.data.get('refresh_token')
            if refresh_token and JWT_AVAILABLE:
                try:
                    token = RefreshToken(refresh_token)
                    token.blacklist()
                except Exception as e:
                    # Si hay error con JWT, continuar con logout tradicional
                    pass
            
            return Response({
                'message': 'Logout exitoso',
                'success': True
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': 'Error durante el logout',
                'success': False
            }, status=status.HTTP_400_BAD_REQUEST)

class LogoutAllView(APIView):
    """
    Endpoint para cerrar todas las sesiones del usuario
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            
            # Eliminar todos los tokens de autenticación tradicional
            Token.objects.filter(user=user).delete()
            
            return Response({
                'message': 'Logout de todas las sesiones exitoso',
                'success': True
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'error': 'Error durante el logout general',
                'success': False
            }, status=status.HTTP_400_BAD_REQUEST)

class AssignRoleView(APIView):
    """
    Vista específica para asignación de roles en la API principal
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        """Asignar rol a un usuario"""
        # Verificar que el usuario actual es administrador
        if not (request.user.is_superuser or getattr(request.user, 'role', None) == 'admin'):
            return Response({
                'success': False,
                'message': 'No tienes permisos para asignar roles',
                'error': 'Acceso denegado'
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            # Obtener el usuario al que se le asignará el rol
            user = User.objects.get(id=user_id)
            
            # Obtener el nuevo rol
            new_role = request.data.get('role')
            if not new_role:
                return Response({
                    'success': False,
                    'message': 'Debe especificar un rol',
                    'error': 'Rol requerido'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validar que el rol sea válido
            valid_roles = ['admin', 'resident', 'security']
            if hasattr(User, 'ROLE_CHOICES'):
                valid_roles = [choice[0] for choice in User.ROLE_CHOICES]
            
            if new_role not in valid_roles:
                return Response({
                    'success': False,
                    'message': f'Rol inválido. Roles válidos: {", ".join(valid_roles)}',
                    'error': 'Rol inválido',
                    'valid_roles': valid_roles
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Guardar el rol anterior para el log
            old_role = getattr(user, 'role', 'resident')
            
            # Asignar el nuevo rol
            user.role = new_role
            
            # Si el rol es admin, configurar permisos de staff
            if new_role == 'admin':
                user.is_staff = True
                user.is_superuser = True
            elif old_role == 'admin' and new_role != 'admin':
                # Solo quitar permisos si era admin antes
                user.is_staff = False
                user.is_superuser = False
            
            user.save()
            
            return Response({
                'success': True,
                'message': f'Rol asignado exitosamente de "{old_role}" a "{new_role}"',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': user.role,
                    'is_staff': user.is_staff,
                    'is_superuser': user.is_superuser
                },
                'role_change': {
                    'previous_role': old_role,
                    'new_role': new_role,
                    'changed_by': request.user.username
                }
            }, status=status.HTTP_200_OK)
            
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Usuario no encontrado',
                'error': 'Usuario inexistente'
            }, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({
                'success': False,
                'message': 'Error al asignar rol',
                'error': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
