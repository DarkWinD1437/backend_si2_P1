from django.contrib import admin
from .models import Aviso, LecturaAviso, ComentarioAviso

@admin.register(Aviso)
class AvisoAdmin(admin.ModelAdmin):
    list_display = [
        'titulo', 'autor', 'estado', 'prioridad', 'tipo_destinatario',
        'fecha_publicacion', 'fecha_vencimiento', 'visualizaciones'
    ]
    list_filter = [
        'estado', 'prioridad', 'tipo_destinatario', 'requiere_confirmacion',
        'es_fijado', 'fecha_publicacion'
    ]
    search_fields = ['titulo', 'contenido', 'autor__username']
    readonly_fields = ['visualizaciones', 'fecha_creacion', 'fecha_actualizacion']
    date_hierarchy = 'fecha_publicacion'
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('titulo', 'contenido', 'resumen', 'autor')
        }),
        ('Configuración', {
            'fields': ('estado', 'prioridad', 'es_fijado', 'requiere_confirmacion')
        }),
        ('Destinatarios', {
            'fields': ('tipo_destinatario', 'roles_destinatarios', 'usuarios_destinatarios')
        }),
        ('Fechas', {
            'fields': ('fecha_publicacion', 'fecha_vencimiento')
        }),
        ('Archivos', {
            'fields': ('adjunto',)
        }),
        ('Estadísticas', {
            'fields': ('visualizaciones', 'fecha_creacion', 'fecha_actualizacion'),
            'classes': ('collapse',)
        })
    )
    
    def save_model(self, request, obj, form, change):
        if not change:  # Si es un nuevo objeto
            obj.autor = request.user
        super().save_model(request, obj, form, change)

@admin.register(LecturaAviso)
class LecturaAvisoAdmin(admin.ModelAdmin):
    list_display = ['aviso', 'usuario', 'fecha_lectura', 'confirmado']
    list_filter = ['confirmado', 'fecha_lectura']
    search_fields = ['aviso__titulo', 'usuario__username']
    date_hierarchy = 'fecha_lectura'

@admin.register(ComentarioAviso)
class ComentarioAvisoAdmin(admin.ModelAdmin):
    list_display = ['aviso', 'autor', 'fecha_creacion', 'es_respuesta']
    list_filter = ['fecha_creacion']
    search_fields = ['aviso__titulo', 'autor__username', 'contenido']
    date_hierarchy = 'fecha_creacion'