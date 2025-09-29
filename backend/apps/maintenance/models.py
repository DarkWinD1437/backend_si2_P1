from django.db import models
from django.conf import settings
from django.utils import timezone


class SolicitudMantenimiento(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('asignada', 'Asignada'),
        ('en_progreso', 'En Progreso'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
    ]

    PRIORIDAD_CHOICES = [
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    ]

    solicitante = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='solicitudes_mantenimiento')
    descripcion = models.TextField(verbose_name='Descripción del problema')
    ubicacion = models.CharField(max_length=255, verbose_name='Ubicación')
    prioridad = models.CharField(max_length=10, choices=PRIORIDAD_CHOICES, default='media')
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='pendiente')
    fecha_solicitud = models.DateTimeField(default=timezone.now)
    fecha_actualizacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Solicitud de Mantenimiento'
        verbose_name_plural = 'Solicitudes de Mantenimiento'
        ordering = ['-fecha_solicitud']

    def __str__(self):
        return f"Solicitud #{self.id} - {self.ubicacion}"


class TareaMantenimiento(models.Model):
    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('asignada', 'Asignada'),
        ('en_progreso', 'En Progreso'),
        ('completada', 'Completada'),
        ('cancelada', 'Cancelada'),
    ]

    solicitud = models.OneToOneField(SolicitudMantenimiento, on_delete=models.CASCADE, related_name='tarea')
    asignado_a = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='tareas_asignadas')
    descripcion_tarea = models.TextField(verbose_name='Descripción de la tarea')
    estado = models.CharField(max_length=15, choices=ESTADO_CHOICES, default='asignada')
    fecha_asignacion = models.DateTimeField(default=timezone.now)
    fecha_completado = models.DateTimeField(null=True, blank=True)
    notas = models.TextField(blank=True, verbose_name='Notas adicionales')

    class Meta:
        verbose_name = 'Tarea de Mantenimiento'
        verbose_name_plural = 'Tareas de Mantenimiento'
        ordering = ['-fecha_asignacion']

    def __str__(self):
        return f"Tarea #{self.id} - Solicitud #{self.solicitud.id}"

    def save(self, *args, **kwargs):
        if self.estado == 'completada' and not self.fecha_completado:
            self.fecha_completado = timezone.now()
        super().save(*args, **kwargs)