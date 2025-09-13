from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model
from .serializers import (
    UserSerializer, 
    UserCreateSerializer, 
    UserUpdateSerializer,
    UserPasswordChangeSerializer,
    UserProfilePictureSerializer
)

User = get_user_model()

class UserRegistrationView(APIView):
    """
    Vista específica para registro de usuarios
    Compatible con React y Flutter
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Crear token para autenticación
            token, _ = Token.objects.get_or_create(user=user)
            
            # Crear tokens JWT
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'success': True,
                'message': 'Usuario registrado exitosamente',
                'user': {
                    'id': user.id,
                    'username': user.username,
                    'email': user.email,
                    'first_name': user.first_name,
                    'last_name': user.last_name,
                    'role': user.role
                },
                'tokens': {
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'token': token.key  # Para compatibilidad con Token auth
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'message': 'Error en el registro',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class UserProfileView(APIView):
    """
    Vista completa para gestión de perfil de usuario
    GET: Obtener perfil
    PUT/PATCH: Actualizar perfil
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        """Obtener perfil del usuario actual"""
        serializer = UserSerializer(request.user)
        return Response({
            'success': True,
            'user': serializer.data
        })
    
    def put(self, request):
        """Actualizar perfil completo (PUT)"""
        serializer = UserUpdateSerializer(request.user, data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'success': True,
                'message': 'Perfil actualizado exitosamente',
                'user': UserSerializer(user).data
            })
        return Response({
            'success': False,
            'message': 'Error al actualizar perfil',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def patch(self, request):
        """Actualizar perfil parcial (PATCH)"""
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'success': True,
                'message': 'Perfil actualizado exitosamente',
                'user': UserSerializer(user).data
            })
        return Response({
            'success': False,
            'message': 'Error al actualizar perfil',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class UserPasswordChangeView(APIView):
    """
    Vista para cambio de contraseña
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = UserPasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            # Cambiar la contraseña
            user = request.user
            new_password = serializer.validated_data['new_password']
            user.set_password(new_password)
            user.save()
            
            # Invalidar todos los tokens existentes para forzar re-login
            Token.objects.filter(user=user).delete()
            
            return Response({
                'success': True,
                'message': 'Contraseña cambiada exitosamente. Debe iniciar sesión nuevamente.',
                'logout_required': True
            })
        return Response({
            'success': False,
            'message': 'Error al cambiar contraseña',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)

class UserProfilePictureView(APIView):
    """
    Vista específica para subir/actualizar foto de perfil
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Subir nueva foto de perfil"""
        serializer = UserProfilePictureSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'success': True,
                'message': 'Foto de perfil actualizada exitosamente',
                'profile_picture': user.profile_picture.url if user.profile_picture else None
            })
        return Response({
            'success': False,
            'message': 'Error al subir foto de perfil',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    def delete(self, request):
        """Eliminar foto de perfil"""
        user = request.user
        if user.profile_picture:
            user.profile_picture.delete()
            user.save()
            return Response({
                'success': True,
                'message': 'Foto de perfil eliminada exitosamente'
            })
        return Response({
            'success': False,
            'message': 'No hay foto de perfil para eliminar'
        }, status=status.HTTP_400_BAD_REQUEST)

class UserLogoutView(APIView):
    """
    Vista de logout específica para usuarios
    Invalida tanto tokens tradicionales como JWT
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            user = request.user
            
            # Eliminar token tradicional
            if hasattr(user, 'auth_token'):
                user.auth_token.delete()
            
            # Para JWT, intentar blacklistear si se proporciona refresh token
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                try:
                    token = RefreshToken(refresh_token)
                    token.blacklist()
                except Exception:
                    # Si falla JWT blacklist, continuar
                    pass
            
            return Response({
                'success': True,
                'message': 'Sesión cerrada exitosamente',
                'detail': 'El usuario ha sido desconectado correctamente'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': 'Error al cerrar sesión',
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return UserUpdateSerializer
        return UserSerializer

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def register(self, request):
        """Método de registro alternativo através del ViewSet"""
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                'user': UserSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Obtener datos del usuario actual"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    @action(detail=False, methods=['put', 'patch'])
    def update_profile(self, request):
        """Actualizar perfil del usuario actual"""
        partial = request.method == 'PATCH'
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=partial)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'success': True,
                'message': 'Perfil actualizado exitosamente',
                'user': UserSerializer(user).data
            })
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def change_password(self, request):
        """Cambiar contraseña del usuario actual"""
        serializer = UserPasswordChangeSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            user = request.user
            new_password = serializer.validated_data['new_password']
            user.set_password(new_password)
            user.save()
            
            # Invalidar tokens existentes
            Token.objects.filter(user=user).delete()
            
            return Response({
                'success': True,
                'message': 'Contraseña cambiada exitosamente',
                'logout_required': True
            })
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def logout(self, request):
        """Logout del usuario actual"""
        try:
            # Eliminar token del usuario actual
            if hasattr(request.user, 'auth_token'):
                request.user.auth_token.delete()
            
            return Response({
                'success': True,
                'message': 'Logout exitoso desde ViewSet'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': 'Error en logout',
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def assign_role(self, request, pk=None):
        """Asignar rol a un usuario (solo para administradores)"""
        # Verificar que el usuario actual es administrador
        if not (request.user.is_superuser or request.user.role == 'admin'):
            return Response({
                'success': False,
                'message': 'No tienes permisos para asignar roles',
                'error': 'Acceso denegado'
            }, status=status.HTTP_403_FORBIDDEN)
        
        try:
            # Obtener el usuario al que se le asignará el rol
            user = self.get_object()
            
            # Obtener el nuevo rol
            new_role = request.data.get('role')
            if not new_role:
                return Response({
                    'success': False,
                    'message': 'Debe especificar un rol',
                    'error': 'Rol requerido'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Validar que el rol sea válido
            valid_roles = [choice[0] for choice in User.ROLE_CHOICES]
            if new_role not in valid_roles:
                return Response({
                    'success': False,
                    'message': f'Rol inválido. Roles válidos: {", ".join(valid_roles)}',
                    'error': 'Rol inválido',
                    'valid_roles': valid_roles
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Guardar el rol anterior para el log
            old_role = user.role
            
            # Asignar el nuevo rol
            user.role = new_role
            
            # Si el rol es admin, configurar permisos de staff
            if new_role == 'admin':
                user.is_staff = True
                user.is_superuser = True
            else:
                # Solo quitar permisos si no es superuser original
                if not user.is_superuser:
                    user.is_staff = False
                    user.is_superuser = False
            
            user.save()
            
            # Log de la acción (opcional - si tienes sistema de auditoría)
            # self.log_role_change(request.user, user, old_role, new_role)
            
            return Response({
                'success': True,
                'message': f'Rol asignado exitosamente de "{old_role}" a "{new_role}"',
                'user': UserSerializer(user).data,
                'role_change': {
                    'previous_role': old_role,
                    'new_role': new_role,
                    'changed_by': request.user.username,
                    'changed_at': user.updated_at
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
