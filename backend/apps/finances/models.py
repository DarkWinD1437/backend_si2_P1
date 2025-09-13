"""
Modelos para el Módulo de Gestión Financiera
Módulo 2: Gestión Financiera Básica
T1: Configurar Cuotas y Multas
"""

from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal
from django.core.validators import MinValueValidator
from datetime import date

User = get_user_model()


class TipoConcepto(models.TextChoices):
    """Tipos de conceptos financieros"""
    CUOTA_MENSUAL = 'cuota_mensual', 'Cuota Mensual'
    CUOTA_EXTRAORDINARIA = 'cuota_extraordinaria', 'Cuota Extraordinaria'
    MULTA_RUIDO = 'multa_ruido', 'Multa por Ruido'
    MULTA_AREAS_COMUNES = 'multa_areas_comunes', 'Multa Áreas Comunes'
    MULTA_ESTACIONAMIENTO = 'multa_estacionamiento', 'Multa Estacionamiento'
    MULTA_MASCOTA = 'multa_mascota', 'Multa por Mascota'
    OTROS = 'otros', 'Otros'


class EstadoConcepto(models.TextChoices):
    """Estados de los conceptos financieros"""
    ACTIVO = 'activo', 'Activo'
    INACTIVO = 'inactivo', 'Inactivo'
    SUSPENDIDO = 'suspendido', 'Suspendido'


class ConceptoFinanciero(models.Model):
    """
    Modelo para definir conceptos financieros (cuotas y multas)
    Permite a los administradores configurar diferentes tipos de cobros
    """
    nombre = models.CharField(max_length=100, verbose_name="Nombre del Concepto")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    tipo = models.CharField(
        max_length=30,
        choices=TipoConcepto.choices,
        verbose_name="Tipo de Concepto"
    )
    monto = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Monto"
    )
    estado = models.CharField(
        max_length=15,
        choices=EstadoConcepto.choices,
        default=EstadoConcepto.ACTIVO,
        verbose_name="Estado"
    )
    fecha_vigencia_desde = models.DateField(
        default=date.today,
        verbose_name="Vigente desde"
    )
    fecha_vigencia_hasta = models.DateField(
        null=True,
        blank=True,
        verbose_name="Vigente hasta"
    )
    
    # Configuraciones específicas
    es_recurrente = models.BooleanField(
        default=False,
        help_text="Si se aplica automáticamente cada mes"
    )
    aplica_a_todos = models.BooleanField(
        default=True,
        help_text="Si aplica a todos los residentes o solo a casos específicos"
    )
    
    # Metadatos
    creado_por = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='conceptos_financieros_creados'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Concepto Financiero"
        verbose_name_plural = "Conceptos Financieros"
        ordering = ['nombre']
        indexes = [
            models.Index(fields=['tipo', 'estado']),
            models.Index(fields=['fecha_vigencia_desde', 'fecha_vigencia_hasta']),
        ]

    def __str__(self):
        return f"{self.nombre} - ${self.monto}"

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.fecha_vigencia_hasta and self.fecha_vigencia_hasta < self.fecha_vigencia_desde:
            raise ValidationError("La fecha de fin no puede ser anterior a la fecha de inicio")

    @property
    def esta_vigente(self):
        """Verifica si el concepto está vigente en la fecha actual"""
        hoy = date.today()
        inicio_ok = hoy >= self.fecha_vigencia_desde
        fin_ok = self.fecha_vigencia_hasta is None or hoy <= self.fecha_vigencia_hasta
        return self.estado == EstadoConcepto.ACTIVO and inicio_ok and fin_ok


class EstadoCargo(models.TextChoices):
    """Estados de los cargos aplicados"""
    PENDIENTE = 'pendiente', 'Pendiente'
    PAGADO = 'pagado', 'Pagado'
    VENCIDO = 'vencido', 'Vencido'
    CANCELADO = 'cancelado', 'Cancelado'


class CargoFinanciero(models.Model):
    """
    Modelo para cargos específicos aplicados a residentes
    Representa la aplicación de un concepto financiero a un usuario específico
    """
    concepto = models.ForeignKey(
        ConceptoFinanciero,
        on_delete=models.PROTECT,
        related_name='cargos_aplicados'
    )
    residente = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cargos_financieros'
    )
    monto = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        verbose_name="Monto a Pagar"
    )
    estado = models.CharField(
        max_length=15,
        choices=EstadoCargo.choices,
        default=EstadoCargo.PENDIENTE,
        verbose_name="Estado del Cargo"
    )
    
    # Fechas importantes
    fecha_aplicacion = models.DateField(
        default=date.today,
        verbose_name="Fecha de Aplicación"
    )
    fecha_vencimiento = models.DateField(
        verbose_name="Fecha de Vencimiento"
    )
    fecha_pago = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de Pago"
    )
    
    # Información adicional
    observaciones = models.TextField(
        blank=True,
        verbose_name="Observaciones"
    )
    referencia_pago = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="Referencia de Pago"
    )
    
    # Metadatos
    aplicado_por = models.ForeignKey(
        User,
        on_delete=models.PROTECT,
        related_name='cargos_aplicados_por_mi'
    )
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_modificacion = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Cargo Financiero"
        verbose_name_plural = "Cargos Financieros"
        ordering = ['-fecha_aplicacion', 'estado']
        indexes = [
            models.Index(fields=['residente', 'estado']),
            models.Index(fields=['fecha_vencimiento', 'estado']),
            models.Index(fields=['concepto', 'fecha_aplicacion']),
        ]

    def __str__(self):
        return f"{self.concepto.nombre} - {self.residente.username} - ${self.monto}"

    @property
    def esta_vencido(self):
        """Verifica si el cargo está vencido"""
        if not self.fecha_vencimiento:
            return False
        return date.today() > self.fecha_vencimiento and self.estado == EstadoCargo.PENDIENTE

    @property
    def dias_para_vencimiento(self):
        """Calcula días restantes para el vencimiento"""
        if self.estado != EstadoCargo.PENDIENTE or not self.fecha_vencimiento:
            return None
        delta = self.fecha_vencimiento - date.today()
        return delta.days

    def marcar_como_pagado(self, referencia_pago='', usuario_proceso=None):
        """Marca el cargo como pagado"""
        from django.utils import timezone
        self.estado = EstadoCargo.PAGADO
        self.fecha_pago = timezone.now()
        self.referencia_pago = referencia_pago
        if usuario_proceso:
            self.observaciones += f"\nProcesado por: {usuario_proceso.username}"
        self.save()