from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import RegistroAuditoria, SesionUsuario, EstadisticasAuditoria


@admin.register(RegistroAuditoria)
class RegistroAuditoriaAdmin(admin.ModelAdmin):
    list_display = [
        'timestamp',
        'usuario_display',
        'tipo_actividad_display',
        'descripcion_corta',
        'nivel_importancia_display',
        'es_exitoso_display',
        'objeto_afectado'
    ]
    
    list_filter = [
        'tipo_actividad',
        'nivel_importancia',
        'es_exitoso',
        ('timestamp', admin.DateFieldListFilter),
        ('usuario', admin.RelatedOnlyFieldListFilter),
    ]
    
    search_fields = [
        'usuario__username',
        'usuario__email',
        'descripcion',
        'ip_address'
    ]
    
    readonly_fields = [
        'timestamp',
        'usuario',
        'tipo_actividad',
        'descripcion',
        'nivel_importancia',
        'content_type',
        'object_id',
        'ip_address',
        'user_agent',
        'datos_adicionales',
        'datos_anteriores',
        'datos_nuevos',
        'es_exitoso',
        'mensaje_error'
    ]
    
    date_hierarchy = 'timestamp'
    
    ordering = ['-timestamp']
    
    def has_add_permission(self, request):
        """No permitir agregar registros manualmente"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """No permitir modificar registros"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Solo superusuarios pueden eliminar registros"""
        return request.user.is_superuser
    
    def usuario_display(self, obj):
        """Mostrar usuario con enlace"""
        if obj.usuario:
            url = reverse('admin:users_user_changelist')
            return format_html(
                '<a href="{}?id={}" target="_blank">{}</a>',
                url,
                obj.usuario.id,
                obj.usuario.username
            )
        return format_html('<span style="color: #666;">Sistema</span>')
    usuario_display.short_description = 'Usuario'
    usuario_display.admin_order_field = 'usuario__username'
    
    def tipo_actividad_display(self, obj):
        """Mostrar tipo de actividad con color"""
        colors = {
            'login': '#28a745',
            'logout': '#6c757d',
            'crear': '#007bff',
            'actualizar': '#ffc107',
            'eliminar': '#dc3545',
            'pago': '#17a2b8',
            'error_sistema': '#dc3545'
        }
        color = colors.get(obj.tipo_actividad, '#6c757d')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_tipo_actividad_display()
        )
    tipo_actividad_display.short_description = 'Tipo'
    tipo_actividad_display.admin_order_field = 'tipo_actividad'
    
    def descripcion_corta(self, obj):
        """Mostrar descripción truncada"""
        if len(obj.descripcion) > 50:
            return obj.descripcion[:50] + '...'
        return obj.descripcion
    descripcion_corta.short_description = 'Descripción'
    
    def nivel_importancia_display(self, obj):
        """Mostrar nivel de importancia con color"""
        color = obj.get_nivel_color()
        return format_html(
            '<span style="background-color: {}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.get_nivel_importancia_display()
        )
    nivel_importancia_display.short_description = 'Importancia'
    nivel_importancia_display.admin_order_field = 'nivel_importancia'
    
    def es_exitoso_display(self, obj):
        """Mostrar estado de éxito con íconos"""
        if obj.es_exitoso:
            return format_html('<span style="color: green;">✓ Exitoso</span>')
        else:
            return format_html('<span style="color: red;">✗ Error</span>')
    es_exitoso_display.short_description = 'Estado'
    es_exitoso_display.admin_order_field = 'es_exitoso'
    
    def objeto_afectado(self, obj):
        """Mostrar objeto afectado si existe"""
        return obj.objeto_afectado_str
    objeto_afectado.short_description = 'Objeto'
    
    fieldsets = (
        ('Información General', {
            'fields': ('timestamp', 'usuario', 'tipo_actividad', 'nivel_importancia', 'es_exitoso')
        }),
        ('Descripción', {
            'fields': ('descripcion',)
        }),
        ('Objeto Afectado', {
            'fields': ('content_type', 'object_id'),
            'classes': ('collapse',)
        }),
        ('Información Técnica', {
            'fields': ('ip_address', 'user_agent'),
            'classes': ('collapse',)
        }),
        ('Datos Adicionales', {
            'fields': ('datos_adicionales', 'datos_anteriores', 'datos_nuevos'),
            'classes': ('collapse',)
        }),
        ('Errores', {
            'fields': ('mensaje_error',),
            'classes': ('collapse',)
        }),
    )


@admin.register(SesionUsuario)
class SesionUsuarioAdmin(admin.ModelAdmin):
    list_display = [
        'usuario',
        'fecha_inicio',
        'fecha_ultimo_acceso',
        'duracion_display',
        'esta_activa_display',
        'ip_address'
    ]
    
    list_filter = [
        'esta_activa',
        ('fecha_inicio', admin.DateFieldListFilter),
        ('usuario', admin.RelatedOnlyFieldListFilter),
    ]
    
    search_fields = [
        'usuario__username',
        'usuario__email',
        'ip_address'
    ]
    
    readonly_fields = [
        'token_session',
        'fecha_inicio',
        'fecha_ultimo_acceso',
        'duracion_display'
    ]
    
    ordering = ['-fecha_inicio']
    
    def has_add_permission(self, request):
        """No permitir agregar sesiones manualmente"""
        return False
    
    def duracion_display(self, obj):
        """Mostrar duración de la sesión"""
        duracion = obj.duracion_sesion
        horas = int(duracion.total_seconds() // 3600)
        minutos = int((duracion.total_seconds() % 3600) // 60)
        return f"{horas}h {minutos}m"
    duracion_display.short_description = 'Duración'
    
    def esta_activa_display(self, obj):
        """Mostrar estado de sesión con colores"""
        if obj.esta_activa:
            return format_html('<span style="color: green;">● Activa</span>')
        else:
            return format_html('<span style="color: red;">● Cerrada</span>')
    esta_activa_display.short_description = 'Estado'
    esta_activa_display.admin_order_field = 'esta_activa'


@admin.register(EstadisticasAuditoria)
class EstadisticasAuditoriaAdmin(admin.ModelAdmin):
    list_display = [
        'fecha',
        'total_actividades',
        'total_logins',
        'total_usuarios_activos',
        'actividades_criticas',
        'errores_sistema'
    ]
    
    list_filter = [
        ('fecha', admin.DateFieldListFilter),
    ]
    
    ordering = ['-fecha']
    
    readonly_fields = [
        'fecha',
        'total_actividades',
        'total_logins',
        'total_usuarios_activos',
        'actividades_criticas',
        'errores_sistema',
        'datos_estadisticas'
    ]
    
    def has_add_permission(self, request):
        """No permitir agregar estadísticas manualmente"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """No permitir modificar estadísticas"""
        return False