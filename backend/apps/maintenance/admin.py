"""
Configuración del panel de administrador para el Módulo de Mantenimiento
Módulo 7: Gestión de Mantenimiento
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import SolicitudMantenimiento, TareaMantenimiento


@admin.register(SolicitudMantenimiento)
class SolicitudMantenimientoAdmin(admin.ModelAdmin):
    """Admin para Solicitudes de Mantenimiento"""

    list_display = [
        'id', 'descripcion_corta', 'ubicacion', 'prioridad', 'estado',
        'fecha_solicitud', 'solicitante', 'tiene_tarea'
    ]
    list_filter = ['estado', 'prioridad', 'fecha_solicitud', 'ubicacion']
    search_fields = ['descripcion', 'ubicacion', 'solicitante__username', 'solicitante__email']
    readonly_fields = ['id', 'fecha_solicitud']
    ordering = ['-fecha_solicitud']

    fieldsets = (
        ('Información Básica', {
            'fields': ('descripcion', 'ubicacion', 'prioridad', 'estado')
        }),
        ('Fechas', {
            'fields': ('fecha_solicitud',)
        }),
        ('Usuario', {
            'fields': ('solicitante',)
        }),
    )

    def descripcion_corta(self, obj):
        return obj.descripcion[:50] + "..." if len(obj.descripcion) > 50 else obj.descripcion
    descripcion_corta.short_description = "Descripción"

    def tiene_tarea(self, obj):
        return hasattr(obj, 'tarea')
    tiene_tarea.boolean = True
    tiene_tarea.short_description = "Tiene Tarea"


@admin.register(TareaMantenimiento)
class TareaMantenimientoAdmin(admin.ModelAdmin):
    """Admin para Tareas de Mantenimiento"""

    list_display = [
        'id', 'solicitud_link', 'descripcion_corta', 'asignado_a',
        'estado', 'fecha_asignacion', 'fecha_completado', 'prioridad_display'
    ]
    list_filter = ['estado', 'fecha_asignacion', 'fecha_completado', 'asignado_a']
    search_fields = ['descripcion_tarea', 'notas', 'asignado_a__username', 'solicitud__descripcion']
    readonly_fields = ['id', 'fecha_asignacion', 'fecha_completado']
    ordering = ['-fecha_asignacion']

    fieldsets = (
        ('Información Básica', {
            'fields': ('solicitud', 'descripcion_tarea', 'estado')
        }),
        ('Asignación', {
            'fields': ('asignado_a', 'notas')
        }),
        ('Fechas', {
            'fields': ('fecha_asignacion', 'fecha_completado')
        }),
    )

    def solicitud_link(self, obj):
        url = reverse('admin:maintenance_solicitudmantenimiento_change', args=[obj.solicitud.id])
        return format_html('<a href="{}">{}</a>', url, f"Solicitud #{obj.solicitud.id}")
    solicitud_link.short_description = "Solicitud"

    def descripcion_corta(self, obj):
        return obj.descripcion_tarea[:50] + "..." if len(obj.descripcion_tarea) > 50 else obj.descripcion_tarea
    descripcion_corta.short_description = "Descripción"

    def prioridad_display(self, obj):
        prioridades = {
            'baja': '🟢 Baja',
            'media': '🟡 Media',
            'alta': '🔴 Alta',
            'urgente': '🚨 Urgente'
        }
        return prioridades.get(obj.solicitud.prioridad, obj.solicitud.prioridad)
    prioridad_display.short_description = "Prioridad"