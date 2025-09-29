from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Dispositivo(models.Model):
    """Modelo para almacenar tokens de dispositivos para notificaciones push"""
    TIPO_DISPOSITIVO_CHOICES = [
        ('web', 'Web Browser'),
        ('android', 'Android'),
        ('ios', 'iOS'),
        ('flutter_web', 'Flutter Web'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dispositivos')
    token_push = models.CharField(max_length=500, unique=True, help_text="Token FCM o web push")
    tipo_dispositivo = models.CharField(max_length=20, choices=TIPO_DISPOSITIVO_CHOICES)
    nombre_dispositivo = models.CharField(max_length=100, blank=True, help_text="Nombre descriptivo del dispositivo")
    activo = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    ultima_actividad = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'modulo_notificaciones'
        verbose_name = "Dispositivo"
        verbose_name_plural = "Dispositivos"
        ordering = ['-ultima_actividad']

    def __str__(self):
        return f"{self.usuario.get_full_name()} - {self.tipo_dispositivo} - {self.nombre_dispositivo or 'Sin nombre'}"


class PreferenciasNotificacion(models.Model):
    """Modelo para las preferencias de notificación de cada usuario"""

    TIPO_NOTIFICACION_CHOICES = [
        ('acceso_permitido', 'Acceso Permitido'),
        ('acceso_denegado', 'Acceso Denegado'),
        ('nuevo_mensaje', 'Nuevo Mensaje'),
        ('pago_realizado', 'Pago Realizado'),
        ('pago_pendiente', 'Pago Pendiente'),
        ('mantenimiento', 'Aviso de Mantenimiento'),
        ('emergencia', 'Emergencia'),
        ('recordatorio', 'Recordatorio'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='preferencias_notificacion')
    tipo_notificacion = models.CharField(max_length=50, choices=TIPO_NOTIFICACION_CHOICES)
    push_enabled = models.BooleanField(default=True, help_text="Enviar notificación push")
    email_enabled = models.BooleanField(default=False, help_text="Enviar notificación por email")
    sms_enabled = models.BooleanField(default=False, help_text="Enviar notificación por SMS")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'modulo_notificaciones'
        verbose_name = "Preferencia de Notificación"
        verbose_name_plural = "Preferencias de Notificación"
        unique_together = ['usuario', 'tipo_notificacion']
        ordering = ['usuario', 'tipo_notificacion']

    def __str__(self):
        return f"{self.usuario.get_full_name()} - {self.get_tipo_notificacion_display()}"


class Notificacion(models.Model):
    """Modelo para almacenar todas las notificaciones enviadas"""

    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('enviada', 'Enviada'),
        ('fallida', 'Fallida'),
        ('leida', 'Leída'),
    ]

    TIPO_NOTIFICACION_CHOICES = [
        ('acceso_permitido', 'Acceso Permitido'),
        ('acceso_denegado', 'Acceso Denegado'),
        ('nuevo_mensaje', 'Nuevo Mensaje'),
        ('pago_realizado', 'Pago Realizado'),
        ('pago_pendiente', 'Pago Pendiente'),
        ('mantenimiento', 'Aviso de Mantenimiento'),
        ('emergencia', 'Emergencia'),
        ('recordatorio', 'Recordatorio'),
        ('sistema', 'Sistema'),
    ]

    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()
    tipo = models.CharField(max_length=50, choices=TIPO_NOTIFICACION_CHOICES, default='sistema')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificaciones')
    dispositivo = models.ForeignKey(Dispositivo, on_delete=models.SET_NULL, null=True, blank=True, related_name='notificaciones')

    # Estado y envío
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_envio = models.DateTimeField(null=True, blank=True)
    fecha_lectura = models.DateTimeField(null=True, blank=True)

    # Datos adicionales
    datos_extra = models.JSONField(null=True, blank=True, help_text="Datos adicionales en formato JSON")
    prioridad = models.IntegerField(default=1, help_text="Prioridad (1-5, siendo 5 la más alta)")

    # Información de envío
    push_enviado = models.BooleanField(default=False)
    email_enviado = models.BooleanField(default=False)
    sms_enviado = models.BooleanField(default=False)

    # Errores
    error_mensaje = models.TextField(blank=True, null=True)

    class Meta:
        app_label = 'modulo_notificaciones'
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"
        ordering = ['-fecha_creacion']
        indexes = [
            models.Index(fields=['usuario', '-fecha_creacion']),
            models.Index(fields=['estado', 'tipo']),
            models.Index(fields=['fecha_creacion']),
        ]

    def __str__(self):
        return f"{self.titulo} - {self.usuario.get_full_name()} ({self.estado})"

    def marcar_como_leida(self):
        """Marcar la notificación como leída"""
        if not self.fecha_lectura:
            self.fecha_lectura = timezone.now()
            self.estado = 'leida'
            self.save()

    def marcar_como_enviada(self):
        """Marcar la notificación como enviada"""
        if not self.fecha_envio:
            self.fecha_envio = timezone.now()
            self.estado = 'enviada'
            self.save()