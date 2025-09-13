from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import Aviso, LecturaAviso, ComentarioAviso

User = get_user_model()

class AutorSerializer(serializers.ModelSerializer):
    """Serializer básico para mostrar información del autor"""
    nombre_completo = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'role', 'nombre_completo']
    
    def get_nombre_completo(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username


class ComentarioAvisoSerializer(serializers.ModelSerializer):
    """Serializer para comentarios de avisos"""
    autor = AutorSerializer(read_only=True)
    respuestas = serializers.SerializerMethodField()
    es_respuesta_a = serializers.SerializerMethodField()
    
    class Meta:
        model = ComentarioAviso
        fields = ['id', 'contenido', 'autor', 'fecha_creacion', 'es_respuesta_a', 'respuestas']
    
    def get_respuestas(self, obj):
        respuestas = obj.respuestas.all()
        return ComentarioAvisoSerializer(respuestas, many=True, context=self.context).data
    
    def get_es_respuesta_a(self, obj):
        if obj.es_respuesta:
            return {
                'id': obj.es_respuesta.id,
                'autor': obj.es_respuesta.autor.username,
                'contenido': obj.es_respuesta.contenido[:50] + '...' if len(obj.es_respuesta.contenido) > 50 else obj.es_respuesta.contenido
            }
        return None


class LecturaAvisoSerializer(serializers.ModelSerializer):
    """Serializer para lecturas de avisos"""
    usuario = AutorSerializer(read_only=True)
    
    class Meta:
        model = LecturaAviso
        fields = ['id', 'usuario', 'fecha_lectura', 'confirmado']


class AvisoListSerializer(serializers.ModelSerializer):
    """Serializer para listar avisos (vista resumida)"""
    autor = AutorSerializer(read_only=True)
    tiempo_transcurrido = serializers.SerializerMethodField()
    total_lecturas = serializers.SerializerMethodField()
    total_comentarios = serializers.SerializerMethodField()
    usuario_ha_leido = serializers.SerializerMethodField()
    destinatarios_display = serializers.SerializerMethodField()
    
    class Meta:
        model = Aviso
        fields = [
            'id', 'titulo', 'resumen', 'autor', 'estado', 'prioridad',
            'tipo_destinatario', 'destinatarios_display', 'fecha_publicacion',
            'fecha_vencimiento', 'esta_vencido', 'esta_publicado',
            'requiere_confirmacion', 'es_fijado', 'visualizaciones',
            'tiempo_transcurrido', 'total_lecturas', 'total_comentarios',
            'usuario_ha_leido'
        ]
    
    def get_tiempo_transcurrido(self, obj):
        if obj.fecha_publicacion:
            delta = timezone.now() - obj.fecha_publicacion
            if delta.days > 0:
                return f"hace {delta.days} día(s)"
            elif delta.seconds > 3600:
                return f"hace {delta.seconds // 3600} hora(s)"
            else:
                return f"hace {delta.seconds // 60} minuto(s)"
        return "Sin publicar"
    
    def get_total_lecturas(self, obj):
        return obj.lecturas.count()
    
    def get_total_comentarios(self, obj):
        return obj.comentarios.count()
    
    def get_usuario_ha_leido(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.lecturas.filter(usuario=request.user).exists()
        return False
    
    def get_destinatarios_display(self, obj):
        """Descripción legible de los destinatarios"""
        return obj.get_tipo_destinatario_display()


class AvisoDetailSerializer(serializers.ModelSerializer):
    """Serializer completo para detalles de avisos"""
    autor = AutorSerializer(read_only=True)
    comentarios = ComentarioAvisoSerializer(many=True, read_only=True)
    lecturas = LecturaAvisoSerializer(many=True, read_only=True)
    tiempo_transcurrido = serializers.SerializerMethodField()
    destinatarios_count = serializers.SerializerMethodField()
    destinatarios_display = serializers.SerializerMethodField()
    usuario_ha_leido = serializers.SerializerMethodField()
    puede_editar = serializers.SerializerMethodField()
    puede_eliminar = serializers.SerializerMethodField()
    
    class Meta:
        model = Aviso
        fields = [
            'id', 'titulo', 'contenido', 'resumen', 'autor', 'estado',
            'prioridad', 'tipo_destinatario', 'roles_destinatarios',
            'fecha_publicacion', 'fecha_vencimiento', 'fecha_creacion',
            'fecha_actualizacion', 'esta_vencido', 'esta_publicado',
            'requiere_confirmacion', 'adjunto', 'visualizaciones',
            'es_fijado', 'comentarios', 'lecturas', 'tiempo_transcurrido',
            'destinatarios_count', 'destinatarios_display', 'usuario_ha_leido',
            'puede_editar', 'puede_eliminar'
        ]
    
    def get_tiempo_transcurrido(self, obj):
        if obj.fecha_publicacion:
            delta = timezone.now() - obj.fecha_publicacion
            if delta.days > 0:
                return f"hace {delta.days} día(s)"
            elif delta.seconds > 3600:
                return f"hace {delta.seconds // 3600} hora(s)"
            else:
                return f"hace {delta.seconds // 60} minuto(s)"
        return "Sin publicar"
    
    def get_destinatarios_count(self, obj):
        return obj.get_destinatarios_queryset().count()
    
    def get_destinatarios_display(self, obj):
        return obj.get_tipo_destinatario_display()
    
    def get_usuario_ha_leido(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.lecturas.filter(usuario=request.user).exists()
        return False
    
    def get_puede_editar(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.autor == request.user or request.user.role == 'admin'
        return False
    
    def get_puede_eliminar(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.autor == request.user or request.user.role == 'admin'
        return False


class AvisoCreateUpdateSerializer(serializers.ModelSerializer):
    """Serializer para crear y actualizar avisos"""
    
    class Meta:
        model = Aviso
        fields = [
            'titulo', 'contenido', 'resumen', 'prioridad', 'tipo_destinatario',
            'roles_destinatarios', 'fecha_vencimiento', 'requiere_confirmacion',
            'adjunto', 'es_fijado'
        ]
        extra_kwargs = {
            'titulo': {'required': True, 'max_length': 200},
            'contenido': {'required': True},
        }
    
    def validate_titulo(self, value):
        """Validar título del aviso"""
        if len(value.strip()) < 5:
            raise serializers.ValidationError("El título debe tener al menos 5 caracteres.")
        return value.strip()
    
    def validate_contenido(self, value):
        """Validar contenido del aviso"""
        if len(value.strip()) < 10:
            raise serializers.ValidationError("El contenido debe tener al menos 10 caracteres.")
        return value.strip()
    
    def validate_roles_destinatarios(self, value):
        """Validar roles de destinatarios cuando es personalizado"""
        tipo_destinatario = self.initial_data.get('tipo_destinatario')
        
        if tipo_destinatario == 'personalizado':
            if not value or not isinstance(value, list):
                raise serializers.ValidationError(
                    "Debe especificar al menos un rol para selección personalizada."
                )
            
            roles_validos = [choice[0] for choice in User.ROLE_CHOICES]
            roles_invalidos = [rol for rol in value if rol not in roles_validos]
            
            if roles_invalidos:
                raise serializers.ValidationError(
                    f"Roles inválidos: {roles_invalidos}. Roles válidos: {roles_validos}"
                )
        
        return value
    
    def validate_fecha_vencimiento(self, value):
        """Validar que la fecha de vencimiento sea futura"""
        if value and value <= timezone.now():
            raise serializers.ValidationError(
                "La fecha de vencimiento debe ser futura."
            )
        return value
    
    def validate(self, attrs):
        """Validaciones adicionales"""
        # Si es personalizado pero no hay roles, usar todos
        if attrs.get('tipo_destinatario') == 'personalizado' and not attrs.get('roles_destinatarios'):
            attrs['roles_destinatarios'] = ['admin', 'resident', 'security']
        
        return attrs


class ComentarioAvisoCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear comentarios"""
    
    class Meta:
        model = ComentarioAviso
        fields = ['contenido', 'es_respuesta']
        extra_kwargs = {
            'contenido': {'required': True, 'min_length': 3}
        }
    
    def validate_contenido(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("El comentario debe tener al menos 3 caracteres.")
        return value.strip()


class EstadisticasAvisoSerializer(serializers.Serializer):
    """Serializer para estadísticas de avisos"""
    total_avisos = serializers.IntegerField()
    avisos_activos = serializers.IntegerField()
    avisos_vencidos = serializers.IntegerField()
    avisos_por_prioridad = serializers.DictField()
    avisos_por_tipo_destinatario = serializers.DictField()
    total_lecturas = serializers.IntegerField()
    total_comentarios = serializers.IntegerField()
    promedio_visualizaciones = serializers.FloatField()