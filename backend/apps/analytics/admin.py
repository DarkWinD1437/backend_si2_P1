"""
Configuración del panel de administrador para el Módulo de Reportes y Analítica
Módulo 8: Reportes y Analítica
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import (
    ReporteFinanciero,
    ReporteSeguridad,
    ReporteUsoAreas,
    PrediccionMorosidad
)


@admin.register(ReporteFinanciero)
class ReporteFinancieroAdmin(admin.ModelAdmin):
    """Admin para Reportes Financieros"""

    list_display = [
        'titulo', 'tipo', 'periodo', 'formato', 'fecha_generacion',
        'generado_por', 'total_registros', 'get_estado_display'
    ]
    list_filter = ['tipo', 'periodo', 'formato', 'fecha_generacion', 'generado_por']
    search_fields = ['titulo', 'descripcion', 'generado_por__username']
    readonly_fields = ['id', 'fecha_generacion', 'datos', 'total_registros']
    ordering = ['-fecha_generacion']

    fieldsets = (
        ('Información Básica', {
            'fields': ('titulo', 'descripcion', 'tipo', 'periodo', 'formato')
        }),
        ('Fechas', {
            'fields': ('fecha_inicio', 'fecha_fin', 'fecha_generacion')
        }),
        ('Usuario y Filtros', {
            'fields': ('generado_por', 'filtros_aplicados')
        }),
        ('Datos del Reporte', {
            'fields': ('datos', 'total_registros'),
            'classes': ('collapse',)
        }),
    )

    def get_estado_display(self, obj):
        return "Completado"
    get_estado_display.short_description = "Estado"


@admin.register(ReporteSeguridad)
class ReporteSeguridadAdmin(admin.ModelAdmin):
    """Admin para Reportes de Seguridad"""

    list_display = [
        'titulo', 'tipo', 'periodo', 'fecha_generacion', 'generado_por',
        'total_eventos', 'eventos_criticos', 'alertas_generadas'
    ]
    list_filter = ['tipo', 'periodo', 'fecha_generacion', 'generado_por']
    search_fields = ['titulo', 'descripcion', 'generado_por__username']
    readonly_fields = ['id', 'fecha_generacion', 'datos', 'total_eventos', 'eventos_criticos', 'alertas_generadas']
    ordering = ['-fecha_generacion']

    fieldsets = (
        ('Información Básica', {
            'fields': ('titulo', 'descripcion', 'tipo', 'periodo')
        }),
        ('Fechas', {
            'fields': ('fecha_inicio', 'fecha_fin', 'fecha_generacion')
        }),
        ('Usuario y Filtros', {
            'fields': ('generado_por', 'filtros_aplicados')
        }),
        ('Estadísticas', {
            'fields': ('total_eventos', 'eventos_criticos', 'alertas_generadas')
        }),
        ('Datos del Reporte', {
            'fields': ('datos',),
            'classes': ('collapse',)
        }),
    )


@admin.register(ReporteUsoAreas)
class ReporteUsoAreasAdmin(admin.ModelAdmin):
    """Admin para Reportes de Uso de Áreas"""

    list_display = [
        'titulo', 'area', 'periodo', 'metrica_principal', 'fecha_generacion',
        'generado_por', 'total_reservas', 'tasa_ocupacion_promedio'
    ]
    list_filter = ['area', 'periodo', 'metrica_principal', 'fecha_generacion', 'generado_por']
    search_fields = ['titulo', 'descripcion', 'generado_por__username']
    readonly_fields = ['id', 'fecha_generacion', 'datos', 'total_reservas', 'horas_ocupacion', 'tasa_ocupacion_promedio']
    ordering = ['-fecha_generacion']

    fieldsets = (
        ('Información Básica', {
            'fields': ('titulo', 'descripcion', 'area', 'periodo', 'metrica_principal')
        }),
        ('Fechas', {
            'fields': ('fecha_inicio', 'fecha_fin', 'fecha_generacion')
        }),
        ('Usuario y Filtros', {
            'fields': ('generado_por', 'filtros_aplicados')
        }),
        ('Estadísticas', {
            'fields': ('total_reservas', 'horas_ocupacion', 'tasa_ocupacion_promedio')
        }),
        ('Datos del Reporte', {
            'fields': ('datos',),
            'classes': ('collapse',)
        }),
    )


@admin.register(PrediccionMorosidad)
class PrediccionMorosidadAdmin(admin.ModelAdmin):
    """Admin para Predicciones de Morosidad"""

    list_display = [
        'titulo', 'modelo_usado', 'nivel_confianza', 'fecha_prediccion',
        'generado_por', 'total_residentes_analizados', 'residentes_riesgo_alto',
        'precision_modelo', 'riesgo_porcentaje'
    ]
    list_filter = ['modelo_usado', 'nivel_confianza', 'fecha_prediccion', 'generado_por']
    search_fields = ['titulo', 'descripcion', 'generado_por__username']
    readonly_fields = [
        'id', 'fecha_prediccion', 'datos_entrada', 'resultados',
        'total_residentes_analizados', 'residentes_riesgo_alto', 'residentes_riesgo_medio',
        'precision_modelo', 'parametros_modelo', 'metricas_evaluacion', 'riesgo_porcentaje'
    ]
    ordering = ['-fecha_prediccion']

    fieldsets = (
        ('Información Básica', {
            'fields': ('titulo', 'descripcion', 'modelo_usado', 'nivel_confianza', 'periodo_predicho')
        }),
        ('Fechas', {
            'fields': ('fecha_prediccion',)
        }),
        ('Usuario', {
            'fields': ('generado_por',)
        }),
        ('Estadísticas de Predicción', {
            'fields': (
                'total_residentes_analizados', 'residentes_riesgo_alto',
                'residentes_riesgo_medio', 'precision_modelo', 'riesgo_porcentaje'
            )
        }),
        ('Datos de Entrada', {
            'fields': ('datos_entrada',),
            'classes': ('collapse',)
        }),
        ('Resultados', {
            'fields': ('resultados',),
            'classes': ('collapse',)
        }),
        ('Configuración del Modelo', {
            'fields': ('parametros_modelo', 'metricas_evaluacion'),
            'classes': ('collapse',)
        }),
    )

    def riesgo_porcentaje(self, obj):
        return f"{obj.get_riesgo_porcentaje()}%"
    riesgo_porcentaje.short_description = "Riesgo Total (%)"