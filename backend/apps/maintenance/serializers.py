from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import SolicitudMantenimiento, TareaMantenimiento

User = get_user_model()


class SolicitudMantenimientoListSerializer(serializers.ModelSerializer):
    """Serializer para lista de solicitudes de mantenimiento"""

    solicitante_info = serializers.SerializerMethodField()
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    prioridad_display = serializers.CharField(source='get_prioridad_display', read_only=True)
    fecha_solicitud_display = serializers.SerializerMethodField()
    tarea_info = serializers.SerializerMethodField()

    class Meta:
        model = SolicitudMantenimiento
        fields = [
            'id', 'solicitante_info', 'descripcion', 'ubicacion', 'prioridad',
            'prioridad_display', 'estado', 'estado_display', 'fecha_solicitud',
            'fecha_solicitud_display', 'fecha_actualizacion', 'tarea_info'
        ]

    def get_solicitante_info(self, obj):
        return {
            'id': obj.solicitante.id,
            'username': obj.solicitante.username,
            'nombre_completo': f"{obj.solicitante.first_name} {obj.solicitante.last_name}".strip()
        }

    def get_fecha_solicitud_display(self, obj):
        return obj.fecha_solicitud.strftime('%d/%m/%Y %H:%M')

    def get_tarea_info(self, obj):
        if hasattr(obj, 'tarea'):
            return {
                'id': obj.tarea.id,
                'asignado_a': {
                    'id': obj.tarea.asignado_a.id,
                    'username': obj.tarea.asignado_a.username,
                    'nombre_completo': f"{obj.tarea.asignado_a.first_name} {obj.tarea.asignado_a.last_name}".strip()
                },
                'estado': obj.tarea.estado,
                'estado_display': obj.tarea.get_estado_display(),
                'fecha_asignacion': obj.tarea.fecha_asignacion.strftime('%d/%m/%Y %H:%M'),
                'fecha_completado': obj.tarea.fecha_completado.strftime('%d/%m/%Y %H:%M') if obj.tarea.fecha_completado else None,
                'descripcion_tarea': obj.tarea.descripcion_tarea,
                'notas': obj.tarea.notas
            }
        return None


class SolicitudMantenimientoSerializer(serializers.ModelSerializer):
    """Serializer completo para Solicitud de Mantenimiento"""

    solicitante_info = serializers.SerializerMethodField()
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    prioridad_display = serializers.CharField(source='get_prioridad_display', read_only=True)
    fecha_solicitud_display = serializers.SerializerMethodField()
    tarea_info = serializers.SerializerMethodField()

    class Meta:
        model = SolicitudMantenimiento
        fields = [
            'id', 'solicitante_info', 'descripcion', 'ubicacion', 'prioridad',
            'prioridad_display', 'estado', 'estado_display', 'fecha_solicitud',
            'fecha_solicitud_display', 'fecha_actualizacion', 'tarea_info'
        ]
        read_only_fields = ['fecha_solicitud', 'fecha_actualizacion']

    def get_solicitante_info(self, obj):
        return {
            'id': obj.solicitante.id,
            'username': obj.solicitante.username,
            'nombre_completo': f"{obj.solicitante.first_name} {obj.solicitante.last_name}".strip(),
            'role': obj.solicitante.role
        }

    def get_fecha_solicitud_display(self, obj):
        return obj.fecha_solicitud.strftime('%d/%m/%Y %H:%M')

    def get_tarea_info(self, obj):
        if hasattr(obj, 'tarea'):
            return {
                'id': obj.tarea.id,
                'asignado_a': {
                    'id': obj.tarea.asignado_a.id,
                    'username': obj.tarea.asignado_a.username,
                    'nombre_completo': f"{obj.tarea.asignado_a.first_name} {obj.tarea.asignado_a.last_name}".strip()
                },
                'estado': obj.tarea.estado,
                'estado_display': obj.tarea.get_estado_display(),
                'fecha_asignacion': obj.tarea.fecha_asignacion.strftime('%d/%m/%Y %H:%M'),
                'fecha_completado': obj.tarea.fecha_completado.strftime('%d/%m/%Y %H:%M') if obj.tarea.fecha_completado else None
            }
        return None


class CrearSolicitudMantenimientoSerializer(serializers.ModelSerializer):
    """Serializer para crear una solicitud de mantenimiento"""

    class Meta:
        model = SolicitudMantenimiento
        fields = ['descripcion', 'ubicacion', 'prioridad']

    def create(self, validated_data):
        validated_data['solicitante'] = self.context['request'].user
        return super().create(validated_data)


class TareaMantenimientoSerializer(serializers.ModelSerializer):
    """Serializer para Tarea de Mantenimiento"""

    solicitud_info = serializers.SerializerMethodField()
    asignado_a_info = serializers.SerializerMethodField()
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    fecha_asignacion_display = serializers.SerializerMethodField()
    fecha_completado_display = serializers.SerializerMethodField()

    class Meta:
        model = TareaMantenimiento
        fields = [
            'id', 'solicitud_info', 'asignado_a_info', 'descripcion_tarea',
            'estado', 'estado_display', 'fecha_asignacion', 'fecha_asignacion_display',
            'fecha_completado', 'fecha_completado_display', 'notas'
        ]
        read_only_fields = ['fecha_asignacion', 'fecha_completado']

    def get_solicitud_info(self, obj):
        return {
            'id': obj.solicitud.id,
            'descripcion': obj.solicitud.descripcion,
            'ubicacion': obj.solicitud.ubicacion,
            'prioridad': obj.solicitud.prioridad,
            'prioridad_display': obj.solicitud.get_prioridad_display()
        }

    def get_asignado_a_info(self, obj):
        return {
            'id': obj.asignado_a.id,
            'username': obj.asignado_a.username,
            'nombre_completo': f"{obj.asignado_a.first_name} {obj.asignado_a.last_name}".strip(),
            'role': obj.asignado_a.role
        }

    def get_fecha_asignacion_display(self, obj):
        return obj.fecha_asignacion.strftime('%d/%m/%Y %H:%M')

    def get_fecha_completado_display(self, obj):
        return obj.fecha_completado.strftime('%d/%m/%Y %H:%M') if obj.fecha_completado else None


class AsignarTareaSerializer(serializers.Serializer):
    """Serializer para asignar una tarea de mantenimiento"""

    asignado_a_id = serializers.IntegerField()
    descripcion_tarea = serializers.CharField(max_length=1000)
    notas = serializers.CharField(max_length=1000, required=False, allow_blank=True)

    def validate_asignado_a_id(self, value):
        try:
            user = User.objects.get(id=value)
            # Aquí podrías validar que el usuario tenga rol de mantenimiento
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("Usuario no encontrado")


class ActualizarEstadoTareaSerializer(serializers.Serializer):
    """Serializer para actualizar el estado de una tarea"""

    estado = serializers.ChoiceField(choices=TareaMantenimiento.ESTADO_CHOICES)
    notas = serializers.CharField(max_length=1000, required=False, allow_blank=True)