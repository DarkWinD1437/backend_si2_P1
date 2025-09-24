"""
Vistas API para el Módulo de Reservas de Áreas Comunes
Módulo 4: Reservas de Áreas Comunes

Permisos:
- Administradores: CRUD completo de áreas comunes y reservas
- Residentes: Pueden ver áreas disponibles, hacer reservas, cancelar sus reservas
- Seguridad: Solo lectura de áreas comunes y reservas
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.utils import timezone
from datetime import date, time, datetime, timedelta
from decimal import Decimal

from .models import (
    AreaComun, Reserva, HorarioDisponible,
    EstadoAreaComun, EstadoReserva, TipoAreaComun
)
from .serializers import (
    AreaComunSerializer,
    AreaComunListSerializer,
    ReservaSerializer,
    ReservaListSerializer,
    CrearReservaSerializer,
    DisponibilidadSerializer,
    ConfirmarReservaSerializer,
    CancelarReservaSerializer,
    HorarioDisponibleSerializer
)

User = get_user_model()


class IsAdminOrResident(permissions.BasePermission):
    """
    Permiso personalizado:
    - Administradores: acceso completo
    - Residentes: acceso a reservas propias
    - Seguridad: solo lectura
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Administradores tienen acceso completo
        if hasattr(request.user, 'role') and request.user.role == 'admin':
            return True

        # Residentes pueden hacer reservas
        if hasattr(request.user, 'role') and request.user.role == 'resident':
            return True

        # Seguridad solo lectura
        if hasattr(request.user, 'role') and request.user.role == 'security':
            return request.method in permissions.SAFE_METHODS

        return False

    def has_object_permission(self, request, view, obj):
        # Administradores tienen acceso completo
        if hasattr(request.user, 'role') and request.user.role == 'admin':
            return True

        # Los usuarios solo pueden acceder a sus propias reservas
        if isinstance(obj, Reserva):
            return obj.usuario == request.user

        # Para áreas comunes, todos los usuarios autenticados pueden ver
        return True


class AreaComunViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de Áreas Comunes
    """
    queryset = AreaComun.objects.filter(estado=EstadoAreaComun.ACTIVA)
    permission_classes = [IsAdminOrResident]

    def get_serializer_class(self):
        if self.action == 'list':
            return AreaComunListSerializer
        return AreaComunSerializer

    def get_queryset(self):
        queryset = AreaComun.objects.filter(estado=EstadoAreaComun.ACTIVA)

        # Filtros opcionales
        tipo = self.request.query_params.get('tipo', None)
        if tipo:
            queryset = queryset.filter(tipo=tipo)

        capacidad_minima = self.request.query_params.get('capacidad_minima', None)
        if capacidad_minima:
            queryset = queryset.filter(capacidad_maxima__gte=capacidad_minima)

        return queryset

    @action(detail=True, methods=['get'])
    def disponibilidad(self, request, pk=None):
        """
        T1: Consultar Disponibilidad de Área Común

        GET /api/reservations/areas/{id}/disponibilidad/?fecha=2025-09-25
        """
        area = self.get_object()
        fecha_str = request.query_params.get('fecha', None)

        if not fecha_str:
            return Response(
                {'error': 'Parámetro fecha requerido (formato: YYYY-MM-DD)'},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            fecha = datetime.strptime(fecha_str, '%Y-%m-%d').date()
        except ValueError:
            return Response(
                {'error': 'Formato de fecha inválido. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verificar que la fecha no sea en el pasado
        if fecha < date.today():
            return Response(
                {'error': 'No se puede consultar disponibilidad para fechas pasadas'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Obtener horarios disponibles para este día de la semana
        dia_semana = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo'][fecha.weekday()]

        try:
            horario = HorarioDisponible.objects.get(
                area_comun=area,
                dia_semana=dia_semana,
                activo=True
            )
        except HorarioDisponible.DoesNotExist:
            return Response({
                'disponible': False,
                'mensaje': f'El área no está disponible los {dia_semana}s',
                'horarios_disponibles': []
            })

        # Generar slots de tiempo disponibles (cada 30 minutos)
        slots_disponibles = []
        hora_actual = horario.hora_apertura

        while hora_actual < horario.hora_cierre:
            hora_fin_slot = (datetime.combine(date.today(), hora_actual) + timedelta(hours=area.tiempo_minimo_reserva)).time()

            if hora_fin_slot <= horario.hora_cierre:
                disponible = area.esta_disponible_en_fecha(fecha, hora_actual, hora_fin_slot)

                slots_disponibles.append({
                    'hora_inicio': hora_actual.strftime('%H:%M'),
                    'hora_fin': hora_fin_slot.strftime('%H:%M'),
                    'disponible': disponible,
                    'duracion_horas': area.tiempo_minimo_reserva,
                    'costo_total': str(area.calcular_costo_total(area.tiempo_minimo_reserva))
                })

            # Avanzar 30 minutos
            hora_actual = (datetime.combine(date.today(), hora_actual) + timedelta(minutes=30)).time()

        return Response({
            'area_comun': AreaComunListSerializer(area).data,
            'fecha': fecha_str,
            'dia_semana': dia_semana,
            'horario_disponible': {
                'hora_apertura': horario.hora_apertura.strftime('%H:%M'),
                'hora_cierre': horario.hora_cierre.strftime('%H:%M')
            },
            'slots_disponibles': slots_disponibles,
            'tiempo_minimo_reserva': area.tiempo_minimo_reserva,
            'anticipacion_minima_horas': area.anticipo_minimo_horas
        })

    @action(detail=True, methods=['post'])
    def reservar(self, request, pk=None):
        """
        T2: Reservar Área Común

        POST /api/reservations/areas/{id}/reservar/
        {
            "fecha": "2025-09-25",
            "hora_inicio": "14:00",
            "hora_fin": "16:00",
            "numero_personas": 10,
            "observaciones": "Fiesta de cumpleaños"
        }
        """
        area = self.get_object()

        # Verificar permisos del usuario
        if not area.puede_reservar_usuario(request.user):
            return Response(
                {'error': 'No tiene permisos para reservar esta área'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = CrearReservaSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Validar fecha y hora
        fecha = serializer.validated_data['fecha']
        hora_inicio = serializer.validated_data['hora_inicio']
        hora_fin = serializer.validated_data['hora_fin']

        # Verificar anticipación mínima
        fecha_hora_reserva = datetime.combine(fecha, hora_inicio)
        ahora = timezone.now()
        horas_anticipacion = (fecha_hora_reserva - ahora).total_seconds() / 3600

        if horas_anticipacion < area.anticipacion_minimo_horas:
            return Response(
                {'error': f'Se requiere reserva con al menos {area.anticipacion_minimo_horas} horas de anticipación'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Verificar disponibilidad
        if not area.esta_disponible_en_fecha(fecha, hora_inicio, hora_fin):
            return Response(
                {'error': 'El horario solicitado no está disponible'},
                status=status.HTTP_409_CONFLICT
            )

        # Verificar capacidad
        numero_personas = serializer.validated_data.get('numero_personas', 1)
        if numero_personas > area.capacidad_maxima:
            return Response(
                {'error': f'El número de personas ({numero_personas}) excede la capacidad máxima ({area.capacidad_maxima})'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Calcular duración y costo
        inicio = datetime.combine(fecha, hora_inicio)
        fin = datetime.combine(fecha, hora_fin)
        if fin <= inicio:
            fin = datetime.combine(fecha + timedelta(days=1), hora_fin)
        duracion = (fin - inicio).total_seconds() / 3600

        if duracion < area.tiempo_minimo_reserva or duracion > area.tiempo_maximo_reserva:
            return Response(
                {'error': f'La duración debe estar entre {area.tiempo_minimo_reserva} y {area.tiempo_maximo_reserva} horas'},
                status=status.HTTP_400_BAD_REQUEST
            )

        costo_total = area.calcular_costo_total(duracion)

        # Crear la reserva
        reserva = Reserva.objects.create(
            area_comun=area,
            usuario=request.user,
            fecha=fecha,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            duracion_horas=Decimal(str(duracion)),
            costo_total=costo_total,
            numero_personas=numero_personas,
            observaciones=serializer.validated_data.get('observaciones', ''),
            estado=EstadoReserva.PENDIENTE if area.requiere_aprobacion else EstadoReserva.CONFIRMADA
        )

        serializer_respuesta = ReservaSerializer(reserva)
        return Response(serializer_respuesta.data, status=status.HTTP_201_CREATED)


class ReservaViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de Reservas
    """
    permission_classes = [IsAdminOrResident]

    def get_serializer_class(self):
        if self.action == 'list':
            return ReservaListSerializer
        elif self.action == 'create':
            return CrearReservaSerializer
        return ReservaSerializer

    def get_queryset(self):
        user = self.request.user

        if hasattr(user, 'role') and user.role == 'admin':
            # Administradores ven todas las reservas
            queryset = Reserva.objects.all()
        else:
            # Otros usuarios solo ven sus propias reservas
            queryset = Reserva.objects.filter(usuario=user)

        # Filtros opcionales
        estado = self.request.query_params.get('estado', None)
        if estado:
            queryset = queryset.filter(estado=estado)

        fecha_desde = self.request.query_params.get('fecha_desde', None)
        if fecha_desde:
            queryset = queryset.filter(fecha__gte=fecha_desde)

        fecha_hasta = self.request.query_params.get('fecha_hasta', None)
        if fecha_hasta:
            queryset = queryset.filter(fecha__lte=fecha_hasta)

        area_comun = self.request.query_params.get('area_comun', None)
        if area_comun:
            queryset = queryset.filter(area_comun_id=area_comun)

        return queryset.order_by('-fecha', '-hora_inicio')

    def perform_create(self, serializer):
        # Las reservas se crean a través del endpoint de áreas comunes
        pass

    @action(detail=True, methods=['post'])
    def confirmar(self, request, pk=None):
        """
        T3: Confirmar Reserva con Pago

        POST /api/reservations/reservas/{id}/confirmar/
        {
            "metodo_pago": "transferencia_bancaria"
        }
        """
        reserva = self.get_object()

        # Verificar que el usuario puede confirmar esta reserva
        if reserva.usuario != request.user and not (hasattr(request.user, 'role') and request.user.role == 'admin'):
            return Response(
                {'error': 'No tiene permisos para confirmar esta reserva'},
                status=status.HTTP_403_FORBIDDEN
            )

        if not reserva.puede_confirmar:
            return Response(
                {'error': 'Esta reserva no puede ser confirmada'},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = ConfirmarReservaSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Aquí se integraría con el módulo financiero para procesar el pago
        # Por ahora, solo marcamos como pagada
        try:
            reserva.marcar_pagada()

            # TODO: Integrar con módulo financiero
            # - Crear cargo financiero
            # - Procesar pago
            # - Generar comprobante

            return Response({
                'mensaje': 'Reserva confirmada y pagada exitosamente',
                'reserva': ReservaSerializer(reserva).data
            })

        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'])
    def cancelar(self, request, pk=None):
        """
        T4: Cancelar Reserva

        POST /api/reservations/reservas/{id}/cancelar/
        {
            "motivo": "Cambio de planes"
        }
        """
        reserva = self.get_object()

        serializer = CancelarReservaSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        motivo = serializer.validated_data.get('motivo', '')

        try:
            reserva.cancelar(request.user, motivo)

            # TODO: Integrar con módulo financiero para reembolso si ya se pagó

            return Response({
                'mensaje': 'Reserva cancelada exitosamente',
                'reserva': ReservaSerializer(reserva).data
            })

        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def mis_reservas(self, request):
        """
        Obtener reservas del usuario actual
        """
        queryset = self.get_queryset().filter(usuario=request.user)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def disponibles(self, request):
        """
        Obtener áreas comunes disponibles para reserva
        """
        areas = AreaComun.objects.filter(estado=EstadoAreaComun.ACTIVA)
        serializer = AreaComunListSerializer(areas, many=True)
        return Response(serializer.data)


class HorarioDisponibleViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de Horarios Disponibles (solo administradores)
    """
    queryset = HorarioDisponible.objects.all()
    serializer_class = HorarioDisponibleSerializer
    permission_classes = [permissions.IsAdminUser]  # Solo administradores