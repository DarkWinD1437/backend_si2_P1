from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta, date
from django.contrib.auth import get_user_model

from .models import RegistroAuditoria, SesionUsuario, EstadisticasAuditoria, TipoActividad, NivelImportancia
from .serializers import (
    RegistroAuditoriaSerializer, RegistroAuditoriaListSerializer,
    SesionUsuarioSerializer, EstadisticasAuditoriaSerializer,
    AuditoriaResumenSerializer, FiltroAuditoriaSerializer
)
from .utils import AuditoriaLogger

User = get_user_model()


class IsAdminOrReadOnlyForOwn(permissions.BasePermission):
    """
    Permiso personalizado para auditoría:
    - Los administradores pueden ver todo
    - Los usuarios regulares solo pueden ver sus propios registros de auditoría
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Los administradores tienen acceso completo
        if request.user.is_staff or getattr(request.user, 'role', '') == 'admin':
            return True
        
        # Los usuarios regulares solo pueden ver (GET) sus propios registros
        return request.method in permissions.SAFE_METHODS
    
    def has_object_permission(self, request, view, obj):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Los administradores pueden acceder a cualquier objeto
        if request.user.is_staff or getattr(request.user, 'role', '') == 'admin':
            return True
        
        # Los usuarios regulares solo pueden ver sus propios registros
        if hasattr(obj, 'usuario'):
            return obj.usuario == request.user
        
        return False


class RegistroAuditoriaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para registros de auditoría
    Solo lectura - Los registros se crean automáticamente
    """
    queryset = RegistroAuditoria.objects.all().select_related('usuario', 'content_type')
    permission_classes = [IsAdminOrReadOnlyForOwn]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return RegistroAuditoriaListSerializer
        return RegistroAuditoriaSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Los administradores ven todo
        if user.is_staff or getattr(user, 'role', '') == 'admin':
            pass  # Mantener queryset completo
        else:
            # Los usuarios regulares solo ven sus propios registros
            queryset = queryset.filter(usuario=user)
        
        # Aplicar filtros desde query params
        return self._aplicar_filtros(queryset)
    
    def _aplicar_filtros(self, queryset):
        """Aplicar filtros basados en parámetros de consulta"""
        # Filtro por usuario (solo para admins)
        usuario_id = self.request.query_params.get('usuario')
        if usuario_id and (self.request.user.is_staff or getattr(self.request.user, 'role', '') == 'admin'):
            queryset = queryset.filter(usuario_id=usuario_id)
        
        # Filtro por tipo de actividad
        tipo_actividad = self.request.query_params.get('tipo_actividad')
        if tipo_actividad:
            queryset = queryset.filter(tipo_actividad=tipo_actividad)
        
        # Filtro por nivel de importancia
        nivel_importancia = self.request.query_params.get('nivel_importancia')
        if nivel_importancia:
            queryset = queryset.filter(nivel_importancia=nivel_importancia)
        
        # Filtro por éxito
        es_exitoso = self.request.query_params.get('es_exitoso')
        if es_exitoso is not None:
            queryset = queryset.filter(es_exitoso=es_exitoso.lower() == 'true')
        
        # Filtro por fechas
        fecha_inicio = self.request.query_params.get('fecha_inicio')
        fecha_fin = self.request.query_params.get('fecha_fin')
        
        if fecha_inicio:
            queryset = queryset.filter(timestamp__gte=fecha_inicio)
        if fecha_fin:
            queryset = queryset.filter(timestamp__lte=fecha_fin)
        
        # Búsqueda en descripción
        busqueda = self.request.query_params.get('busqueda')
        if busqueda:
            queryset = queryset.filter(descripcion__icontains=busqueda)
        
        return queryset.order_by('-timestamp')
    
    @action(detail=False, methods=['get'])
    def resumen(self, request):
        """Endpoint para obtener resumen de auditoría"""
        if not (request.user.is_staff or getattr(request.user, 'role', '') == 'admin'):
            return Response(
                {'error': 'No tiene permisos para ver el resumen de auditoría'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        hoy = timezone.now().date()
        inicio_semana = hoy - timedelta(days=7)
        
        # Estadísticas generales
        total_registros = RegistroAuditoria.objects.count()
        registros_hoy = RegistroAuditoria.objects.filter(timestamp__date=hoy).count()
        registros_semana = RegistroAuditoria.objects.filter(timestamp__date__gte=inicio_semana).count()
        
        # Logins del día
        logins_hoy = RegistroAuditoria.objects.filter(
            timestamp__date=hoy,
            tipo_actividad=TipoActividad.LOGIN
        )
        logins_exitosos_hoy = logins_hoy.filter(es_exitoso=True).count()
        logins_fallidos_hoy = logins_hoy.filter(es_exitoso=False).count()
        
        # Usuarios activos hoy
        usuarios_activos_hoy = RegistroAuditoria.objects.filter(
            timestamp__date=hoy,
            usuario__isnull=False
        ).values('usuario').distinct().count()
        
        # Sesiones activas
        sesiones_activas = SesionUsuario.objects.filter(esta_activa=True).count()
        
        # Errores críticos hoy
        errores_criticos_hoy = RegistroAuditoria.objects.filter(
            timestamp__date=hoy,
            nivel_importancia=NivelImportancia.CRITICO
        ).count()
        
        # Actividades por tipo (última semana)
        actividades_por_tipo = dict(
            RegistroAuditoria.objects.filter(
                timestamp__date__gte=inicio_semana
            ).values('tipo_actividad').annotate(
                count=Count('id')
            ).values_list('tipo_actividad', 'count')
        )
        
        # Usuarios más activos (última semana)
        usuarios_mas_activos = list(
            RegistroAuditoria.objects.filter(
                timestamp__date__gte=inicio_semana,
                usuario__isnull=False
            ).values(
                'usuario__username', 'usuario__email'
            ).annotate(
                count=Count('id')
            ).order_by('-count')[:10]
        )
        
        # IPs más frecuentes (última semana)
        ips_mas_frecuentes = list(
            RegistroAuditoria.objects.filter(
                timestamp__date__gte=inicio_semana,
                ip_address__isnull=False
            ).values('ip_address').annotate(
                count=Count('id')
            ).order_by('-count')[:10]
        )
        
        resumen_data = {
            'total_registros': total_registros,
            'registros_hoy': registros_hoy,
            'registros_semana': registros_semana,
            'logins_exitosos_hoy': logins_exitosos_hoy,
            'logins_fallidos_hoy': logins_fallidos_hoy,
            'usuarios_activos_hoy': usuarios_activos_hoy,
            'sesiones_activas': sesiones_activas,
            'errores_criticos_hoy': errores_criticos_hoy,
            'actividades_por_tipo': actividades_por_tipo,
            'usuarios_mas_activos': usuarios_mas_activos,
            'ips_mas_frecuentes': ips_mas_frecuentes
        }
        
        serializer = AuditoriaResumenSerializer(resumen_data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def mis_actividades(self, request):
        """Endpoint para que usuarios vean sus propias actividades"""
        queryset = RegistroAuditoria.objects.filter(
            usuario=request.user
        ).order_by('-timestamp')
        
        # Aplicar paginación siempre para consistencia
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = RegistroAuditoriaListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        # Fallback: crear respuesta paginada manualmente
        serializer = RegistroAuditoriaListSerializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'next': None,
            'previous': None,
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def exportar(self, request):
        """Endpoint para exportar registros de auditoría (solo admins)"""
        if not (request.user.is_staff or getattr(request.user, 'role', '') == 'admin'):
            return Response(
                {'error': 'No tiene permisos para exportar datos de auditoría'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Registrar la actividad de exportación
        AuditoriaLogger.registrar_actividad(
            usuario=request.user,
            tipo_actividad=TipoActividad.EXPORTAR,
            descripcion='Exportación de registros de auditoría solicitada',
            nivel_importancia=NivelImportancia.MEDIO,
            ip_address=getattr(request, 'audit_ip', None),
            user_agent=getattr(request, 'audit_user_agent', None)
        )
        
        # Obtener datos filtrados
        queryset = self._aplicar_filtros(self.get_queryset())
        serializer = RegistroAuditoriaSerializer(queryset[:1000], many=True)  # Limitar a 1000
        
        return Response({
            'mensaje': 'Datos de auditoría listos para exportación',
            'total_registros': queryset.count(),
            'registros_exportados': len(serializer.data),
            'datos': serializer.data
        })


class SesionUsuarioViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para sesiones de usuario
    Solo lectura - Las sesiones se manejan automáticamente
    """
    queryset = SesionUsuario.objects.all().select_related('usuario')
    serializer_class = SesionUsuarioSerializer
    permission_classes = [IsAdminOrReadOnlyForOwn]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        
        # Los administradores ven todas las sesiones
        if user.is_staff or getattr(user, 'role', '') == 'admin':
            pass
        else:
            # Los usuarios regulares solo ven sus propias sesiones
            queryset = queryset.filter(usuario=user)
        
        # Filtros opcionales
        activas_solo = self.request.query_params.get('activas_solo')
        if activas_solo and activas_solo.lower() == 'true':
            queryset = queryset.filter(esta_activa=True)
        
        return queryset.order_by('-fecha_inicio')
    
    @action(detail=False, methods=['get'])
    def mis_sesiones(self, request):
        """Endpoint para ver las propias sesiones del usuario"""
        queryset = SesionUsuario.objects.filter(
            usuario=request.user
        ).order_by('-fecha_inicio')
        
        # Aplicar paginación siempre para consistencia
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = SesionUsuarioSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        # Fallback: crear respuesta paginada manualmente
        serializer = SesionUsuarioSerializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'next': None,
            'previous': None,
            'results': serializer.data
        })


class EstadisticasAuditoriaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet para estadísticas de auditoría
    Solo lectura - Las estadísticas se calculan automáticamente
    """
    queryset = EstadisticasAuditoria.objects.all()
    serializer_class = EstadisticasAuditoriaSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_permissions(self):
        """Solo administradores pueden acceder a las estadísticas"""
        if self.request.user.is_staff or getattr(self.request.user, 'role', '') == 'admin':
            return [permissions.IsAuthenticated()]
        return [permissions.IsAdminUser()]
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filtros por fecha
        fecha_inicio = self.request.query_params.get('fecha_inicio')
        fecha_fin = self.request.query_params.get('fecha_fin')
        
        if fecha_inicio:
            queryset = queryset.filter(fecha__gte=fecha_inicio)
        if fecha_fin:
            queryset = queryset.filter(fecha__lte=fecha_fin)
        
        return queryset.order_by('-fecha')
    
    @action(detail=False, methods=['get'])
    def tendencias(self, request):
        """Endpoint para obtener tendencias de las estadísticas"""
        # Últimos 30 días
        fecha_limite = date.today() - timedelta(days=30)
        estadisticas = EstadisticasAuditoria.objects.filter(
            fecha__gte=fecha_limite
        ).order_by('fecha')
        
        datos_tendencia = {
            'fechas': [],
            'total_actividades': [],
            'total_logins': [],
            'usuarios_activos': [],
            'errores_sistema': []
        }
        
        for stat in estadisticas:
            datos_tendencia['fechas'].append(stat.fecha.strftime('%Y-%m-%d'))
            datos_tendencia['total_actividades'].append(stat.total_actividades)
            datos_tendencia['total_logins'].append(stat.total_logins)
            datos_tendencia['usuarios_activos'].append(stat.total_usuarios_activos)
            datos_tendencia['errores_sistema'].append(stat.errores_sistema)
        
        return Response(datos_tendencia)