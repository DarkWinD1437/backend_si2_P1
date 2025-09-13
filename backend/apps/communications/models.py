from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

class Aviso(models.Model):
    """
    Modelo para avisos generales del condominio
    Permite comunicación flexible entre diferentes roles
    """
    
    PRIORIDAD_CHOICES = (
        ('baja', 'Baja'),
        ('media', 'Media'),
        ('alta', 'Alta'),
        ('urgente', 'Urgente'),
    )
    
    TIPO_DESTINATARIO_CHOICES = (
        ('todos', 'Todos los usuarios'),
        ('residentes', 'Solo residentes'),
        ('administradores', 'Solo administradores'),
        ('seguridad', 'Solo personal de seguridad'),
        ('admin_seguridad', 'Administradores y seguridad'),
        ('residentes_seguridad', 'Residentes y seguridad'),
        ('personalizado', 'Selección personalizada'),
    )
    
    ESTADO_CHOICES = (
        ('borrador', 'Borrador'),
        ('publicado', 'Publicado'),
        ('archivado', 'Archivado'),
        ('vencido', 'Vencido'),
    )

    # Información básica del aviso
    titulo = models.CharField(max_length=200, help_text="Título del aviso")
    contenido = models.TextField(help_text="Contenido detallado del aviso")
    resumen = models.CharField(max_length=500, blank=True, help_text="Resumen corto para notificaciones")
    
    # Autor y control
    autor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='avisos_creados')
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='borrador')
    prioridad = models.CharField(max_length=20, choices=PRIORIDAD_CHOICES, default='media')
    
    # Sistema de destinatarios
    tipo_destinatario = models.CharField(max_length=30, choices=TIPO_DESTINATARIO_CHOICES, default='todos')
    roles_destinatarios = models.JSONField(
        default=list,
        blank=True,
        help_text="Lista de roles específicos cuando tipo_destinatario es 'personalizado'"
    )
    usuarios_destinatarios = models.ManyToManyField(
        User,
        blank=True,
        related_name='avisos_recibidos',
        help_text="Usuarios específicos adicionales"
    )
    
    # Control de fechas
    fecha_publicacion = models.DateTimeField(null=True, blank=True)
    fecha_vencimiento = models.DateTimeField(null=True, blank=True, help_text="Opcional: fecha de vencimiento del aviso")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
    
    # Campos adicionales
    requiere_confirmacion = models.BooleanField(
        default=False,
        help_text="Si los destinatarios deben confirmar lectura"
    )
    adjunto = models.FileField(
        upload_to='avisos/adjuntos/',
        null=True,
        blank=True,
        help_text="Archivo adjunto opcional"
    )
    
    # Metadatos
    visualizaciones = models.PositiveIntegerField(default=0)
    es_fijado = models.BooleanField(default=False, help_text="Aviso fijado al inicio de la lista")
    
    class Meta:
        ordering = ['-es_fijado', '-fecha_publicacion', '-fecha_creacion']
        verbose_name = 'Aviso'
        verbose_name_plural = 'Avisos'
        
    def __str__(self):
        return f"{self.titulo} ({self.get_prioridad_display()})"
    
    @property
    def esta_vencido(self):
        """Verificar si el aviso está vencido"""
        if self.fecha_vencimiento:
            return timezone.now() > self.fecha_vencimiento
        return False
    
    @property
    def esta_publicado(self):
        """Verificar si el aviso está publicado y vigente"""
        return (
            self.estado == 'publicado' and 
            self.fecha_publicacion and 
            self.fecha_publicacion <= timezone.now() and
            not self.esta_vencido
        )
    
    def get_destinatarios_queryset(self):
        """
        Retorna el queryset de usuarios que deben recibir este aviso
        según el tipo de destinatario configurado
        """
        if self.tipo_destinatario == 'todos':
            return User.objects.all()
        elif self.tipo_destinatario == 'residentes':
            return User.objects.filter(role='resident')
        elif self.tipo_destinatario == 'administradores':
            return User.objects.filter(role='admin')
        elif self.tipo_destinatario == 'seguridad':
            return User.objects.filter(role='security')
        elif self.tipo_destinatario == 'admin_seguridad':
            return User.objects.filter(role__in=['admin', 'security'])
        elif self.tipo_destinatario == 'residentes_seguridad':
            return User.objects.filter(role__in=['resident', 'security'])
        elif self.tipo_destinatario == 'personalizado' and self.roles_destinatarios:
            return User.objects.filter(role__in=self.roles_destinatarios)
        else:
            return User.objects.none()
    
    def incrementar_visualizaciones(self):
        """Incrementar contador de visualizaciones"""
        self.visualizaciones += 1
        self.save(update_fields=['visualizaciones'])
    
    def publicar(self):
        """Publicar el aviso"""
        self.estado = 'publicado'
        self.fecha_publicacion = timezone.now()
        self.save()
    
    def archivar(self):
        """Archivar el aviso"""
        self.estado = 'archivado'
        self.save()


class LecturaAviso(models.Model):
    """
    Modelo para trackear qué usuarios han leído cada aviso
    Útil para avisos que requieren confirmación de lectura
    """
    aviso = models.ForeignKey(Aviso, on_delete=models.CASCADE, related_name='lecturas')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    fecha_lectura = models.DateTimeField(auto_now_add=True)
    confirmado = models.BooleanField(default=False)
    
    class Meta:
        unique_together = ('aviso', 'usuario')
        ordering = ['-fecha_lectura']
        verbose_name = 'Lectura de Aviso'
        verbose_name_plural = 'Lecturas de Avisos'
    
    def __str__(self):
        confirmacion = "✓" if self.confirmado else "○"
        return f"{self.usuario.username} - {self.aviso.titulo} {confirmacion}"


class ComentarioAviso(models.Model):
    """
    Modelo para comentarios en avisos
    Permite retroalimentación y preguntas
    """
    aviso = models.ForeignKey(Aviso, on_delete=models.CASCADE, related_name='comentarios')
    autor = models.ForeignKey(User, on_delete=models.CASCADE)
    contenido = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    es_respuesta = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='respuestas'
    )
    
    class Meta:
        ordering = ['fecha_creacion']
        verbose_name = 'Comentario de Aviso'
        verbose_name_plural = 'Comentarios de Avisos'
    
    def __str__(self):
        tipo = "Respuesta" if self.es_respuesta else "Comentario"
        return f"{tipo} de {self.autor.username} en '{self.aviso.titulo}'"