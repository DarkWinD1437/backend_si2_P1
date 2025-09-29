"""
Vistas API para el Módulo de Gestión de Mantenimiento
Módulo: Gestión de Mantenimiento

Permisos:
- Administradores: CRUD completo
- Residentes: Pueden crear solicitudes y ver las suyas
- Mantenimiento: Pueden ver tareas asignadas y actualizar estados
- Seguridad: Solo lectura
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone

from .models import SolicitudMantenimiento, TareaMantenimiento
from .serializers import (
    SolicitudMantenimientoSerializer,
    SolicitudMantenimientoListSerializer,
    CrearSolicitudMantenimientoSerializer,
    TareaMantenimientoSerializer,
    AsignarTareaSerializer,
    ActualizarEstadoTareaSerializer
)

User = get_user_model()


class IsAdminOrMaintenanceOrResident(permissions.BasePermission):
    """
    Permiso personalizado para mantenimiento:
    - Administradores: acceso completo
    - Residentes: pueden crear solicitudes y ver las suyas
    - Mantenimiento: pueden ver tareas asignadas y gestionar estados
    - Seguridad: solo lectura
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Administradores tienen acceso completo
        if hasattr(request.user, 'role') and request.user.role == 'admin':
            return True

        # Residentes pueden crear solicitudes
        if hasattr(request.user, 'role') and request.user.role == 'resident':
            return True

        # Mantenimiento puede gestionar tareas
        if hasattr(request.user, 'role') and request.user.role == 'maintenance':
            return True

        # Seguridad solo lectura
        if hasattr(request.user, 'role') and request.user.role == 'security':
            return request.method in permissions.SAFE_METHODS

        return False

    def has_object_permission(self, request, view, obj):
        # Administradores tienen acceso completo
        if hasattr(request.user, 'role') and request.user.role == 'admin':
            return True

        # Residentes solo pueden ver/modificar sus propias solicitudes
        if isinstance(obj, SolicitudMantenimiento):
            return obj.solicitante == request.user

        # Mantenimiento solo puede ver/modificar tareas asignadas a ellos
        if isinstance(obj, TareaMantenimiento):
            return obj.asignado_a == request.user

        return True


class SolicitudMantenimientoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de Solicitudes de Mantenimiento
    """
    permission_classes = [IsAdminOrMaintenanceOrResident]

    def get_serializer_class(self):
        if self.action == 'list':
            return SolicitudMantenimientoListSerializer
        elif self.action == 'create':
            return CrearSolicitudMantenimientoSerializer
        elif self.action == 'retrieve':
            return SolicitudMantenimientoSerializer
        return SolicitudMantenimientoSerializer

    def create(self, request, *args, **kwargs):
        """Crear solicitud y devolver datos completos"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        # Usar el serializer completo para la respuesta
        response_serializer = SolicitudMantenimientoSerializer(instance, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def get_queryset(self):
        user = self.request.user

        # Administradores ven todas las solicitudes
        if hasattr(user, 'role') and user.role == 'admin':
            queryset = SolicitudMantenimiento.objects.select_related('tarea', 'tarea__asignado_a')
        # Mantenimiento ve todas las solicitudes (para asignar tareas)
        elif hasattr(user, 'role') and user.role == 'maintenance':
            queryset = SolicitudMantenimiento.objects.select_related('tarea', 'tarea__asignado_a')
        # Residentes solo ven sus propias solicitudes
        else:
            queryset = SolicitudMantenimiento.objects.select_related('tarea', 'tarea__asignado_a').filter(solicitante=user)

        # Filtros opcionales
        estado = self.request.query_params.get('estado', None)
        if estado:
            queryset = queryset.filter(estado=estado)

        prioridad = self.request.query_params.get('prioridad', None)
        if prioridad:
            queryset = queryset.filter(prioridad=prioridad)

        return queryset.order_by('-fecha_solicitud')

    def perform_create(self, serializer):
        serializer.save(solicitante=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def asignar_tarea(self, request, pk=None):
        """
        Asignar una tarea de mantenimiento a una solicitud
        Solo administradores y usuarios de mantenimiento pueden asignar tareas
        """
        solicitud = self.get_object()

        # Verificar permisos
        if not (hasattr(request.user, 'role') and
                request.user.role in ['admin', 'maintenance']):
            return Response(
                {'error': 'No tienes permisos para asignar tareas'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Verificar que la solicitud no tenga ya una tarea asignada
        if hasattr(solicitud, 'tarea'):
            return Response(
                {'error': 'Esta solicitud ya tiene una tarea asignada'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = AsignarTareaSerializer(data=request.data)
        if serializer.is_valid():
            # Crear la tarea
            tarea = TareaMantenimiento.objects.create(
                solicitud=solicitud,
                asignado_a_id=serializer.validated_data['asignado_a_id'],
                descripcion_tarea=serializer.validated_data['descripcion_tarea'],
                notas=serializer.validated_data.get('notas', ''),
                estado='asignada'
            )

            # Actualizar estado de la solicitud
            solicitud.estado = 'asignada'
            solicitud.save()

            # Retornar la tarea creada
            tarea_serializer = TareaMantenimientoSerializer(tarea)
            return Response(tarea_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TareaMantenimientoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de Tareas de Mantenimiento
    """
    serializer_class = TareaMantenimientoSerializer
    permission_classes = [IsAdminOrMaintenanceOrResident]

    def get_queryset(self):
        user = self.request.user

        # Administradores ven todas las tareas
        if hasattr(user, 'role') and user.role == 'admin':
            queryset = TareaMantenimiento.objects.all()
        # Mantenimiento ve tareas asignadas a ellos
        elif hasattr(user, 'role') and user.role == 'maintenance':
            queryset = TareaMantenimiento.objects.filter(asignado_a=user)
        # Residentes ven tareas relacionadas con sus solicitudes
        else:
            queryset = TareaMantenimiento.objects.filter(
                solicitud__solicitante=user
            )

        # Filtros opcionales
        estado = self.request.query_params.get('estado', None)
        if estado:
            queryset = queryset.filter(estado=estado)

        asignado_a = self.request.query_params.get('asignado_a', None)
        if asignado_a:
            queryset = queryset.filter(asignado_a_id=asignado_a)

        return queryset.order_by('-fecha_asignacion')

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def actualizar_estado(self, request, pk=None):
        """
        Actualizar el estado de una tarea de mantenimiento
        Solo el usuario asignado o administradores pueden actualizar el estado
        """
        tarea = self.get_object()

        # Verificar permisos - permitir administradores y usuarios de mantenimiento
        user_can_update = False
        if hasattr(request.user, 'role'):
            if request.user.role in ['admin', 'maintenance']:
                user_can_update = True
            elif request.user == tarea.asignado_a:
                user_can_update = True

        if not user_can_update:
            return Response(
                {'error': 'No tienes permisos para actualizar esta tarea'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = ActualizarEstadoTareaSerializer(data=request.data)
        if serializer.is_valid():
            nuevo_estado = serializer.validated_data['estado']
            notas = serializer.validated_data.get('notas', '')

            # Actualizar tarea
            tarea.estado = nuevo_estado
            if notas:
                tarea.notas += f"\n{request.user.username} ({timezone.now().strftime('%d/%m/%Y %H:%M')}): {notas}"
            tarea.save()

            # Actualizar estado de la solicitud según el estado de la tarea
            if nuevo_estado == 'completada':
                tarea.solicitud.estado = 'completada'
            elif nuevo_estado == 'en_progreso':
                tarea.solicitud.estado = 'en_progreso'
            elif nuevo_estado == 'cancelada':
                tarea.solicitud.estado = 'cancelada'
            tarea.solicitud.save()

            # Retornar la tarea actualizada
            tarea_serializer = TareaMantenimientoSerializer(tarea)
            return Response(tarea_serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)