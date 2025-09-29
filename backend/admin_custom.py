"""
Configuración personalizada del panel de administrador de Django
Organiza los módulos en secciones temáticas y registra todos los modelos
"""

from django.contrib import admin
from django.contrib.admin.sites import AdminSite
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html

# Importar modelos y admin classes de todas las aplicaciones
from backend.apps.users.models import User
from backend.apps.audit.models import RegistroAuditoria, SesionUsuario, EstadisticasAuditoria
from backend.apps.communications.models import Aviso, LecturaAviso, ComentarioAviso
from backend.apps.condominio.models import (
    Rol, Usuario, AreaComun, Zona, Camara, TipoEvento, VehiculoAutorizado,
    UnidadHabitacional, Reserva, Cuota, Pago, Aviso as AvisoCondominio,
    EventoSeguridad, Mantenimiento, Reporte, Bitacora
)
from backend.apps.finances.models import ConceptoFinanciero, CargoFinanciero
from backend.apps.maintenance.models import SolicitudMantenimiento, TareaMantenimiento
from backend.apps.modulo_ia.models import RostroRegistrado, VehiculoRegistrado, Acceso
from backend.apps.analytics.models import ReporteFinanciero, ReporteSeguridad, ReporteUsoAreas, PrediccionMorosidad

# Importar admin classes existentes
from backend.apps.users.admin import CustomUserAdmin
from backend.apps.audit.admin import RegistroAuditoriaAdmin, SesionUsuarioAdmin, EstadisticasAuditoriaAdmin
from backend.apps.communications.admin import AvisoAdmin as CommunicationsAvisoAdmin, LecturaAvisoAdmin, ComentarioAvisoAdmin
from backend.apps.condominio.admin import (
    RolAdmin, UsuarioAdmin, AreaComunAdmin, ZonaAdmin, CamaraAdmin, TipoEventoAdmin,
    VehiculoAutorizadoAdmin, UnidadHabitacionalAdmin, ReservaAdmin, CuotaAdmin,
    PagoAdmin, AvisoAdmin as CondominioAvisoAdmin, EventoSeguridadAdmin,
    MantenimientoAdmin, ReporteAdmin, BitacoraAdmin
)
from backend.apps.finances.admin import ConceptoFinancieroAdmin, CargoFinancieroAdmin
from backend.apps.maintenance.admin import SolicitudMantenimientoAdmin, TareaMantenimientoAdmin
from backend.apps.analytics.admin import ReporteFinancieroAdmin, ReporteSeguridadAdmin, ReporteUsoAreasAdmin, PrediccionMorosidadAdmin


class SmartCondominiumAdminSite(AdminSite):
    """Admin site personalizado para SmartCondominium"""

    site_header = _("Administración SmartCondominium")
    site_title = _("SmartCondominium Admin")
    index_title = _("Panel de Administración")
    site_url = None

    def get_app_list(self, request):
        """
        Organiza las aplicaciones en secciones temáticas
        """
        app_list = super().get_app_list(request)

        # Definir las secciones personalizadas
        sections = {
            'gestión_mantenimiento': {
                'name': 'Gestión de Mantenimiento',
                'app_label': 'maintenance',
                'models': [
                    'maintenance.SolicitudMantenimiento',
                    'maintenance.TareaMantenimiento'
                ],
                'icon': '🔧'
            },
            'reportes_analiticas': {
                'name': 'Reportes y Analíticas',
                'app_label': 'analytics',
                'models': [
                    'analytics.ReporteFinanciero',
                    'analytics.ReporteSeguridad',
                    'analytics.ReporteUsoAreas',
                    'analytics.PrediccionMorosidad'
                ],
                'icon': '📊'
            }
        }

        # Crear lista organizada
        organized_apps = []

        # Agregar sección de Gestión de Mantenimiento
        maintenance_models = []
        for app in app_list:
            if app['app_label'] == 'maintenance':
                for model in app['models']:
                    if f"{app['app_label']}.{model['object_name']}" in sections['gestión_mantenimiento']['models']:
                        maintenance_models.append(model)

        if maintenance_models:
            organized_apps.append({
                'name': f"{sections['gestión_mantenimiento']['icon']} {sections['gestión_mantenimiento']['name']}",
                'app_label': sections['gestión_mantenimiento']['app_label'],
                'app_url': f"/admin/{sections['gestión_mantenimiento']['app_label']}/",
                'has_module_perms': True,
                'models': maintenance_models
            })

        # Agregar sección de Reportes y Analíticas
        analytics_models = []
        for app in app_list:
            if app['app_label'] == 'analytics':
                for model in app['models']:
                    if f"{app['app_label']}.{model['object_name']}" in sections['reportes_analiticas']['models']:
                        analytics_models.append(model)

        if analytics_models:
            organized_apps.append({
                'name': f"{sections['reportes_analiticas']['icon']} {sections['reportes_analiticas']['name']}",
                'app_label': sections['reportes_analiticas']['app_label'],
                'app_url': f"/admin/{sections['reportes_analiticas']['app_label']}/",
                'has_module_perms': True,
                'models': analytics_models
            })

        # Agregar otras aplicaciones que no estén en las secciones personalizadas
        for app in app_list:
            if app['app_label'] not in ['maintenance', 'analytics']:
                organized_apps.append(app)

        return organized_apps


# Crear instancia del admin site personalizado
admin_site = SmartCondominiumAdminSite(name='smartcondominium_admin')


# Registrar TODOS los modelos en el admin personalizado

# Usuarios
@admin.register(User, site=admin_site)
class CustomUserAdmin(CustomUserAdmin):
    pass

# Auditoría
@admin.register(RegistroAuditoria, site=admin_site)
class RegistroAuditoriaAdmin(RegistroAuditoriaAdmin):
    pass

@admin.register(SesionUsuario, site=admin_site)
class SesionUsuarioAdmin(SesionUsuarioAdmin):
    pass

@admin.register(EstadisticasAuditoria, site=admin_site)
class EstadisticasAuditoriaAdmin(EstadisticasAuditoriaAdmin):
    pass

# Comunicaciones
@admin.register(Aviso, site=admin_site)
class CommunicationsAvisoAdmin(CommunicationsAvisoAdmin):
    pass

@admin.register(LecturaAviso, site=admin_site)
class LecturaAvisoAdmin(LecturaAvisoAdmin):
    pass

@admin.register(ComentarioAviso, site=admin_site)
class ComentarioAvisoAdmin(ComentarioAvisoAdmin):
    pass

# Condominio
@admin.register(Rol, site=admin_site)
class RolAdmin(RolAdmin):
    pass

@admin.register(Usuario, site=admin_site)
class UsuarioAdmin(UsuarioAdmin):
    pass

@admin.register(AreaComun, site=admin_site)
class AreaComunAdmin(AreaComunAdmin):
    pass

@admin.register(Zona, site=admin_site)
class ZonaAdmin(ZonaAdmin):
    pass

@admin.register(Camara, site=admin_site)
class CamaraAdmin(CamaraAdmin):
    pass

@admin.register(TipoEvento, site=admin_site)
class TipoEventoAdmin(TipoEventoAdmin):
    pass

@admin.register(VehiculoAutorizado, site=admin_site)
class VehiculoAutorizadoAdmin(VehiculoAutorizadoAdmin):
    pass

@admin.register(UnidadHabitacional, site=admin_site)
class UnidadHabitacionalAdmin(UnidadHabitacionalAdmin):
    pass

@admin.register(Reserva, site=admin_site)
class ReservaAdmin(ReservaAdmin):
    pass

@admin.register(Cuota, site=admin_site)
class CuotaAdmin(CuotaAdmin):
    pass

@admin.register(Pago, site=admin_site)
class PagoAdmin(PagoAdmin):
    pass

@admin.register(AvisoCondominio, site=admin_site)
class CondominioAvisoAdmin(CondominioAvisoAdmin):
    pass

@admin.register(EventoSeguridad, site=admin_site)
class EventoSeguridadAdmin(EventoSeguridadAdmin):
    pass

@admin.register(Mantenimiento, site=admin_site)
class MantenimientoAdmin(MantenimientoAdmin):
    pass

@admin.register(Reporte, site=admin_site)
class ReporteAdmin(ReporteAdmin):
    pass

@admin.register(Bitacora, site=admin_site)
class BitacoraAdmin(BitacoraAdmin):
    pass

# Finanzas
@admin.register(ConceptoFinanciero, site=admin_site)
class ConceptoFinancieroAdmin(ConceptoFinancieroAdmin):
    pass

@admin.register(CargoFinanciero, site=admin_site)
class CargoFinancieroAdmin(CargoFinancieroAdmin):
    pass

# Gestión de Mantenimiento
@admin.register(SolicitudMantenimiento, site=admin_site)
class SolicitudMantenimientoAdmin(SolicitudMantenimientoAdmin):
    pass

@admin.register(TareaMantenimiento, site=admin_site)
class TareaMantenimientoAdmin(TareaMantenimientoAdmin):
    pass

# Reportes y Analíticas
@admin.register(ReporteFinanciero, site=admin_site)
class ReporteFinancieroAdmin(ReporteFinancieroAdmin):
    pass

@admin.register(ReporteSeguridad, site=admin_site)
class ReporteSeguridadAdmin(ReporteSeguridadAdmin):
    pass

@admin.register(ReporteUsoAreas, site=admin_site)
class ReporteUsoAreasAdmin(ReporteUsoAreasAdmin):
    pass

@admin.register(RostroRegistrado, site=admin_site)
class RostroRegistradoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'nombre_identificador', 'fecha_registro', 'activo', 'confianza_minima']
    list_filter = ['activo', 'fecha_registro']
    search_fields = ['usuario__username', 'nombre_identificador']
    readonly_fields = ['id', 'fecha_registro']

@admin.register(VehiculoRegistrado, site=admin_site)
class VehiculoRegistradoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'placa', 'marca', 'modelo', 'color', 'activo', 'fecha_registro']
    list_filter = ['activo', 'fecha_registro', 'color']
    search_fields = ['usuario__username', 'placa', 'marca', 'modelo']
    readonly_fields = ['id', 'fecha_registro']

@admin.register(Acceso, site=admin_site)
class AccesoAdmin(admin.ModelAdmin):
    list_display = ['usuario', 'tipo_acceso', 'estado', 'fecha_hora', 'ubicacion', 'confianza_ia']
    list_filter = ['tipo_acceso', 'estado', 'fecha_hora']
    search_fields = ['usuario__username', 'ubicacion']
    readonly_fields = ['id', 'fecha_hora']
    date_hierarchy = 'fecha_hora'