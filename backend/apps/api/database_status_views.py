"""
Vista para verificar estado de la base de datos
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from backend.apps.users.models import User
from backend.apps.condominio.models import Rol, Usuario, AreaComun, Aviso

User = get_user_model()

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def database_status(request):
    """
    Endpoint para verificar el estado de la base de datos
    Muestra conteos de todos los modelos principales
    """
    if not request.user.is_superuser:
        return Response({
            'error': 'Solo administradores pueden ver esta información'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        # Conteos de usuarios
        total_users = User.objects.count()
        admin_users = User.objects.filter(is_superuser=True).count()
        staff_users = User.objects.filter(is_staff=True).count()
        
        # Conteos por rol
        admin_role = User.objects.filter(role='admin').count()
        conserje_role = User.objects.filter(role='conserje').count()
        residente_role = User.objects.filter(role='residente').count()
        
        # Conteos de modelos del condominio
        total_roles = 0
        total_usuarios_old = 0
        total_areas = 0
        total_avisos = 0
        
        try:
            total_roles = Rol.objects.count()
        except:
            total_roles = 0
            
        try:
            total_usuarios_old = Usuario.objects.count()
        except:
            total_usuarios_old = 0
            
        try:
            total_areas = AreaComun.objects.count()
        except:
            total_areas = 0
            
        try:
            total_avisos = Aviso.objects.count()
        except:
            total_avisos = 0
        
        # Lista de usuarios recientes
        recent_users = []
        for user in User.objects.all().order_by('-date_joined')[:10]:
            recent_users.append({
                'username': user.username,
                'email': user.email,
                'role': getattr(user, 'role', 'No definido'),
                'date_joined': user.date_joined,
                'is_superuser': user.is_superuser
            })
        
        result = {
            'database_status': 'OK',
            'timestamp': '2025-09-14',
            'usuarios_sistema': {
                'total': total_users,
                'administradores': admin_users,
                'staff': staff_users,
                'por_rol': {
                    'admin': admin_role,
                    'conserje': conserje_role,
                    'residente': residente_role
                }
            },
            'modelos_condominio': {
                'roles': total_roles,
                'usuarios_old_model': total_usuarios_old,
                'areas_comunes': total_areas,
                'avisos': total_avisos
            },
            'usuarios_recientes': recent_users,
            'poblacion_detectada': {
                'tiene_usuarios_adicionales': total_users > 1,
                'tiene_roles': total_roles > 0,
                'tiene_areas_comunes': total_areas > 0,
                'tiene_avisos': total_avisos > 0,
                'estado_general': 'POBLADO' if (total_users > 1 and total_areas > 0) else 'VACÍO'
            }
        }
        
        return Response(result, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'error': f'Error al verificar la base de datos: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)