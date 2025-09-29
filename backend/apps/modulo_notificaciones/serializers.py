from rest_framework import serializers
from .models import Dispositivo, PreferenciasNotificacion, Notificacion


class DispositivoSerializer(serializers.ModelSerializer):
    """Serializer para dispositivos"""

    class Meta:
        model = Dispositivo
        fields = [
            'id', 'token_push', 'tipo_dispositivo', 'nombre_dispositivo',
            'activo', 'fecha_registro', 'ultima_actividad'
        ]
        read_only_fields = ['id', 'fecha_registro', 'ultima_actividad']

    def create(self, validated_data):
        validated_data['usuario'] = self.context['request'].user
        return super().create(validated_data)


class DispositivoRegistroSerializer(serializers.Serializer):
    """Serializer para registrar un nuevo dispositivo"""
    token_push = serializers.CharField(max_length=500, required=True)
    tipo_dispositivo = serializers.ChoiceField(
        choices=Dispositivo.TIPO_DISPOSITIVO_CHOICES,
        required=True
    )
    nombre_dispositivo = serializers.CharField(max_length=100, required=False, allow_blank=True)

    def create(self, validated_data):
        # Verificar si ya existe un dispositivo con este token
        dispositivo, created = Dispositivo.objects.get_or_create(
            token_push=validated_data['token_push'],
            defaults={
                'usuario': self.context['request'].user,
                'tipo_dispositivo': validated_data['tipo_dispositivo'],
                'nombre_dispositivo': validated_data.get('nombre_dispositivo', ''),
                'activo': True
            }
        )

        if not created:
            # Actualizar si ya existe
            dispositivo.tipo_dispositivo = validated_data['tipo_dispositivo']
            dispositivo.nombre_dispositivo = validated_data.get('nombre_dispositivo', dispositivo.nombre_dispositivo)
            dispositivo.activo = True
            dispositivo.save()

        return dispositivo


class PreferenciasNotificacionSerializer(serializers.ModelSerializer):
    """Serializer para preferencias de notificación"""

    tipo_display = serializers.CharField(source='get_tipo_notificacion_display', read_only=True)

    class Meta:
        model = PreferenciasNotificacion
        fields = [
            'id', 'tipo_notificacion', 'tipo_display',
            'push_enabled', 'email_enabled', 'sms_enabled',
            'fecha_creacion', 'fecha_actualizacion'
        ]
        read_only_fields = ['id', 'fecha_creacion', 'fecha_actualizacion']

    def create(self, validated_data):
        validated_data['usuario'] = self.context['request'].user
        return super().create(validated_data)


class NotificacionSerializer(serializers.ModelSerializer):
    """Serializer para notificaciones"""

    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    dispositivo_info = serializers.SerializerMethodField()

    class Meta:
        model = Notificacion
        fields = [
            'id', 'titulo', 'mensaje', 'tipo', 'tipo_display',
            'estado', 'estado_display', 'fecha_creacion', 'fecha_envio', 'fecha_lectura',
            'datos_extra', 'prioridad', 'push_enviado', 'email_enviado', 'sms_enviado',
            'dispositivo_info', 'error_mensaje'
        ]
        read_only_fields = [
            'id', 'fecha_creacion', 'fecha_envio', 'fecha_lectura',
            'push_enviado', 'email_enviado', 'sms_enviado', 'error_mensaje'
        ]

    def get_dispositivo_info(self, obj):
        if obj.dispositivo:
            return {
                'id': obj.dispositivo.id,
                'tipo': obj.dispositivo.tipo_dispositivo,
                'nombre': obj.dispositivo.nombre_dispositivo
            }
        return None


class NotificacionCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear notificaciones"""

    class Meta:
        model = Notificacion
        fields = [
            'titulo', 'mensaje', 'tipo', 'usuario', 'dispositivo',
            'datos_extra', 'prioridad'
        ]

    def create(self, validated_data):
        # Crear la notificación
        notificacion = super().create(validated_data)

        # Intentar enviar la notificación automáticamente
        from .services import NotificacionService
        service = NotificacionService()
        service.enviar_notificacion(notificacion)

        return notificacion


class EnviarNotificacionSerializer(serializers.Serializer):
    """Serializer para enviar notificaciones push"""

    titulo = serializers.CharField(max_length=200, required=True)
    mensaje = serializers.CharField(required=True)
    tipo = serializers.ChoiceField(choices=Notificacion.TIPO_NOTIFICACION_CHOICES, default='sistema')
    usuarios_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text="Lista de IDs de usuarios. Si no se especifica, se envía a todos los usuarios activos."
    )
    destinatarios = serializers.ListField(
        child=serializers.CharField(),
        required=False,
        help_text="Lista de roles destinatarios. Opciones: 'residentes', 'administradores', 'seguridad'"
    )
    datos_extra = serializers.JSONField(required=False, default=dict)
    prioridad = serializers.IntegerField(min_value=1, max_value=5, default=1)

    def create(self, validated_data):
        from .services import NotificacionService
        service = NotificacionService()

        usuarios_ids = validated_data.pop('usuarios_ids', None)
        destinatarios = validated_data.pop('destinatarios', None)
        
        return service.enviar_notificacion_masiva(
            titulo=validated_data['titulo'],
            mensaje=validated_data['mensaje'],
            tipo=validated_data['tipo'],
            usuarios_ids=usuarios_ids,
            destinatarios=destinatarios,
            datos_extra=validated_data.get('datos_extra'),
            prioridad=validated_data.get('prioridad', 1)
        )