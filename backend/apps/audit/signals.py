from django.db.models.signals import post_save, pre_delete, post_delete
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth import get_user_model
from .models import RegistroAuditoria, SesionUsuario, TipoActividad, NivelImportancia
from .utils import AuditoriaLogger

User = get_user_model()


@receiver(user_logged_in)
def registrar_login_exitoso(sender, request, user, **kwargs):
    """Registra cuando un usuario hace login exitoso"""
    ip_address = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    
    # Registrar en auditoría
    RegistroAuditoria.objects.create(
        usuario=user,
        tipo_actividad=TipoActividad.LOGIN,
        descripcion=f'Inicio de sesión exitoso para {user.username}',
        nivel_importancia=NivelImportancia.MEDIO,
        ip_address=ip_address,
        user_agent=user_agent,
        es_exitoso=True,
        datos_adicionales={
            'rol': getattr(user, 'role', 'no_definido'),
            'es_superuser': user.is_superuser,
            'es_staff': user.is_staff
        }
    )
    
    # Crear o actualizar sesión
    if hasattr(request, 'auth') and hasattr(request.auth, 'key'):
        token = request.auth.key
        SesionUsuario.objects.update_or_create(
            token_session=token,
            defaults={
                'usuario': user,
                'ip_address': ip_address,
                'user_agent': user_agent,
                'esta_activa': True,
                'fecha_cierre': None
            }
        )


@receiver(user_logged_out)
def registrar_logout(sender, request, user, **kwargs):
    """Registra cuando un usuario hace logout"""
    if user:
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Registrar en auditoría
        RegistroAuditoria.objects.create(
            usuario=user,
            tipo_actividad=TipoActividad.LOGOUT,
            descripcion=f'Cierre de sesión para {user.username}',
            nivel_importancia=NivelImportancia.BAJO,
            ip_address=ip_address,
            user_agent=user_agent,
            es_exitoso=True
        )
        
        # Cerrar sesión activa si existe
        if hasattr(request, 'auth') and hasattr(request.auth, 'key'):
            try:
                sesion = SesionUsuario.objects.get(
                    token_session=request.auth.key,
                    esta_activa=True
                )
                sesion.cerrar_sesion()
            except SesionUsuario.DoesNotExist:
                pass


@receiver(user_login_failed)
def registrar_login_fallido(sender, credentials, request, **kwargs):
    """Registra cuando falla un intento de login"""
    ip_address = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '') if request else ''
    username = credentials.get('username', 'desconocido')
    
    RegistroAuditoria.objects.create(
        usuario=None,
        tipo_actividad=TipoActividad.LOGIN,
        descripcion=f'Intento de inicio de sesión fallido para usuario: {username}',
        nivel_importancia=NivelImportancia.ALTO,
        ip_address=ip_address,
        user_agent=user_agent,
        es_exitoso=False,
        mensaje_error='Credenciales inválidas',
        datos_adicionales={
            'username_intentado': username,
            'metodo': request.method if request else 'UNKNOWN'
        }
    )


# Señales para modelos específicos importantes
@receiver(post_save, sender=User)
def registrar_cambios_usuario(sender, instance, created, **kwargs):
    """Registra creación y modificación de usuarios"""
    if created:
        RegistroAuditoria.objects.create(
            usuario=instance if not created else None,
            tipo_actividad=TipoActividad.CREAR,
            descripcion=f'Usuario creado: {instance.username}',
            nivel_importancia=NivelImportancia.ALTO,
            content_type=ContentType.objects.get_for_model(User),
            object_id=instance.id,
            es_exitoso=True,
            datos_adicionales={
                'username': instance.username,
                'email': instance.email,
                'rol': getattr(instance, 'role', 'no_definido'),
                'es_activo': instance.is_active
            }
        )
    else:
        # Para actualizaciones, necesitaríamos comparar con el estado anterior
        # Por simplicidad, solo registramos que hubo una actualización
        RegistroAuditoria.objects.create(
            usuario=instance,
            tipo_actividad=TipoActividad.ACTUALIZAR,
            descripcion=f'Usuario actualizado: {instance.username}',
            nivel_importancia=NivelImportancia.MEDIO,
            content_type=ContentType.objects.get_for_model(User),
            object_id=instance.id,
            es_exitoso=True
        )


@receiver(pre_delete, sender=User)
def registrar_eliminacion_usuario(sender, instance, **kwargs):
    """Registra eliminación de usuarios"""
    # Obtener el usuario que está realizando la eliminación desde el contexto de la petición
    # En un escenario real, esto se haría a través del request
    RegistroAuditoria.objects.create(
        usuario=None,  # Se puede mejorar para obtener el usuario actual
        tipo_actividad=TipoActividad.ELIMINAR,
        descripcion=f'Usuario eliminado: {instance.username}',
        nivel_importancia=NivelImportancia.CRITICO,
        content_type=ContentType.objects.get_for_model(User),
        object_id=instance.id,
        es_exitoso=True,
        datos_adicionales={
            'username_eliminado': instance.username,
            'email': instance.email,
            'rol': getattr(instance, 'role', 'no_definido')
        }
    )


def get_client_ip(request):
    """Obtiene la IP del cliente desde el request"""
    if request is None:
        return '127.0.0.1'
    
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip or '127.0.0.1'


# Registrar auditoría para modelos financieros
def registrar_auditoria_modelo(sender, instance, created, **kwargs):
    """Función genérica para registrar auditoría de modelos"""
    try:
        from backend.apps.finances.models import ConceptoFinanciero, CargoFinanciero
        
        tipo_actividad = TipoActividad.CREAR if created else TipoActividad.ACTUALIZAR
        descripcion = f'{"Creado" if created else "Actualizado"} {sender._meta.verbose_name}: {str(instance)}'
        
        # Determinar nivel de importancia según el modelo
        if sender == CargoFinanciero:
            nivel = NivelImportancia.ALTO if created else NivelImportancia.MEDIO
        else:
            nivel = NivelImportancia.MEDIO
        
        RegistroAuditoria.objects.create(
            usuario=None,  # Se puede mejorar para obtener el usuario actual
            tipo_actividad=tipo_actividad,
            descripcion=descripcion,
            nivel_importancia=nivel,
            content_type=ContentType.objects.get_for_model(sender),
            object_id=instance.id,
            es_exitoso=True,
            datos_adicionales={
                'modelo': sender._meta.label,
                'operacion': 'creacion' if created else 'actualizacion'
            }
        )
    except ImportError:
        # El módulo de finanzas no existe aún
        pass


# Conectar las señales para modelos financieros
def conectar_signals_finanzas():
    """Conecta las señales para los modelos financieros"""
    try:
        from backend.apps.finances.models import ConceptoFinanciero, CargoFinanciero
        
        post_save.connect(registrar_auditoria_modelo, sender=ConceptoFinanciero)
        post_save.connect(registrar_auditoria_modelo, sender=CargoFinanciero)
        
    except ImportError:
        # El módulo de finanzas no existe aún, se conectará cuando esté disponible
        pass


# Intentar conectar las señales de finanzas
conectar_signals_finanzas()