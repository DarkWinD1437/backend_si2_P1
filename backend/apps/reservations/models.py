"""
Modelos para el Módulo de Reservas de Áreas Comunes
Módulo 4: Reservas de Áreas Comunes
T1: Consultar Disponibilidad de Área Común
T2: Reservar Área Común
T3: Confirmar Reserva con Pago
T4: Cancelar Reserva
"""

from django.db import models
from django.contrib.auth import get_user_model
from decimal import Decimal
from django.core.validators import MinValueValidator
from datetime import date, time, datetime, timedelta
from django.utils import timezone

User = get_user_model()


class TipoAreaComun(models.TextChoices):
    """Tipos de áreas comunes disponibles para reserva"""
    SALON_EVENTOS = 'salon_eventos', 'Salón de Eventos'
    GIMNASIO = 'gimnasio', 'Gimnasio'
    PISCINA = 'piscina', 'Piscina'
    CANCHA_TENIS = 'cancha_tenis', 'Cancha de Tenis'
    CANCHA_FUTBOL = 'cancha_futbol', 'Cancha de Fútbol'
    SALA_JUNTAS = 'sala_juntas', 'Sala de Juntas'
    BBQ = 'bbq', 'Área de BBQ'
    OTROS = 'otros', 'Otros'


class EstadoAreaComun(models.TextChoices):
    """Estados de las áreas comunes"""
    ACTIVA = 'activa', 'Activa'
    INACTIVA = 'inactiva', 'Inactiva'
    MANTENIMIENTO = 'mantenimiento', 'En Mantenimiento'


class EstadoReserva(models.TextChoices):
    """Estados de las reservas"""
    PENDIENTE = 'pendiente', 'Pendiente'
    CONFIRMADA = 'confirmada', 'Confirmada'
    PAGADA = 'pagada', 'Pagada'
    CANCELADA = 'cancelada', 'Cancelada'
    EXPIRADA = 'expirada', 'Expirada'
    USADA = 'usada', 'Usada'


class AreaComun(models.Model):
    """
    Modelo para definir áreas comunes disponibles para reserva
    """
    nombre = models.CharField(max_length=100, verbose_name="Nombre del Área")
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    tipo = models.CharField(
        max_length=20,
        choices=TipoAreaComun.choices,
        verbose_name="Tipo de Área"
    )
    capacidad_maxima = models.PositiveIntegerField(
        verbose_name="Capacidad Máxima",
        help_text="Número máximo de personas"
    )
    costo_por_hora = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        default=Decimal('0.00'),
        verbose_name="Costo por Hora"
    )
    costo_reserva = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        default=Decimal('0.00'),
        verbose_name="Costo de Reserva",
        help_text="Costo fijo por reserva (adicional al costo por hora)"
    )
    estado = models.CharField(
        max_length=15,
        choices=EstadoAreaComun.choices,
        default=EstadoAreaComun.ACTIVA,
        verbose_name="Estado"
    )
    requiere_aprobacion = models.BooleanField(
        default=False,
        verbose_name="Requiere Aprobación",
        help_text="Si es True, la reserva debe ser aprobada por un administrador"
    )
    tiempo_minimo_reserva = models.PositiveIntegerField(
        default=1,
        verbose_name="Tiempo Mínimo (horas)",
        help_text="Tiempo mínimo de reserva en horas"
    )
    tiempo_maximo_reserva = models.PositiveIntegerField(
        default=8,
        verbose_name="Tiempo Máximo (horas)",
        help_text="Tiempo máximo de reserva en horas"
    )
    anticipo_minimo_horas = models.PositiveIntegerField(
        default=24,
        verbose_name="Anticipación Mínima (horas)",
        help_text="Horas mínimas de anticipación para reservar"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Área Común"
        verbose_name_plural = "Áreas Comunes"
        ordering = ['tipo', 'nombre']

    def __str__(self):
        return f"{self.nombre} ({self.get_tipo_display()})"

    def esta_disponible_en_fecha(self, fecha, hora_inicio, hora_fin):
        """
        Verifica si el área está disponible en una fecha y horario específicos
        """
        if self.estado != EstadoAreaComun.ACTIVA:
            return False

        # Verificar si hay reservas confirmadas/pagadas en ese horario
        reservas_conflictivas = Reserva.objects.filter(
            area_comun=self,
            fecha=fecha,
            estado__in=[EstadoReserva.CONFIRMADA, EstadoReserva.PAGADA, EstadoReserva.USADA]
        ).filter(
            models.Q(hora_inicio__lt=hora_fin, hora_fin__gt=hora_inicio)
        )

        return not reservas_conflictivas.exists()

    def puede_reservar_usuario(self, usuario):
        """
        Verifica si un usuario puede reservar esta área
        """
        # Lógica básica: todos los residentes pueden reservar
        # Se puede extender con reglas específicas por área o usuario
        return usuario.role in ['resident', 'admin']

    def calcular_costo_total(self, horas):
        """
        Calcula el costo total de una reserva
        """
        costo_horas = self.costo_por_hora * Decimal(str(horas))
        return costo_horas + self.costo_reserva


class HorarioDisponible(models.Model):
    """
    Modelo para definir horarios disponibles para reservas
    """
    area_comun = models.ForeignKey(
        AreaComun,
        on_delete=models.CASCADE,
        related_name='horarios_disponibles',
        verbose_name="Área Común"
    )
    dia_semana = models.CharField(
        max_length=10,
        choices=[
            ('lunes', 'Lunes'),
            ('martes', 'Martes'),
            ('miercoles', 'Miércoles'),
            ('jueves', 'Jueves'),
            ('viernes', 'Viernes'),
            ('sabado', 'Sábado'),
            ('domingo', 'Domingo'),
        ],
        verbose_name="Día de la Semana"
    )
    hora_apertura = models.TimeField(verbose_name="Hora de Apertura")
    hora_cierre = models.TimeField(verbose_name="Hora de Cierre")
    activo = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        verbose_name = "Horario Disponible"
        verbose_name_plural = "Horarios Disponibles"
        unique_together = ['area_comun', 'dia_semana']
        ordering = ['area_comun', 'dia_semana']

    def __str__(self):
        return f"{self.area_comun.nombre} - {self.get_dia_semana_display()}"


class Reserva(models.Model):
    """
    Modelo para gestionar reservas de áreas comunes
    """
    area_comun = models.ForeignKey(
        AreaComun,
        on_delete=models.CASCADE,
        related_name='reservas',
        verbose_name="Área Común"
    )
    usuario = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reservas',
        verbose_name="Usuario"
    )
    fecha = models.DateField(verbose_name="Fecha de Reserva")
    hora_inicio = models.TimeField(verbose_name="Hora de Inicio")
    hora_fin = models.TimeField(verbose_name="Hora de Fin")
    duracion_horas = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        verbose_name="Duración (horas)"
    )
    estado = models.CharField(
        max_length=15,
        choices=EstadoReserva.choices,
        default=EstadoReserva.PENDIENTE,
        verbose_name="Estado"
    )
    costo_total = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        verbose_name="Costo Total"
    )
    observaciones = models.TextField(
        blank=True,
        verbose_name="Observaciones"
    )
    numero_personas = models.PositiveIntegerField(
        default=1,
        verbose_name="Número de Personas"
    )
    # Información de pago (se integra con módulo financiero)
    cargo_financiero = models.ForeignKey(
        'finances.CargoFinanciero',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reservas',
        verbose_name="Cargo Financiero"
    )
    # Información de cancelación
    cancelada_por = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reservas_canceladas',
        verbose_name="Cancelada Por"
    )
    motivo_cancelacion = models.TextField(
        blank=True,
        verbose_name="Motivo de Cancelación"
    )
    fecha_cancelacion = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="Fecha de Cancelación"
    )
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Reserva"
        verbose_name_plural = "Reservas"
        ordering = ['-fecha', '-hora_inicio']

    def __str__(self):
        return f"Reserva {self.area_comun.nombre} - {self.usuario.username} - {self.fecha}"

    def save(self, *args, **kwargs):
        # Calcular duración automáticamente
        if self.hora_inicio and self.hora_fin:
            inicio = datetime.combine(date.today(), self.hora_inicio)
            fin = datetime.combine(date.today(), self.hora_fin)
            if fin <= inicio:
                fin = datetime.combine(date.today() + timedelta(days=1), self.hora_fin)
            duracion = (fin - inicio).total_seconds() / 3600
            self.duracion_horas = Decimal(str(round(duracion, 2)))

        # Calcular costo total
        if not self.costo_total:
            self.costo_total = self.area_comun.calcular_costo_total(self.duracion_horas)

        super().save(*args, **kwargs)

    def puede_cancelar(self, usuario):
        """
        Verifica si un usuario puede cancelar esta reserva
        """
        # El propietario puede cancelar
        if self.usuario == usuario:
            return True

        # Administradores pueden cancelar cualquier reserva
        if usuario.role == 'admin':
            return True

        # No se puede cancelar si ya está pagada/usada
        if self.estado in [EstadoReserva.PAGADA, EstadoReserva.USADA]:
            return False

        return False

    def cancelar(self, usuario, motivo=""):
        """
        Cancela la reserva
        """
        if not self.puede_cancelar(usuario):
            raise ValueError("No tiene permisos para cancelar esta reserva")

        self.estado = EstadoReserva.CANCELADA
        self.cancelada_por = usuario
        self.motivo_cancelacion = motivo
        self.fecha_cancelacion = timezone.now()
        self.save()

        # Aquí se podría agregar lógica para reembolsar si ya se pagó
        # if self.cargo_financiero and self.cargo_financiero.estado == 'pagado':
        #     # Lógica de reembolso

    def confirmar(self):
        """
        Confirma la reserva (cambia de pendiente a confirmada)
        """
        if self.estado != EstadoReserva.PENDIENTE:
            raise ValueError("Solo se pueden confirmar reservas pendientes")

        self.estado = EstadoReserva.CONFIRMADA
        self.save()

    def marcar_pagada(self):
        """
        Marca la reserva como pagada
        """
        if self.estado not in [EstadoReserva.CONFIRMADA, EstadoReserva.PENDIENTE]:
            raise ValueError("Solo se pueden pagar reservas confirmadas o pendientes")

        self.estado = EstadoReserva.PAGADA
        self.save()

    @property
    def esta_vencida(self):
        """
        Verifica si la reserva está vencida
        """
        ahora = timezone.now()
        fecha_hora_reserva = datetime.combine(self.fecha, self.hora_inicio)
        fecha_hora_reserva = timezone.make_aware(fecha_hora_reserva)

        return ahora > fecha_hora_reserva and self.estado in [EstadoReserva.PENDIENTE, EstadoReserva.CONFIRMADA]

    @property
    def puede_confirmar(self):
        """
        Verifica si la reserva puede ser confirmada
        """
        return self.estado == EstadoReserva.PENDIENTE and not self.esta_vencida

    @property
    def puede_pagar(self):
        """
        Verifica si la reserva puede ser pagada
        """
        return self.estado in [EstadoReserva.PENDIENTE, EstadoReserva.CONFIRMADA] and not self.esta_vencida