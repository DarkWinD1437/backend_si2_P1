from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import RegexValidator
import uuid

User = get_user_model()

class RostroRegistrado(models.Model):
    """Modelo para rostros registrados para reconocimiento facial"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='rostros_registrados')
    nombre_identificador = models.CharField(max_length=100, help_text="Nombre descriptivo del rostro")
    imagen_rostro = models.ImageField(upload_to='rostros/', help_text="Imagen del rostro para reconocimiento")
    embedding_ia = models.JSONField(help_text="Vector de características extraído por IA")
    fecha_registro = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)
    confianza_minima = models.FloatField(default=0.95, help_text="Confianza mínima para reconocimiento (0-1)")

    class Meta:
        verbose_name = "Rostro Registrado"
        verbose_name_plural = "Rostros Registrados"
        ordering = ['-fecha_registro']

    def __str__(self):
        return f"Rostro de {self.usuario.get_full_name()} - {self.nombre_identificador}"

class VehiculoRegistrado(models.Model):
    """Modelo para vehículos registrados"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='vehiculos_registrados')

    # Validadores para placa
    placa_validator = RegexValidator(
        regex=r'^\d{3,4}[A-Z]{3}$',
        message='Formato de placa inválido. Use formato: 123ABC o 1234ABC'
    )

    placa = models.CharField(
        max_length=7,
        unique=True,
        validators=[placa_validator],
        help_text="Placa del vehículo (formato: 123ABC o 1234ABC)"
    )
    marca = models.CharField(max_length=50, help_text="Marca del vehículo")
    modelo = models.CharField(max_length=50, help_text="Modelo del vehículo")
    color = models.CharField(max_length=30, help_text="Color del vehículo")
    descripcion = models.TextField(blank=True, help_text="Descripción adicional")

    fecha_registro = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = "Vehículo Registrado"
        verbose_name_plural = "Vehículos Registrados"
        ordering = ['-fecha_registro']

    def __str__(self):
        return f"{self.placa} - {self.marca} {self.modelo}"

class Acceso(models.Model):
    """Modelo para historial de accesos al condominio"""

    TIPO_ACCESO_CHOICES = [
        ('facial', 'Reconocimiento Facial'),
        ('placa', 'Lectura de Placa'),
        ('manual', 'Acceso Manual'),
        ('codigo', 'Código de Acceso'),
    ]

    ESTADO_ACCESO_CHOICES = [
        ('permitido', 'Acceso Permitido'),
        ('denegado', 'Acceso Denegado'),
        ('pendiente', 'Pendiente de Verificación'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    usuario = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='accesos'
    )

    tipo_acceso = models.CharField(
        max_length=20,
        choices=TIPO_ACCESO_CHOICES,
        default='manual'
    )
    estado = models.CharField(
        max_length=20,
        choices=ESTADO_ACCESO_CHOICES,
        default='pendiente'
    )

    # Información del acceso
    fecha_hora = models.DateTimeField(auto_now_add=True)
    ubicacion = models.CharField(max_length=100, help_text="Punto de acceso (ej: Puerta Principal)")

    # Información específica por tipo
    rostro_detectado = models.ForeignKey(
        RostroRegistrado,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='accesos'
    )
    vehiculo_detectado = models.ForeignKey(
        VehiculoRegistrado,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='accesos'
    )

    # Datos de IA
    confianza_ia = models.FloatField(null=True, blank=True, help_text="Confianza de la IA (0-1)")
    datos_ia = models.JSONField(null=True, blank=True, help_text="Datos adicionales de la IA")

    # Información adicional
    observaciones = models.TextField(blank=True)
    autorizado_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='accesos_autorizados'
    )

    class Meta:
        verbose_name = "Acceso"
        verbose_name_plural = "Historial de Accesos"
        ordering = ['-fecha_hora']
        indexes = [
            models.Index(fields=['fecha_hora']),
            models.Index(fields=['usuario', 'fecha_hora']),
            models.Index(fields=['tipo_acceso', 'estado']),
        ]

    def __str__(self):
        usuario_str = self.usuario.get_full_name() if self.usuario else "Desconocido"
        return f"{self.tipo_acceso} - {usuario_str} - {self.fecha_hora.strftime('%d/%m/%Y %H:%M')}"