from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from .models import RegistroAuditoria, TipoActividad, NivelImportancia

User = get_user_model()


class AuditoriaLogger:
    """
    Clase utilitaria para facilitar el registro de auditoría
    """
    
    @staticmethod
    def registrar_actividad(
        usuario=None,
        tipo_actividad=TipoActividad.VER,
        descripcion="",
        nivel_importancia=NivelImportancia.BAJO,
        objeto_afectado=None,
        ip_address=None,
        user_agent=None,
        es_exitoso=True,
        mensaje_error=None,
        datos_adicionales=None,
        datos_anteriores=None,
        datos_nuevos=None
    ):
        """
        Registra una actividad en el sistema de auditoría
        
        Args:
            usuario: Usuario que realiza la acción
            tipo_actividad: Tipo de actividad (ver TipoActividad)
            descripcion: Descripción de la actividad
            nivel_importancia: Nivel de importancia (ver NivelImportancia)
            objeto_afectado: Objeto del modelo afectado (opcional)
            ip_address: Dirección IP del usuario
            user_agent: User agent del navegador
            es_exitoso: Si la operación fue exitosa
            mensaje_error: Mensaje de error si aplica
            datos_adicionales: Datos adicionales en JSON
            datos_anteriores: Estado anterior del objeto
            datos_nuevos: Nuevo estado del objeto
        
        Returns:
            RegistroAuditoria: El registro creado
        """
        # Preparar datos del objeto afectado
        content_type = None
        object_id = None
        if objeto_afectado:
            content_type = ContentType.objects.get_for_model(objeto_afectado)
            object_id = objeto_afectado.pk
        
        # Crear el registro
        registro = RegistroAuditoria.objects.create(
            usuario=usuario,
            tipo_actividad=tipo_actividad,
            descripcion=descripcion,
            nivel_importancia=nivel_importancia,
            content_type=content_type,
            object_id=object_id,
            ip_address=ip_address,
            user_agent=user_agent,
            es_exitoso=es_exitoso,
            mensaje_error=mensaje_error,
            datos_adicionales=datos_adicionales,
            datos_anteriores=datos_anteriores,
            datos_nuevos=datos_nuevos
        )
        
        return registro
    
    @staticmethod
    def registrar_login(usuario, ip_address=None, user_agent=None, exitoso=True):
        """Registra un intento de login"""
        descripcion = f"Inicio de sesión {'exitoso' if exitoso else 'fallido'} para {usuario.username if usuario else 'usuario desconocido'}"
        nivel = NivelImportancia.MEDIO if exitoso else NivelImportancia.ALTO
        
        return AuditoriaLogger.registrar_actividad(
            usuario=usuario,
            tipo_actividad=TipoActividad.LOGIN,
            descripcion=descripcion,
            nivel_importancia=nivel,
            ip_address=ip_address,
            user_agent=user_agent,
            es_exitoso=exitoso
        )
    
    @staticmethod
    def registrar_logout(usuario, ip_address=None, user_agent=None):
        """Registra un logout"""
        return AuditoriaLogger.registrar_actividad(
            usuario=usuario,
            tipo_actividad=TipoActividad.LOGOUT,
            descripcion=f"Cierre de sesión para {usuario.username}",
            nivel_importancia=NivelImportancia.BAJO,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @staticmethod
    def registrar_creacion(usuario, objeto, descripcion_personalizada=None, datos_adicionales=None):
        """Registra la creación de un objeto"""
        descripcion = descripcion_personalizada or f"Creado {objeto._meta.verbose_name}: {str(objeto)}"
        
        return AuditoriaLogger.registrar_actividad(
            usuario=usuario,
            tipo_actividad=TipoActividad.CREAR,
            descripcion=descripcion,
            nivel_importancia=NivelImportancia.MEDIO,
            objeto_afectado=objeto,
            es_exitoso=True,
            datos_adicionales=datos_adicionales
        )
    
    @staticmethod
    def registrar_actualizacion(usuario, objeto, datos_anteriores=None, datos_nuevos=None, descripcion_personalizada=None):
        """Registra la actualización de un objeto"""
        descripcion = descripcion_personalizada or f"Actualizado {objeto._meta.verbose_name}: {str(objeto)}"
        
        return AuditoriaLogger.registrar_actividad(
            usuario=usuario,
            tipo_actividad=TipoActividad.ACTUALIZAR,
            descripcion=descripcion,
            nivel_importancia=NivelImportancia.MEDIO,
            objeto_afectado=objeto,
            es_exitoso=True,
            datos_anteriores=datos_anteriores,
            datos_nuevos=datos_nuevos
        )
    
    @staticmethod
    def registrar_eliminacion(usuario, objeto, descripcion_personalizada=None):
        """Registra la eliminación de un objeto"""
        descripcion = descripcion_personalizada or f"Eliminado {objeto._meta.verbose_name}: {str(objeto)}"
        
        return AuditoriaLogger.registrar_actividad(
            usuario=usuario,
            tipo_actividad=TipoActividad.ELIMINAR,
            descripcion=descripcion,
            nivel_importancia=NivelImportancia.ALTO,
            objeto_afectado=objeto,
            es_exitoso=True
        )
    
    @staticmethod
    def registrar_pago(usuario, cargo, referencia_pago=None, monto=None):
        """Registra un pago procesado"""
        descripcion = f"Pago procesado para cargo ID {cargo.id}"
        if referencia_pago:
            descripcion += f" - Referencia: {referencia_pago}"
        
        datos_adicionales = {
            'referencia_pago': referencia_pago,
            'monto': str(monto) if monto else str(cargo.monto),
            'concepto': cargo.concepto.nombre if cargo.concepto else 'N/A'
        }
        
        return AuditoriaLogger.registrar_actividad(
            usuario=usuario,
            tipo_actividad=TipoActividad.PAGO,
            descripcion=descripcion,
            nivel_importancia=NivelImportancia.ALTO,
            objeto_afectado=cargo,
            es_exitoso=True,
            datos_adicionales=datos_adicionales
        )
    
    @staticmethod
    def registrar_acceso_denegado(usuario, recurso, motivo=""):
        """Registra un acceso denegado"""
        descripcion = f"Acceso denegado a {recurso}"
        if motivo:
            descripcion += f" - Motivo: {motivo}"
        
        return AuditoriaLogger.registrar_actividad(
            usuario=usuario,
            tipo_actividad=TipoActividad.ACCESO_DENEGADO,
            descripcion=descripcion,
            nivel_importancia=NivelImportancia.ALTO,
            es_exitoso=False,
            datos_adicionales={'recurso': recurso, 'motivo': motivo}
        )
    
    @staticmethod
    def registrar_error_sistema(usuario, error, contexto=""):
        """Registra un error del sistema"""
        descripcion = f"Error del sistema: {str(error)}"
        if contexto:
            descripcion += f" - Contexto: {contexto}"
        
        return AuditoriaLogger.registrar_actividad(
            usuario=usuario,
            tipo_actividad=TipoActividad.ERROR_SISTEMA,
            descripcion=descripcion,
            nivel_importancia=NivelImportancia.CRITICO,
            es_exitoso=False,
            mensaje_error=str(error),
            datos_adicionales={'contexto': contexto}
        )


def get_client_ip_from_request(request):
    """
    Obtiene la IP del cliente desde el request
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent_from_request(request):
    """
    Obtiene el user agent desde el request
    """
    return request.META.get('HTTP_USER_AGENT', '')


class AuditMiddleware:
    """
    Middleware para capturar automáticamente información de auditoría
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Agregar información de auditoría al request
        request.audit_ip = get_client_ip_from_request(request)
        request.audit_user_agent = get_user_agent_from_request(request)
        
        response = self.get_response(request)
        
        return response