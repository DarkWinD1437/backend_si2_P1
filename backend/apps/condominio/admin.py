from django.contrib import admin
from .models import *

# Admin para todos los modelos - CON PROTECCIÓN CONTRA ERRORES 500

@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ('id_rol', 'nombre', 'descripcion')
    search_fields = ('nombre',)

@admin.register(Usuario)
class UsuarioAdmin(admin.ModelAdmin):
    list_display = ('id_usuario', 'nombre', 'email', 'tipo', 'activo')
    list_filter = ('tipo', 'activo')
    search_fields = ('nombre', 'email')
    readonly_fields = ('fecha_registro',)
    
    def has_module_permission(self, request):
        # Evita errores si hay problemas de configuración
        try:
            return super().has_module_permission(request)
        except Exception:
            return False

@admin.register(AreaComun)
class AreaComunAdmin(admin.ModelAdmin):
    list_display = ('id_areacomun', 'nombre', 'capacidad', 'precio_hora', 'activa')
    list_filter = ('activa',)
    search_fields = ('nombre',)

@admin.register(Zona)
class ZonaAdmin(admin.ModelAdmin):
    list_display = ('id_zona', 'nombre', 'tipo')
    list_filter = ('tipo',)
    search_fields = ('nombre',)
    
    # Protección contra errores de ForeignKey
    def get_queryset(self, request):
        try:
            return super().get_queryset(request)
        except Exception:
            return self.model.objects.none()

@admin.register(Camara)
class CamaraAdmin(admin.ModelAdmin):
    list_display = ('id_camara', 'nombre', 'ubicacion', 'activa')
    list_filter = ('activa',)
    search_fields = ('nombre', 'ubicacion')

@admin.register(TipoEvento)
class TipoEventoAdmin(admin.ModelAdmin):
    list_display = ('id_tipoevento', 'nombre', 'severidad')
    list_filter = ('severidad',)
    search_fields = ('nombre',)

@admin.register(VehiculoAutorizado)
class VehiculoAutorizadoAdmin(admin.ModelAdmin):
    list_display = ('id_vehiculoautorizado', 'placa', 'modelo', 'color', 'activo')
    list_filter = ('activo', 'color')
    search_fields = ('placa', 'modelo')
    
    # Evitar errores con ForeignKey a Usuario
    def get_queryset(self, request):
        try:
            return super().get_queryset(request)
        except Exception:
            return self.model.objects.none()

@admin.register(UnidadHabitacional)
class UnidadHabitacionalAdmin(admin.ModelAdmin):
    list_display = ('id_unidadhabitacional', 'identificador', 'tipo', 'metros_cuadrados', 'activo')
    list_filter = ('tipo', 'activo')
    search_fields = ('identificador',)

@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('id_reserva', 'fecha_inicio', 'fecha_fin', 'estado')
    list_filter = ('estado', 'fecha_inicio')
    date_hierarchy = 'fecha_inicio'
    
    # Protección contra errores de relaciones
    def get_queryset(self, request):
        try:
            return super().get_queryset(request)
        except Exception:
            return self.model.objects.none()

@admin.register(Cuota)
class CuotaAdmin(admin.ModelAdmin):
    list_display = ('id_cuota', 'concepto', 'monto', 'fecha_vencimiento', 'estado')
    list_filter = ('estado', 'fecha_vencimiento')
    search_fields = ('concepto',)
    date_hierarchy = 'fecha_vencimiento'
    
    # Protección contra errores de relaciones
    def get_queryset(self, request):
        try:
            return super().get_queryset(request)
        except Exception:
            return self.model.objects.none()

@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = ('id_pago', 'monto', 'fecha_pago', 'metodo_pago', 'estado')
    list_filter = ('metodo_pago', 'estado', 'fecha_pago')
    date_hierarchy = 'fecha_pago'
    
    # Protección contra errores de relaciones
    def get_queryset(self, request):
        try:
            return super().get_queryset(request)
        except Exception:
            return self.model.objects.none()

@admin.register(Aviso)
class AvisoAdmin(admin.ModelAdmin):
    list_display = ('id_aviso', 'titulo', 'prioridad', 'fecha_publicacion', 'fecha_expiracion')
    list_filter = ('prioridad', 'fecha_publicacion')
    search_fields = ('titulo', 'contenido')
    date_hierarchy = 'fecha_publicacion'

@admin.register(EventoSeguridad)
class EventoSeguridadAdmin(admin.ModelAdmin):
    list_display = ('id_eventoseguridad', 'severidad', 'fecha_hora', 'revisado')
    list_filter = ('severidad', 'revisado', 'fecha_hora')
    search_fields = ('descripcion',)
    date_hierarchy = 'fecha_hora'
    
    # Protección contra errores de relaciones
    def get_queryset(self, request):
        try:
            return super().get_queryset(request)
        except Exception:
            return self.model.objects.none()

@admin.register(Mantenimiento)
class MantenimientoAdmin(admin.ModelAdmin):
    list_display = ('id_mantenimiento', 'descripcion', 'tipo', 'prioridad', 'estado', 'fecha_solicitud')
    list_filter = ('tipo', 'prioridad', 'estado')
    search_fields = ('descripcion',)
    date_hierarchy = 'fecha_solicitud'
    
    # Protección contra errores de relaciones
    def get_queryset(self, request):
        try:
            return super().get_queryset(request)
        except Exception:
            return self.model.objects.none()

@admin.register(Reporte)
class ReporteAdmin(admin.ModelAdmin):
    list_display = ('id_reporte', 'tipo_reporte', 'fecha_generacion')
    list_filter = ('tipo_reporte', 'fecha_generacion')
    date_hierarchy = 'fecha_generacion'
    
    # Protección contra errores de relaciones
    def get_queryset(self, request):
        try:
            return super().get_queryset(request)
        except Exception:
            return self.model.objects.none()

@admin.register(Bitacora)
class BitacoraAdmin(admin.ModelAdmin):
    list_display = ('id_bitacora', 'tabla_afectada', 'accion', 'fecha_hora')
    list_filter = ('tabla_afectada', 'accion', 'fecha_hora')
    search_fields = ('tabla_afectada', 'accion')
    date_hierarchy = 'fecha_hora'
    readonly_fields = ('fecha_hora',)
    
    # Protección contra errores de relaciones
    def get_queryset(self, request):
        try:
            return super().get_queryset(request)
        except Exception:
            return self.model.objects.none()
