from rest_framework import serializers
from .models import RostroRegistrado, VehiculoRegistrado, Acceso

class RostroRegistradoSerializer(serializers.ModelSerializer):
    """Serializer para rostros registrados"""
    usuario_nombre = serializers.CharField(source='usuario.get_full_name', read_only=True)
    imagen_rostro_url = serializers.ImageField(source='imagen_rostro', read_only=True)

    class Meta:
        model = RostroRegistrado
        fields = [
            'id', 'usuario', 'usuario_nombre', 'nombre_identificador',
            'imagen_rostro', 'imagen_rostro_url', 'embedding_ia',
            'fecha_registro', 'activo', 'confianza_minima'
        ]
        read_only_fields = ['id', 'fecha_registro', 'embedding_ia']

    def validate_confianza_minima(self, value):
        if not 0 <= value <= 1:
            raise serializers.ValidationError("La confianza mínima debe estar entre 0 y 1")
        return value

class RostroRegistroSerializer(serializers.Serializer):
    """Serializer para registrar un nuevo rostro con IA"""
    imagen_base64 = serializers.CharField(help_text="Imagen en base64 para procesar con IA")
    nombre_identificador = serializers.CharField(max_length=100)
    confianza_minima = serializers.FloatField(default=0.7, min_value=0, max_value=1)

class VehiculoRegistradoSerializer(serializers.ModelSerializer):
    """Serializer para vehículos registrados"""
    usuario_nombre = serializers.CharField(source='usuario.get_full_name', read_only=True)

    class Meta:
        model = VehiculoRegistrado
        fields = [
            'id', 'usuario', 'usuario_nombre', 'placa', 'marca', 'modelo',
            'color', 'descripcion', 'fecha_registro', 'activo'
        ]
        read_only_fields = ['id', 'fecha_registro', 'usuario', 'usuario_nombre']

    def validate_placa(self, value):
        """Validar formato de placa"""
        import re
        if not re.match(r'^\d{3,4}[A-Z]{3}$', value):
            raise serializers.ValidationError(
                'Formato de placa inválido. Use formato: 123ABC o 1234ABC'
            )
        return value.upper()

class AccesoSerializer(serializers.ModelSerializer):
    """Serializer para historial de accesos"""
    usuario_nombre = serializers.CharField(source='usuario.get_full_name', read_only=True)
    rostro_nombre = serializers.CharField(source='rostro_detectado.nombre_identificador', read_only=True)
    vehiculo_placa = serializers.CharField(source='vehiculo_detectado.placa', read_only=True)
    autorizado_por_nombre = serializers.CharField(source='autorizado_por.get_full_name', read_only=True)

    class Meta:
        model = Acceso
        fields = [
            'id', 'usuario', 'usuario_nombre', 'tipo_acceso', 'estado',
            'fecha_hora', 'ubicacion', 'rostro_detectado', 'rostro_nombre',
            'vehiculo_detectado', 'vehiculo_placa', 'confianza_ia',
            'datos_ia', 'observaciones', 'autorizado_por', 'autorizado_por_nombre'
        ]
        read_only_fields = ['id', 'fecha_hora']

class AccesoCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear nuevos accesos"""

    class Meta:
        model = Acceso
        fields = [
            'tipo_acceso', 'ubicacion', 'observaciones'
        ]

    def create(self, validated_data):
        # Agregar usuario del contexto de la request
        validated_data['usuario'] = self.context['request'].user
        return super().create(validated_data)

class ReconocimientoFacialSerializer(serializers.Serializer):
    """Serializer para reconocimiento facial"""
    imagen_base64 = serializers.CharField(help_text="Imagen en base64 para reconocimiento")
    ubicacion = serializers.CharField(max_length=100, default="Punto de acceso principal")

class LecturaPlacaSerializer(serializers.Serializer):
    """Serializer para lectura de placa"""
    imagen_base64 = serializers.CharField(help_text="Imagen de la placa en base64")
    ubicacion = serializers.CharField(max_length=100, default="Entrada vehicular")