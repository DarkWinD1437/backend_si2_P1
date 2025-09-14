from django.db import models
from django.contrib.auth import get_user_model

# Para referenciar el modelo User personalizado
User = get_user_model()

# Choices para campos ENUM
PRIORIDAD_CHOICES = [
    ('baja', 'Baja'),
    ('media', 'Media'),
    ('alta', 'Alta'),
]

ESTADO_RESERVA_CHOICES = [
    ('pendiente', 'Pendiente'),
    ('confirmada', 'Confirmada'),
    ('cancelada', 'Cancelada'),
    ('completada', 'Completada'),
]

ESTADO_PAGO_CHOICES = [
    ('pendiente', 'Pendiente'),
    ('completado', 'Completado'),
    ('fallido', 'Fallido'),
    ('reembolsado', 'Reembolsado'),
]

ESTADO_CUOTA_CHOICES = [
    ('pendiente', 'Pendiente'),
    ('pagada', 'Pagada'),
    ('vencida', 'Vencida'),
]

TIPO_USUARIO_CHOICES = [
    ('propietario', 'Propietario'),
    ('inquilino', 'Inquilino'),
    ('administrador', 'Administrador'),
    ('seguridad', 'Seguridad'),
]

METODO_PAGO_CHOICES = [
    ('transferencia', 'Transferencia'),
    ('tarjeta_credito', 'Tarjeta de Crédito'),
    ('efectivo', 'Efectivo'),
    ('digital', 'Digital'),
]

TIPO_MANTENIMIENTO_CHOICES = [
    ('preventivo', 'Preventivo'),
    ('correctivo', 'Correctivo'),
    ('urgente', 'Urgente'),
]

ESTADO_MANTENIMIENTO_CHOICES = [
    ('solicitado', 'Solicitado'),
    ('asignado', 'Asignado'),
    ('en_proceso', 'En Proceso'),
    ('completado', 'Completado'),
    ('cancelado', 'Cancelado'),
]

SEVERIDAD_CHOICES = [
    ('baja', 'Baja'),
    ('media', 'Media'),
    ('alta', 'Alta'),
    ('critica', 'Crítica'),
]

TIPO_REPORTE_CHOICES = [
    ('financiero', 'Financiero'),
    ('reservas', 'Reservas'),
    ('seguridad', 'Seguridad'),
    ('mantenimiento', 'Mantenimiento'),
]


class Rol(models.Model):
    """Roles del sistema"""
    id_rol = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True, null=True)

    class Meta:
        managed = True  # ✅ Cambiar a True para que Django gestione la tabla
        db_table = 'rol'
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'

    def __str__(self):
        return self.nombre


class Usuario(models.Model):
    """Usuarios del condominio"""
    id_usuario = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100)
    email = models.EmailField(max_length=100, unique=True)
    password = models.CharField(max_length=255)
    telefono = models.CharField(max_length=20, blank=True, null=True)
    tipo = models.CharField(max_length=20, choices=TIPO_USUARIO_CHOICES, default='propietario')
    fecha_registro = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    class Meta:
        managed = True
        db_table = 'usuario'
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def __str__(self):
        return f"{self.nombre} ({self.email})"


class AreaComun(models.Model):
    """Áreas comunes del condominio"""
    id_areacomun = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    capacidad = models.PositiveIntegerField()
    precio_hora = models.DecimalField(max_digits=10, decimal_places=2)
    horario_disponible = models.CharField(max_length=100, blank=True, null=True)
    activa = models.BooleanField(default=True)

    class Meta:
        managed = True
        db_table = 'area_comun'
        verbose_name = 'Área Común'
        verbose_name_plural = 'Áreas Comunes'

    def __str__(self):
        return self.nombre


class Zona(models.Model):
    """Zonas dentro de áreas comunes"""
    id_zona = models.AutoField(primary_key=True)
    id_areacomun = models.ForeignKey(AreaComun, on_delete=models.CASCADE, db_column='id_areacomun')
    nombre = models.CharField(max_length=100)
    tipo = models.CharField(max_length=50)

    class Meta:
        managed = True
        db_table = 'zona'
        verbose_name = 'Zona'
        verbose_name_plural = 'Zonas'

    def __str__(self):
        return f"{self.nombre} - {self.id_areacomun.nombre}"


class Camara(models.Model):
    """Cámaras de seguridad"""
    id_camara = models.AutoField(primary_key=True)
    id_zona = models.ForeignKey(Zona, on_delete=models.CASCADE, db_column='id_zona')
    nombre = models.CharField(max_length=100)
    ubicacion = models.CharField(max_length=200)
    url_stream = models.URLField(max_length=500, blank=True, null=True)
    activa = models.BooleanField(default=True)

    class Meta:
        managed = True
        db_table = 'camara'
        verbose_name = 'Cámara'
        verbose_name_plural = 'Cámaras'

    def __str__(self):
        return self.nombre


class TipoEvento(models.Model):
    """Tipos de eventos de seguridad"""
    id_tipoevento = models.AutoField(primary_key=True)
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True, null=True)
    severidad = models.CharField(max_length=20, choices=SEVERIDAD_CHOICES, default='media')

    class Meta:
        managed = True
        db_table = 'tipo_evento'
        verbose_name = 'Tipo de Evento'
        verbose_name_plural = 'Tipos de Eventos'

    def __str__(self):
        return self.nombre


class VehiculoAutorizado(models.Model):
    """Vehículos autorizados"""
    id_vehiculoautorizado = models.AutoField(primary_key=True)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='id_usuario')
    placa = models.CharField(max_length=20, unique=True)
    modelo = models.CharField(max_length=100)
    color = models.CharField(max_length=50)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    activo = models.BooleanField(default=True)

    class Meta:
        managed = True
        db_table = 'vehiculo_autorizado'
        verbose_name = 'Vehículo Autorizado'
        verbose_name_plural = 'Vehículos Autorizados'

    def __str__(self):
        return f"{self.placa} - {self.modelo}"


class UnidadHabitacional(models.Model):
    """Unidades habitacionales del condominio"""
    id_unidadhabitacional = models.AutoField(primary_key=True)
    id_usuariopropietario = models.ForeignKey(
        Usuario, 
        on_delete=models.RESTRICT, 
        db_column='id_usuariopropietario',
        related_name='propiedades_propietario'
    )
    id_usuarioinquilino = models.ForeignKey(
        Usuario, 
        on_delete=models.SET_NULL, 
        db_column='id_usuarioinquilino',
        blank=True, null=True,
        related_name='propiedades_inquilino'
    )
    identificador = models.CharField(max_length=50, unique=True)
    tipo = models.CharField(max_length=50)
    metros_cuadrados = models.DecimalField(max_digits=8, decimal_places=2)
    activo = models.BooleanField(default=True)

    class Meta:
        managed = True
        db_table = 'unidad_habitacional'
        verbose_name = 'Unidad Habitacional'
        verbose_name_plural = 'Unidades Habitacionales'

    def __str__(self):
        return f"{self.identificador} - {self.tipo}"


class Reserva(models.Model):
    """Reservas de áreas comunes"""
    id_reserva = models.AutoField(primary_key=True)
    id_areacomun = models.ForeignKey(AreaComun, on_delete=models.RESTRICT, db_column='id_areacomun')
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='id_usuario')
    fecha_inicio = models.DateTimeField()
    fecha_fin = models.DateTimeField()
    monto_total = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(max_length=20, choices=ESTADO_RESERVA_CHOICES, default='pendiente')
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed = True
        db_table = 'reserva'
        verbose_name = 'Reserva'
        verbose_name_plural = 'Reservas'

    def __str__(self):
        return f"{self.id_areacomun.nombre} - {self.id_usuario.nombre} ({self.fecha_inicio})"


class Cuota(models.Model):
    """Cuotas de mantenimiento"""
    id_cuota = models.AutoField(primary_key=True)
    id_unidadhabitacional = models.ForeignKey(UnidadHabitacional, on_delete=models.CASCADE, db_column='id_unidadhabitacional')
    concepto = models.CharField(max_length=200)
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_emision = models.DateField()
    fecha_vencimiento = models.DateField()
    estado = models.CharField(max_length=20, choices=ESTADO_CUOTA_CHOICES, default='pendiente')
    fecha_pago = models.DateTimeField(blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'cuota'
        verbose_name = 'Cuota'
        verbose_name_plural = 'Cuotas'

    def __str__(self):
        return f"{self.concepto} - {self.id_unidadhabitacional.identificador}"


class Pago(models.Model):
    """Pagos realizados"""
    id_pago = models.AutoField(primary_key=True)
    id_cuota = models.ForeignKey(Cuota, on_delete=models.CASCADE, db_column='id_cuota')
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    fecha_pago = models.DateTimeField(auto_now_add=True)
    metodo_pago = models.CharField(max_length=20, choices=METODO_PAGO_CHOICES)
    comprobante_url = models.CharField(max_length=500, blank=True, null=True)
    estado = models.CharField(max_length=20, choices=ESTADO_PAGO_CHOICES, default='completado')

    class Meta:
        managed = True
        db_table = 'pago'
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'

    def __str__(self):
        return f"Pago {self.id_pago} - ${self.monto}"


class Aviso(models.Model):
    """Avisos del condominio"""
    id_aviso = models.AutoField(primary_key=True)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='id_usuario')
    titulo = models.CharField(max_length=200)
    contenido = models.TextField()
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    fecha_expiracion = models.DateTimeField(blank=True, null=True)
    prioridad = models.CharField(max_length=20, choices=PRIORIDAD_CHOICES, default='media')

    class Meta:
        managed = True
        db_table = 'aviso'
        verbose_name = 'Aviso'
        verbose_name_plural = 'Avisos'

    def __str__(self):
        return self.titulo


class EventoSeguridad(models.Model):
    """Eventos de seguridad"""
    id_eventoseguridad = models.AutoField(primary_key=True)
    id_camara = models.ForeignKey(Camara, on_delete=models.CASCADE, db_column='id_camara')
    id_tipoevento = models.ForeignKey(TipoEvento, on_delete=models.RESTRICT, db_column='id_tipoevento')
    id_usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, db_column='id_usuario', blank=True, null=True)
    id_vehiculoautorizado = models.ForeignKey(VehiculoAutorizado, on_delete=models.SET_NULL, db_column='id_vehiculoautorizado', blank=True, null=True)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    descripcion = models.TextField(blank=True, null=True)
    evidencia_url = models.CharField(max_length=500, blank=True, null=True)
    severidad = models.CharField(max_length=20, choices=SEVERIDAD_CHOICES, default='media')
    revisado = models.BooleanField(default=False)

    class Meta:
        managed = True
        db_table = 'evento_seguridad'
        verbose_name = 'Evento de Seguridad'
        verbose_name_plural = 'Eventos de Seguridad'

    def __str__(self):
        return f"{self.id_tipoevento.nombre} - {self.fecha_hora}"


class Mantenimiento(models.Model):
    """Mantenimientos solicitados"""
    id_mantenimiento = models.AutoField(primary_key=True)
    id_unidadhabitacional = models.ForeignKey(UnidadHabitacional, on_delete=models.CASCADE, db_column='id_unidadhabitacional')
    descripcion = models.TextField()
    tipo = models.CharField(max_length=20, choices=TIPO_MANTENIMIENTO_CHOICES, default='correctivo')
    prioridad = models.CharField(max_length=20, choices=PRIORIDAD_CHOICES, default='media')
    estado = models.CharField(max_length=20, choices=ESTADO_MANTENIMIENTO_CHOICES, default='solicitado')
    fecha_solicitud = models.DateTimeField(auto_now_add=True)
    fecha_asignacion = models.DateTimeField(blank=True, null=True)
    fecha_completado = models.DateTimeField(blank=True, null=True)
    costo = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'mantenimiento'
        verbose_name = 'Mantenimiento'
        verbose_name_plural = 'Mantenimientos'

    def __str__(self):
        return f"{self.descripcion[:50]} - {self.id_unidadhabitacional.identificador}"


class Reporte(models.Model):
    """Reportes generados"""
    id_reporte = models.AutoField(primary_key=True)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.CASCADE, db_column='id_usuario')
    tipo_reporte = models.CharField(max_length=20, choices=TIPO_REPORTE_CHOICES)
    fecha_generacion = models.DateTimeField(auto_now_add=True)
    parametros = models.JSONField(blank=True, null=True)
    url_reporte = models.CharField(max_length=500)

    class Meta:
        managed = True
        db_table = 'reporte'
        verbose_name = 'Reporte'
        verbose_name_plural = 'Reportes'

    def __str__(self):
        return f"Reporte {self.tipo_reporte} - {self.fecha_generacion}"


class Bitacora(models.Model):
    """Bitácora de auditoría"""
    id_bitacora = models.AutoField(primary_key=True)
    id_usuario = models.ForeignKey(Usuario, on_delete=models.SET_NULL, db_column='id_usuario', blank=True, null=True)
    registroafectado = models.IntegerField(blank=True, null=True)
    tabla_afectada = models.CharField(max_length=100)
    accion = models.CharField(max_length=20)
    valores_anteriores = models.JSONField(blank=True, null=True)
    valores_nuevos = models.JSONField(blank=True, null=True)
    fecha_hora = models.DateTimeField(auto_now_add=True)
    ip_origen = models.CharField(max_length=45, blank=True, null=True)

    class Meta:
        managed = True
        db_table = 'bitacora'
        verbose_name = 'Bitácora'
        verbose_name_plural = 'Bitácoras'

    def __str__(self):
        return f"{self.accion} en {self.tabla_afectada} - {self.fecha_hora}"
