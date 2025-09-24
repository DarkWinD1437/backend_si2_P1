"""
Serializers para el Módulo de Reservas de Áreas Comunes
Módulo 4: Reservas de Áreas Comunes
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import date, time, datetime, timedelta
from decimal import Decimal

from .models import (
    AreaComun, Reserva, HorarioDisponible,
    EstadoAreaComun, EstadoReserva, TipoAreaComun
)

User = get_user_model()


class HorarioDisponibleSerializer(serializers.ModelSerializer):
    """Serializer para HorarioDisponible"""

    dia_semana_display = serializers.CharField(source='get_dia_semana_display', read_only=True)

    class Meta:
        model = HorarioDisponible
        fields = [
            'id', 'dia_semana', 'dia_semana_display', 'hora_apertura',
            'hora_cierre', 'activo'
        ]


class AreaComunListSerializer(serializers.ModelSerializer):
    """Serializer para lista de áreas comunes"""

    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    costo_por_hora_display = serializers.SerializerMethodField()
    costo_reserva_display = serializers.SerializerMethodField()

    class Meta:
        model = AreaComun
        fields = [
            'id', 'nombre', 'tipo', 'tipo_display', 'capacidad_maxima',
            'costo_por_hora', 'costo_por_hora_display', 'costo_reserva',
            'costo_reserva_display', 'estado', 'estado_display',
            'requiere_aprobacion', 'tiempo_minimo_reserva',
            'tiempo_maximo_reserva', 'anticipo_minimo_horas'
        ]

    def get_costo_por_hora_display(self, obj):
        return f"${obj.costo_por_hora}"

    def get_costo_reserva_display(self, obj):
        return f"${obj.costo_reserva}"


class AreaComunSerializer(serializers.ModelSerializer):
    """Serializer completo para Área Común"""

    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    horarios_disponibles = HorarioDisponibleSerializer(many=True, read_only=True)
    costo_por_hora_display = serializers.SerializerMethodField()
    costo_reserva_display = serializers.SerializerMethodField()

    class Meta:
        model = AreaComun
        fields = [
            'id', 'nombre', 'descripcion', 'tipo', 'tipo_display',
            'capacidad_maxima', 'costo_por_hora', 'costo_por_hora_display',
            'costo_reserva', 'costo_reserva_display', 'estado', 'estado_display',
            'requiere_aprobacion', 'tiempo_minimo_reserva', 'tiempo_maximo_reserva',
            'anticipo_minimo_horas', 'horarios_disponibles',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def get_costo_por_hora_display(self, obj):
        return f"${obj.costo_por_hora}"

    def get_costo_reserva_display(self, obj):
        return f"${obj.costo_reserva}"


class ReservaListSerializer(serializers.ModelSerializer):
    """Serializer para lista de reservas"""

    area_comun_info = serializers.SerializerMethodField()
    usuario_info = serializers.SerializerMethodField()
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    costo_total_display = serializers.SerializerMethodField()
    fecha_hora_display = serializers.SerializerMethodField()
    puede_cancelar = serializers.SerializerMethodField()
    puede_confirmar = serializers.SerializerMethodField()

    class Meta:
        model = Reserva
        fields = [
            'id', 'area_comun_info', 'usuario_info', 'fecha', 'hora_inicio',
            'hora_fin', 'duracion_horas', 'estado', 'estado_display',
            'costo_total', 'costo_total_display', 'numero_personas',
            'fecha_hora_display', 'puede_cancelar', 'puede_confirmar',
            'created_at'
        ]

    def get_area_comun_info(self, obj):
        return {
            'id': obj.area_comun.id,
            'nombre': obj.area_comun.nombre,
            'tipo': obj.area_comun.tipo,
            'tipo_display': obj.area_comun.get_tipo_display()
        }

    def get_usuario_info(self, obj):
        return {
            'id': obj.usuario.id,
            'username': obj.usuario.username,
            'nombre_completo': f"{obj.usuario.first_name} {obj.usuario.last_name}".strip()
        }

    def get_costo_total_display(self, obj):
        return f"${obj.costo_total}"

    def get_fecha_hora_display(self, obj):
        return f"{obj.fecha.strftime('%d/%m/%Y')} {obj.hora_inicio.strftime('%H:%M')} - {obj.hora_fin.strftime('%H:%M')}"

    def get_puede_cancelar(self, obj):
        request = self.context.get('request')
        if request and request.user:
            return obj.puede_cancelar(request.user)
        return False

    def get_puede_confirmar(self, obj):
        return obj.puede_confirmar


class ReservaSerializer(serializers.ModelSerializer):
    """Serializer completo para Reserva"""

    area_comun_info = serializers.SerializerMethodField()
    usuario_info = serializers.SerializerMethodField()
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    costo_total_display = serializers.SerializerMethodField()
    fecha_hora_display = serializers.SerializerMethodField()
    puede_cancelar = serializers.SerializerMethodField()
    puede_confirmar = serializers.SerializerMethodField()
    esta_vencida = serializers.ReadOnlyField()

    class Meta:
        model = Reserva
        fields = [
            'id', 'area_comun_info', 'usuario_info', 'fecha', 'hora_inicio',
            'hora_fin', 'duracion_horas', 'estado', 'estado_display',
            'costo_total', 'costo_total_display', 'numero_personas',
            'observaciones', 'fecha_hora_display', 'puede_cancelar',
            'puede_confirmar', 'esta_vencida', 'cargo_financiero',
            'created_at', 'updated_at'
        ]
        read_only_fields = [
            'duracion_horas', 'costo_total', 'cargo_financiero',
            'created_at', 'updated_at'
        ]

    def get_area_comun_info(self, obj):
        return {
            'id': obj.area_comun.id,
            'nombre': obj.area_comun.nombre,
            'tipo': obj.area_comun.tipo,
            'tipo_display': obj.area_comun.get_tipo_display(),
            'capacidad_maxima': obj.area_comun.capacidad_maxima
        }

    def get_usuario_info(self, obj):
        return {
            'id': obj.usuario.id,
            'username': obj.usuario.username,
            'nombre_completo': f"{obj.usuario.first_name} {obj.usuario.last_name}".strip(),
            'role': obj.usuario.role
        }

    def get_costo_total_display(self, obj):
        return f"${obj.costo_total}"

    def get_fecha_hora_display(self, obj):
        return f"{obj.fecha.strftime('%d/%m/%Y')} {obj.hora_inicio.strftime('%H:%M')} - {obj.hora_fin.strftime('%H:%M')}"

    def get_puede_cancelar(self, obj):
        request = self.context.get('request')
        if request and request.user:
            return obj.puede_cancelar(request.user)
        return False

    def get_puede_confirmar(self, obj):
        return obj.puede_confirmar


class CrearReservaSerializer(serializers.Serializer):
    """Serializer para crear una reserva"""

    fecha = serializers.DateField()
    hora_inicio = serializers.TimeField()
    hora_fin = serializers.TimeField()
    numero_personas = serializers.IntegerField(min_value=1, default=1)
    observaciones = serializers.CharField(max_length=500, required=False, allow_blank=True)

    def validate_fecha(self, value):
        """Validar que la fecha no sea en el pasado"""
        if value < date.today():
            raise serializers.ValidationError("No se pueden hacer reservas para fechas pasadas")
        return value

    def validate(self, data):
        """Validaciones personalizadas"""
        fecha = data['fecha']
        hora_inicio = data['hora_inicio']
        hora_fin = data['hora_fin']

        # Validar que hora_fin sea posterior a hora_inicio
        if hora_fin <= hora_inicio:
            # Si hora_fin es menor o igual, asumimos que es al día siguiente
            fecha_fin = fecha + timedelta(days=1)
            hora_fin_datetime = datetime.combine(fecha_fin, hora_fin)
        else:
            hora_fin_datetime = datetime.combine(fecha, hora_fin)

        hora_inicio_datetime = datetime.combine(fecha, hora_inicio)

        # Validar duración mínima (al menos 30 minutos)
        duracion = hora_fin_datetime - hora_inicio_datetime
        if duracion.total_seconds() < 1800:  # 30 minutos
            raise serializers.ValidationError("La reserva debe tener al menos 30 minutos de duración")

        return data


class DisponibilidadSerializer(serializers.Serializer):
    """Serializer para consultar disponibilidad"""

    fecha = serializers.DateField()
    area_comun_id = serializers.IntegerField()

    def validate_fecha(self, value):
        """Validar que la fecha no sea en el pasado"""
        if value < date.today():
            raise serializers.ValidationError("No se puede consultar disponibilidad para fechas pasadas")
        return value


class ConfirmarReservaSerializer(serializers.Serializer):
    """Serializer para confirmar reserva con pago"""

    metodo_pago = serializers.ChoiceField(
        choices=[
            ('efectivo', 'Efectivo'),
            ('transferencia_bancaria', 'Transferencia Bancaria'),
            ('tarjeta_credito', 'Tarjeta de Crédito'),
            ('tarjeta_debito', 'Tarjeta de Débito'),
        ],
        default='transferencia_bancaria'
    )
    referencia_pago = serializers.CharField(max_length=100, required=False, allow_blank=True)
    observaciones_pago = serializers.CharField(max_length=500, required=False, allow_blank=True)


class CancelarReservaSerializer(serializers.Serializer):
    """Serializer para cancelar reserva"""

    motivo = serializers.CharField(max_length=500, required=False, allow_blank=True)