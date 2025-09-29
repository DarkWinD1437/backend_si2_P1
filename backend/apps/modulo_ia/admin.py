from django.contrib import admin
from .models import RostroRegistrado, VehiculoRegistrado, Acceso

@admin.register(RostroRegistrado)
class RostroRegistradoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'nombre_identificador', 'activo', 'fecha_registro', 'confianza_minima']
    list_filter = ['activo', 'fecha_registro']
    search_fields = ['usuario__username', 'usuario__first_name', 'usuario__last_name', 'nombre_identificador']
    readonly_fields = ['id', 'fecha_registro', 'embedding_ia']

@admin.register(VehiculoRegistrado)
class VehiculoRegistradoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'placa', 'marca', 'modelo', 'activo', 'fecha_registro']
    list_filter = ['activo', 'fecha_registro', 'marca']
    search_fields = ['usuario__username', 'placa', 'marca', 'modelo']
    readonly_fields = ['id', 'fecha_registro']

@admin.register(Acceso)
class AccesoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'tipo_acceso', 'estado', 'ubicacion', 'fecha_hora', 'confianza_ia']
    list_filter = ['tipo_acceso', 'estado', 'fecha_hora', 'ubicacion']
    search_fields = ['usuario__username', 'ubicacion', 'observaciones']
    readonly_fields = ['id', 'fecha_hora']
    date_hierarchy = 'fecha_hora'