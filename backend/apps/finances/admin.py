"""
Configuración del Admin Panel para el Módulo de Gestión Financiera
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import ConceptoFinanciero, CargoFinanciero


@admin.register(ConceptoFinanciero)
class ConceptoFinancieroAdmin(admin.ModelAdmin):
    list_display = [
        'nombre', 'tipo', 'monto', 'estado', 'fecha_vigencia_desde',
        'fecha_vigencia_hasta', 'es_recurrente', 'esta_vigente_badge'
    ]
    list_filter = [
        'tipo', 'estado', 'es_recurrente', 'aplica_a_todos',
        'fecha_vigencia_desde', 'fecha_creacion'
    ]
    search_fields = ['nombre', 'descripcion']
    readonly_fields = ['creado_por', 'fecha_creacion', 'fecha_modificacion', 'esta_vigente']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('nombre', 'descripcion', 'tipo', 'monto')
        }),
        ('Configuración', {
            'fields': ('estado', 'es_recurrente', 'aplica_a_todos')
        }),
        ('Vigencia', {
            'fields': ('fecha_vigencia_desde', 'fecha_vigencia_hasta')
        }),
        ('Metadatos', {
            'fields': ('creado_por', 'fecha_creacion', 'fecha_modificacion', 'esta_vigente'),
            'classes': ('collapse',)
        })
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Si es un nuevo objeto
            obj.creado_por = request.user
        super().save_model(request, obj, form, change)
    
    def esta_vigente_badge(self, obj):
        if obj.esta_vigente:
            return format_html('<span style="color: green;">✓ Vigente</span>')
        return format_html('<span style="color: red;">✗ No vigente</span>')
    esta_vigente_badge.short_description = 'Vigente'


@admin.register(CargoFinanciero)
class CargoFinancieroAdmin(admin.ModelAdmin):
    list_display = [
        'concepto', 'residente', 'monto', 'estado', 'fecha_aplicacion',
        'fecha_vencimiento', 'esta_vencido_badge', 'aplicado_por'
    ]
    list_filter = [
        'estado', 'concepto__tipo', 'fecha_aplicacion', 'fecha_vencimiento',
        'aplicado_por'
    ]
    search_fields = [
        'concepto__nombre', 'residente__username', 'residente__first_name',
        'residente__last_name', 'observaciones', 'referencia_pago'
    ]
    readonly_fields = [
        'aplicado_por', 'fecha_creacion', 'fecha_modificacion',
        'esta_vencido', 'dias_para_vencimiento'
    ]
    
    fieldsets = (
        ('Cargo', {
            'fields': ('concepto', 'residente', 'monto')
        }),
        ('Estado y Fechas', {
            'fields': ('estado', 'fecha_aplicacion', 'fecha_vencimiento', 'fecha_pago')
        }),
        ('Información de Pago', {
            'fields': ('referencia_pago', 'observaciones')
        }),
        ('Metadatos', {
            'fields': (
                'aplicado_por', 'fecha_creacion', 'fecha_modificacion',
                'esta_vencido', 'dias_para_vencimiento'
            ),
            'classes': ('collapse',)
        })
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Si es un nuevo objeto
            obj.aplicado_por = request.user
        super().save_model(request, obj, form, change)
    
    def esta_vencido_badge(self, obj):
        if obj.esta_vencido:
            return format_html('<span style="color: red;">⚠ Vencido</span>')
        elif obj.estado == 'pagado':
            return format_html('<span style="color: green;">✓ Pagado</span>')
        else:
            dias = obj.dias_para_vencimiento
            if dias is not None:
                if dias < 0:
                    return format_html('<span style="color: red;">⚠ Vencido</span>')
                elif dias <= 7:
                    return format_html(f'<span style="color: orange;">⚠ {dias} días</span>')
                else:
                    return format_html(f'<span style="color: blue;">{dias} días</span>')
            return '-'
    esta_vencido_badge.short_description = 'Estado/Vencimiento'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('concepto', 'residente', 'aplicado_por')


# Configuraciones adicionales del admin
admin.site.site_header = "Smart Condominium - Administración"
admin.site.site_title = "Smart Condominium Admin"
admin.site.index_title = "Panel de Administración"