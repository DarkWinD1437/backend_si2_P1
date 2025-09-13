from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey

User = get_user_model()


class TipoActividad(models.TextChoices):
    """Tipos de actividad que se pueden registrar"""
    LOGIN = 'login', 'Inicio de sesión'
    LOGOUT = 'logout', 'Cierre de sesión'
    CREAR = 'crear', 'Crear registro'
    ACTUALIZAR = 'actualizar', 'Actualizar registro'
    ELIMINAR = 'eliminar', 'Eliminar registro'
    VER = 'ver', 'Ver registro'
    PAGO = 'pago', 'Procesar pago'
    ASIGNAR_ROL = 'asignar_rol', 'Asignar rol'
    CAMBIAR_PASSWORD = 'cambiar_password', 'Cambiar contraseña'
    ACCESO_DENEGADO = 'acceso_denegado', 'Acceso denegado'
    ERROR_SISTEMA = 'error_sistema', 'Error del sistema'
    EXPORTAR = 'exportar', 'Exportar datos'
    IMPORTAR = 'importar', 'Importar datos'
    CONFIGURAR = 'configurar', 'Configurar sistema'


class NivelImportancia(models.TextChoices):
    """Nivel de importancia de la actividad"""
    BAJO = 'bajo', 'Bajo'
    MEDIO = 'medio', 'Medio'
    ALTO = 'alto', 'Alto'
    CRITICO = 'critico', 'Crítico'


class RegistroAuditoria(models.Model):
    """
    Modelo principal para registrar todas las actividades del sistema
    """
    # Información básica del evento
    usuario = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='actividades_auditoria',
        verbose_name='Usuario'
    )
    
    tipo_actividad = models.CharField(
        max_length=20,
        choices=TipoActividad.choices,
        verbose_name='Tipo de Actividad'
    )
    
    descripcion = models.TextField(
        verbose_name='Descripción',
        help_text='Descripción detallada de la actividad'
    )
    
    nivel_importancia = models.CharField(
        max_length=10,
        choices=NivelImportancia.choices,
        default=NivelImportancia.MEDIO,
        verbose_name='Nivel de Importancia'
    )
    
    # Información del objeto afectado (opcional)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Tipo de Objeto'
    )
    object_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='ID del Objeto'
    )
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Información técnica
    timestamp = models.DateTimeField(
        default=timezone.now,
        verbose_name='Fecha y Hora'
    )
    
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name='Dirección IP'
    )
    
    user_agent = models.TextField(
        null=True,
        blank=True,
        verbose_name='User Agent'
    )
    
    # Datos adicionales en formato JSON
    datos_adicionales = models.JSONField(
        null=True,
        blank=True,
        verbose_name='Datos Adicionales',
        help_text='Información adicional en formato JSON'
    )
    
    # Información de cambios (para actualizaciones)
    datos_anteriores = models.JSONField(
        null=True,
        blank=True,
        verbose_name='Datos Anteriores',
        help_text='Estado anterior del objeto (para cambios)'
    )
    
    datos_nuevos = models.JSONField(
        null=True,
        blank=True,
        verbose_name='Datos Nuevos',
        help_text='Nuevo estado del objeto (para cambios)'
    )
    
    # Estado y control
    es_exitoso = models.BooleanField(
        default=True,
        verbose_name='Operación Exitosa'
    )
    
    mensaje_error = models.TextField(
        null=True,
        blank=True,
        verbose_name='Mensaje de Error'
    )
    
    class Meta:
        verbose_name = 'Registro de Auditoría'
        verbose_name_plural = 'Registros de Auditoría'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['usuario', '-timestamp']),
            models.Index(fields=['tipo_actividad', '-timestamp']),
            models.Index(fields=['nivel_importancia', '-timestamp']),
            models.Index(fields=['-timestamp']),
        ]
    
    def __str__(self):
        usuario_str = self.usuario.username if self.usuario else 'Sistema'
        return f"{self.get_tipo_actividad_display()} por {usuario_str} - {self.timestamp.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def nombre_usuario(self):
        """Retorna el nombre del usuario o 'Sistema' si es None"""
        return self.usuario.username if self.usuario else 'Sistema'
    
    @property
    def nombre_completo_usuario(self):
        """Retorna el nombre completo del usuario"""
        if self.usuario:
            return self.usuario.get_full_name() or self.usuario.username
        return 'Sistema'
    
    @property
    def objeto_afectado_str(self):
        """Retorna una representación string del objeto afectado"""
        if self.content_object:
            return str(self.content_object)
        elif self.content_type:
            return f"{self.content_type.model} (ID: {self.object_id})"
        return 'N/A'
    
    def get_nivel_color(self):
        """Retorna un color asociado al nivel de importancia"""
        colors = {
            NivelImportancia.BAJO: '#28a745',      # Verde
            NivelImportancia.MEDIO: '#ffc107',     # Amarillo
            NivelImportancia.ALTO: '#fd7e14',      # Naranja
            NivelImportancia.CRITICO: '#dc3545',   # Rojo
        }
        return colors.get(self.nivel_importancia, '#6c757d')


class SesionUsuario(models.Model):
    """
    Modelo para rastrear sesiones activas de usuarios
    """
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='sesiones_auditoria',
        verbose_name='Usuario'
    )
    
    token_session = models.CharField(
        max_length=255,
        unique=True,
        verbose_name='Token de Sesión'
    )
    
    ip_address = models.GenericIPAddressField(
        verbose_name='Dirección IP'
    )
    
    user_agent = models.TextField(
        verbose_name='User Agent'
    )
    
    fecha_inicio = models.DateTimeField(
        default=timezone.now,
        verbose_name='Fecha de Inicio'
    )
    
    fecha_ultimo_acceso = models.DateTimeField(
        auto_now=True,
        verbose_name='Último Acceso'
    )
    
    esta_activa = models.BooleanField(
        default=True,
        verbose_name='Sesión Activa'
    )
    
    fecha_cierre = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de Cierre'
    )
    
    class Meta:
        verbose_name = 'Sesión de Usuario'
        verbose_name_plural = 'Sesiones de Usuario'
        ordering = ['-fecha_inicio']
    
    def __str__(self):
        estado = 'Activa' if self.esta_activa else 'Cerrada'
        return f"Sesión de {self.usuario.username} - {estado}"
    
    @property
    def duracion_sesion(self):
        """Calcula la duración de la sesión"""
        if self.fecha_cierre:
            return self.fecha_cierre - self.fecha_inicio
        return timezone.now() - self.fecha_inicio
    
    def cerrar_sesion(self):
        """Marca la sesión como cerrada"""
        self.esta_activa = False
        self.fecha_cierre = timezone.now()
        self.save()


class EstadisticasAuditoria(models.Model):
    """
    Modelo para almacenar estadísticas precalculadas de auditoría
    """
    fecha = models.DateField(
        verbose_name='Fecha'
    )
    
    total_actividades = models.PositiveIntegerField(
        default=0,
        verbose_name='Total de Actividades'
    )
    
    total_logins = models.PositiveIntegerField(
        default=0,
        verbose_name='Total de Logins'
    )
    
    total_usuarios_activos = models.PositiveIntegerField(
        default=0,
        verbose_name='Usuarios Activos'
    )
    
    actividades_criticas = models.PositiveIntegerField(
        default=0,
        verbose_name='Actividades Críticas'
    )
    
    errores_sistema = models.PositiveIntegerField(
        default=0,
        verbose_name='Errores del Sistema'
    )
    
    datos_estadisticas = models.JSONField(
        null=True,
        blank=True,
        verbose_name='Datos Estadísticos Detallados'
    )
    
    class Meta:
        verbose_name = 'Estadística de Auditoría'
        verbose_name_plural = 'Estadísticas de Auditoría'
        unique_together = ['fecha']
        ordering = ['-fecha']
    
    def __str__(self):
        return f"Estadísticas del {self.fecha} - {self.total_actividades} actividades"