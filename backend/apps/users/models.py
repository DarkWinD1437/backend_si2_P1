from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    ROLE_CHOICES = (
        ('admin', 'Administrador'),
        ('resident', 'Residente'),
        ('security', 'Seguridad'),
    )
    
    DOCUMENT_TYPE_CHOICES = (
        ('CI', 'Cédula de Identidad'),
        ('PASSPORT', 'Pasaporte'),
        ('RUC', 'RUC'),
        ('NIT', 'NIT'),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='resident')
    phone = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPE_CHOICES, default='CI', blank=True)
    document_number = models.CharField(max_length=50, blank=True)
    unit_number = models.CharField(max_length=20, blank=True, help_text="Número de unidad (solo para residentes)")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    # ESTAS LÍNEAS SON PARA EVITAR CONFLICTOS
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='custom_user_set',  # ← related_name único
        related_query_name='user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='custom_user_set',  # ← related_name único
        related_query_name='user',
    )

    def __str__(self):
        return f"{self.username} - {self.get_role_display()}"
