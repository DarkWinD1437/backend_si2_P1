"""
Serializers para el Módulo de Reportes y Analítica
Módulo 8: Reportes y Analítica
"""

from rest_framework import serializers
from django.utils import timezone
from .models import (
    ReporteFinanciero,
    ReporteSeguridad,
    ReporteUsoAreas,
    PrediccionMorosidad
)


class ReporteFinancieroSerializer(serializers.ModelSerializer):
    """Serializer para ReporteFinanciero"""

    generado_por_info = serializers.SerializerMethodField()

    class Meta:
        model = ReporteFinanciero
        fields = [
            'id', 'titulo', 'descripcion', 'tipo', 'periodo', 'formato',
            'fecha_inicio', 'fecha_fin', 'fecha_generacion', 'generado_por',
            'generado_por_info', 'datos', 'total_registros', 'filtros_aplicados'
        ]
        read_only_fields = ['id', 'fecha_generacion', 'generado_por_info']

    def get_generado_por_info(self, obj):
        return {
            'id': obj.generado_por.id,
            'username': obj.generado_por.username,
            'email': obj.generado_por.email,
            'role': obj.generado_por.role
        }


class CrearReporteFinancieroSerializer(serializers.ModelSerializer):
    """Serializer para crear reportes financieros"""

    class Meta:
        model = ReporteFinanciero
        fields = [
            'titulo', 'descripcion', 'tipo', 'periodo', 'formato',
            'fecha_inicio', 'fecha_fin', 'filtros_aplicados'
        ]

    def validate_fecha_fin(self, value):
        """Validar que fecha_fin no sea anterior a fecha_inicio"""
        fecha_inicio = self.initial_data.get('fecha_inicio')
        if fecha_inicio and value < fecha_inicio:
            raise serializers.ValidationError("La fecha de fin no puede ser anterior a la fecha de inicio")
        return value


class ReporteFinancieroListSerializer(serializers.ModelSerializer):
    """Serializer para listar reportes financieros"""

    generado_por_info = serializers.SerializerMethodField()

    class Meta:
        model = ReporteFinanciero
        fields = [
            'id', 'titulo', 'tipo', 'periodo', 'formato',
            'fecha_inicio', 'fecha_fin', 'fecha_generacion',
            'generado_por_info', 'total_registros'
        ]

    def get_generado_por_info(self, obj):
        return {
            'username': obj.generado_por.username,
            'role': obj.generado_por.role
        }


class ReporteSeguridadSerializer(serializers.ModelSerializer):
    """Serializer para ReporteSeguridad"""

    generado_por_info = serializers.SerializerMethodField()

    class Meta:
        model = ReporteSeguridad
        fields = [
            'id', 'titulo', 'descripcion', 'tipo', 'periodo',
            'fecha_inicio', 'fecha_fin', 'fecha_generacion', 'generado_por',
            'generado_por_info', 'datos', 'total_eventos', 'eventos_criticos',
            'alertas_generadas', 'filtros_aplicados'
        ]
        read_only_fields = ['id', 'fecha_generacion', 'generado_por_info']

    def get_generado_por_info(self, obj):
        return {
            'id': obj.generado_por.id,
            'username': obj.generado_por.username,
            'email': obj.generado_por.email,
            'role': obj.generado_por.role
        }


class CrearReporteSeguridadSerializer(serializers.ModelSerializer):
    """Serializer para crear reportes de seguridad"""

    class Meta:
        model = ReporteSeguridad
        fields = [
            'titulo', 'descripcion', 'tipo', 'periodo',
            'fecha_inicio', 'fecha_fin', 'filtros_aplicados'
        ]

    def validate_fecha_fin(self, value):
        """Validar que fecha_fin no sea anterior a fecha_inicio"""
        fecha_inicio = self.initial_data.get('fecha_inicio')
        if fecha_inicio and value < fecha_inicio:
            raise serializers.ValidationError("La fecha de fin no puede ser anterior a la fecha de inicio")
        return value


class ReporteSeguridadListSerializer(serializers.ModelSerializer):
    """Serializer para listar reportes de seguridad"""

    generado_por_info = serializers.SerializerMethodField()

    class Meta:
        model = ReporteSeguridad
        fields = [
            'id', 'titulo', 'tipo', 'periodo',
            'fecha_inicio', 'fecha_fin', 'fecha_generacion',
            'generado_por_info', 'total_eventos', 'eventos_criticos'
        ]

    def get_generado_por_info(self, obj):
        return {
            'username': obj.generado_por.username,
            'role': obj.generado_por.role
        }


class ReporteUsoAreasSerializer(serializers.ModelSerializer):
    """Serializer para ReporteUsoAreas"""

    generado_por_info = serializers.SerializerMethodField()

    class Meta:
        model = ReporteUsoAreas
        fields = [
            'id', 'titulo', 'descripcion', 'area', 'periodo', 'metrica_principal',
            'fecha_inicio', 'fecha_fin', 'fecha_generacion', 'generado_por',
            'generado_por_info', 'datos', 'total_reservas', 'horas_ocupacion',
            'tasa_ocupacion_promedio', 'filtros_aplicados'
        ]
        read_only_fields = ['id', 'fecha_generacion', 'generado_por_info']

    def get_generado_por_info(self, obj):
        return {
            'id': obj.generado_por.id,
            'username': obj.generado_por.username,
            'email': obj.generado_por.email,
            'role': obj.generado_por.role
        }


class CrearReporteUsoAreasSerializer(serializers.ModelSerializer):
    """Serializer para crear reportes de uso de áreas"""

    class Meta:
        model = ReporteUsoAreas
        fields = [
            'titulo', 'descripcion', 'area', 'periodo', 'metrica_principal',
            'fecha_inicio', 'fecha_fin', 'filtros_aplicados'
        ]

    def validate_fecha_fin(self, value):
        """Validar que fecha_fin no sea anterior a fecha_inicio"""
        fecha_inicio = self.initial_data.get('fecha_inicio')
        if fecha_inicio and value < fecha_inicio:
            raise serializers.ValidationError("La fecha de fin no puede ser anterior a la fecha de inicio")
        return value


class ReporteUsoAreasListSerializer(serializers.ModelSerializer):
    """Serializer para listar reportes de uso de áreas"""

    generado_por_info = serializers.SerializerMethodField()

    class Meta:
        model = ReporteUsoAreas
        fields = [
            'id', 'titulo', 'area', 'periodo', 'metrica_principal',
            'fecha_inicio', 'fecha_fin', 'fecha_generacion',
            'generado_por_info', 'total_reservas', 'tasa_ocupacion_promedio'
        ]

    def get_generado_por_info(self, obj):
        return {
            'username': obj.generado_por.username,
            'role': obj.generado_por.role
        }


class PrediccionMorosidadSerializer(serializers.ModelSerializer):
    """Serializer para PrediccionMorosidad"""

    generado_por_info = serializers.SerializerMethodField()
    riesgo_porcentaje = serializers.SerializerMethodField()
    residente_info = serializers.SerializerMethodField()

    class Meta:
        model = PrediccionMorosidad
        fields = [
            'id', 'titulo', 'descripcion', 'modelo_usado', 'nivel_confianza',
            'fecha_prediccion', 'periodo_predicho', 'generado_por',
            'generado_por_info', 'residente_especifico', 'residente',
            'residente_info', 'datos_entrada', 'resultados',
            'total_residentes_analizados', 'residentes_riesgo_alto',
            'residentes_riesgo_medio', 'precision_modelo', 'riesgo_porcentaje',
            'parametros_modelo', 'metricas_evaluacion'
        ]
        read_only_fields = ['id', 'fecha_prediccion', 'generado_por_info', 'riesgo_porcentaje', 'residente_info']

    def get_generado_por_info(self, obj):
        return {
            'id': obj.generado_por.id,
            'username': obj.generado_por.username,
            'email': obj.generado_por.email,
            'role': obj.generado_por.role
        }

    def get_residente_info(self, obj):
        if obj.residente:
            return {
                'id': obj.residente.id,
                'username': obj.residente.username,
                'email': obj.residente.email,
                'first_name': obj.residente.first_name,
                'last_name': obj.residente.last_name
            }
        return None

    def get_riesgo_porcentaje(self, obj):
        return obj.get_riesgo_porcentaje()


class CrearPrediccionMorosidadSerializer(serializers.ModelSerializer):
    """Serializer para crear predicciones de morosidad"""

    residente_id = serializers.IntegerField(required=False, allow_null=True,
                                           help_text="ID del residente específico para predicción individual")

    class Meta:
        model = PrediccionMorosidad
        fields = [
            'titulo', 'descripcion', 'modelo_usado', 'periodo_predicho',
            'datos_entrada', 'parametros_modelo', 'residente_id'
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Establecer valor por defecto para modelo_usado
        if 'modelo_usado' in self.fields:
            self.fields['modelo_usado'].default = 'grok-4-fast-free'
            self.fields['modelo_usado'].required = False

    def validate(self, attrs):
        # Asegurar que modelo_usado tenga el valor correcto
        if 'modelo_usado' not in attrs or not attrs['modelo_usado']:
            attrs['modelo_usado'] = 'grok-4-fast-free'
        return attrs


class PrediccionMorosidadListSerializer(serializers.ModelSerializer):
    """Serializer para listar predicciones de morosidad"""

    generado_por_info = serializers.SerializerMethodField()
    riesgo_porcentaje = serializers.SerializerMethodField()
    residente_info = serializers.SerializerMethodField()

    class Meta:
        model = PrediccionMorosidad
        fields = [
            'id', 'titulo', 'modelo_usado', 'nivel_confianza',
            'fecha_prediccion', 'periodo_predicho', 'generado_por_info',
            'residente_especifico', 'residente_info', 'total_residentes_analizados',
            'residentes_riesgo_alto', 'residentes_riesgo_medio', 'precision_modelo',
            'riesgo_porcentaje'
        ]

    def get_generado_por_info(self, obj):
        return {
            'username': obj.generado_por.username,
            'role': obj.generado_por.role
        }

    def get_residente_info(self, obj):
        if obj.residente:
            return {
                'id': obj.residente.id,
                'username': obj.residente.username,
                'first_name': obj.residente.first_name,
                'last_name': obj.residente.last_name
            }
        return None

    def get_riesgo_porcentaje(self, obj):
        return obj.get_riesgo_porcentaje()