from rest_framework import serializers
from .models import RegistroAuditoria, SesionUsuario, EstadisticasAuditoria


class RegistroAuditoriaSerializer(serializers.ModelSerializer):
    """Serializer para registros de auditoría"""
    usuario_info = serializers.SerializerMethodField()
    tipo_actividad_display = serializers.CharField(source='get_tipo_actividad_display', read_only=True)
    nivel_importancia_display = serializers.CharField(source='get_nivel_importancia_display', read_only=True)
    objeto_afectado_str = serializers.CharField(source='objeto_afectado_str', read_only=True)
    nivel_color = serializers.CharField(source='get_nivel_color', read_only=True)
    
    class Meta:
        model = RegistroAuditoria
        fields = [
            'id', 'timestamp', 'usuario', 'usuario_info',
            'tipo_actividad', 'tipo_actividad_display',
            'descripcion', 'nivel_importancia', 'nivel_importancia_display', 'nivel_color',
            'ip_address', 'es_exitoso', 'mensaje_error',
            'objeto_afectado_str', 'datos_adicionales'
        ]
        read_only_fields = ['id', 'timestamp']
    
    def get_usuario_info(self, obj):
        """Información del usuario que realizó la acción"""
        if obj.usuario:
            return {
                'id': obj.usuario.id,
                'username': obj.usuario.username,
                'nombre_completo': obj.usuario.get_full_name() or obj.usuario.username,
                'email': obj.usuario.email
            }
        return {
            'id': None,
            'username': 'Sistema',
            'nombre_completo': 'Sistema',
            'email': None
        }


class RegistroAuditoriaListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listas de registros de auditoría"""
    usuario_username = serializers.CharField(source='nombre_usuario', read_only=True)
    tipo_actividad_display = serializers.CharField(source='get_tipo_actividad_display', read_only=True)
    nivel_importancia_display = serializers.CharField(source='get_nivel_importancia_display', read_only=True)
    descripcion_corta = serializers.SerializerMethodField()
    
    class Meta:
        model = RegistroAuditoria
        fields = [
            'id', 'timestamp', 'usuario_username',
            'tipo_actividad', 'tipo_actividad_display',
            'descripcion_corta', 'nivel_importancia', 'nivel_importancia_display',
            'es_exitoso'
        ]
    
    def get_descripcion_corta(self, obj):
        """Descripción truncada para la lista"""
        if len(obj.descripcion) > 100:
            return obj.descripcion[:100] + '...'
        return obj.descripcion


class SesionUsuarioSerializer(serializers.ModelSerializer):
    """Serializer para sesiones de usuario"""
    usuario_info = serializers.SerializerMethodField()
    duracion_sesion_str = serializers.SerializerMethodField()
    
    class Meta:
        model = SesionUsuario
        fields = [
            'id', 'usuario', 'usuario_info', 'ip_address',
            'fecha_inicio', 'fecha_ultimo_acceso', 'esta_activa',
            'fecha_cierre', 'duracion_sesion_str'
        ]
        read_only_fields = ['id']
    
    def get_usuario_info(self, obj):
        """Información del usuario"""
        return {
            'id': obj.usuario.id,
            'username': obj.usuario.username,
            'nombre_completo': obj.usuario.get_full_name() or obj.usuario.username
        }
    
    def get_duracion_sesion_str(self, obj):
        """Duración de la sesión en formato legible"""
        duracion = obj.duracion_sesion
        horas = int(duracion.total_seconds() // 3600)
        minutos = int((duracion.total_seconds() % 3600) // 60)
        return f"{horas}h {minutos}m"


class EstadisticasAuditoriaSerializer(serializers.ModelSerializer):
    """Serializer para estadísticas de auditoría"""
    
    class Meta:
        model = EstadisticasAuditoria
        fields = [
            'id', 'fecha', 'total_actividades', 'total_logins',
            'total_usuarios_activos', 'actividades_criticas',
            'errores_sistema', 'datos_estadisticas'
        ]
        read_only_fields = ['id']


class AuditoriaResumenSerializer(serializers.Serializer):
    """Serializer para resumen de auditoría"""
    total_registros = serializers.IntegerField()
    registros_hoy = serializers.IntegerField()
    registros_semana = serializers.IntegerField()
    logins_exitosos_hoy = serializers.IntegerField()
    logins_fallidos_hoy = serializers.IntegerField()
    usuarios_activos_hoy = serializers.IntegerField()
    sesiones_activas = serializers.IntegerField()
    errores_criticos_hoy = serializers.IntegerField()
    actividades_por_tipo = serializers.DictField()
    usuarios_mas_activos = serializers.ListField()
    ips_mas_frecuentes = serializers.ListField()


class FiltroAuditoriaSerializer(serializers.Serializer):
    """Serializer para filtros de búsqueda de auditoría"""
    usuario = serializers.IntegerField(required=False, help_text="ID del usuario")
    tipo_actividad = serializers.CharField(required=False, help_text="Tipo de actividad")
    nivel_importancia = serializers.CharField(required=False, help_text="Nivel de importancia")
    fecha_inicio = serializers.DateTimeField(required=False, help_text="Fecha de inicio")
    fecha_fin = serializers.DateTimeField(required=False, help_text="Fecha de fin")
    es_exitoso = serializers.BooleanField(required=False, help_text="Solo operaciones exitosas/fallidas")
    ip_address = serializers.CharField(required=False, help_text="Dirección IP")
    busqueda = serializers.CharField(required=False, help_text="Búsqueda en descripción")