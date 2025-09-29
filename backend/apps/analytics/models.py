"""
Modelos para el Módulo de Reportes y Analítica
Módulo 8: Reportes y Analítica

Este módulo maneja:
- Reportes Financieros
- Reportes de Seguridad
- Reportes de Uso de Áreas Comunes
- Predicciones de Morosidad con IA
"""

from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()


class ReporteFinanciero(models.Model):
    """
    Modelo para reportes financieros del condominio
    """

    TIPO_CHOICES = [
        ('ingresos', 'Ingresos'),
        ('egresos', 'Egresos'),
        ('balance', 'Balance General'),
        ('estado_cuenta', 'Estado de Cuenta'),
        ('morosidad', 'Morosidad'),
        ('presupuesto', 'Presupuesto'),
    ]

    PERIODO_CHOICES = [
        ('diario', 'Diario'),
        ('semanal', 'Semanal'),
        ('mensual', 'Mensual'),
        ('trimestral', 'Trimestral'),
        ('anual', 'Anual'),
    ]

    FORMATO_CHOICES = [
        ('json', 'JSON'),
        ('pdf', 'PDF'),
        ('excel', 'Excel'),
        ('csv', 'CSV'),
    ]

    # Información básica
    titulo = models.CharField(max_length=200, help_text="Título del reporte")
    descripcion = models.TextField(blank=True, help_text="Descripción del reporte")

    # Configuración del reporte
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, help_text="Tipo de reporte financiero")
    periodo = models.CharField(max_length=20, choices=PERIODO_CHOICES, help_text="Período del reporte")
    formato = models.CharField(max_length=10, choices=FORMATO_CHOICES, default='json', help_text="Formato de salida")

    # Fechas
    fecha_inicio = models.DateField(help_text="Fecha de inicio del período")
    fecha_fin = models.DateField(help_text="Fecha de fin del período")
    fecha_generacion = models.DateTimeField(auto_now_add=True, help_text="Fecha cuando se generó el reporte")

    # Usuario que generó el reporte
    generado_por = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reportes_financieros')

    # Datos del reporte (JSON)
    datos = models.JSONField(help_text="Datos del reporte en formato JSON")

    # Metadatos
    total_registros = models.PositiveIntegerField(default=0, help_text="Total de registros procesados")
    filtros_aplicados = models.JSONField(default=dict, help_text="Filtros aplicados al reporte")

    class Meta:
        verbose_name = "Reporte Financiero"
        verbose_name_plural = "Reportes Financieros"
        ordering = ['-fecha_generacion']

    def __str__(self):
        return f"{self.titulo} - {self.fecha_generacion.strftime('%d/%m/%Y')}"


class ReporteSeguridad(models.Model):
    """
    Modelo para reportes de seguridad del condominio
    """

    TIPO_CHOICES = [
        ('accesos', 'Accesos al Condominio'),
        ('incidentes', 'Incidentes de Seguridad'),
        ('alertas', 'Alertas del Sistema'),
        ('patrones', 'Patrones de Comportamiento'),
        ('auditoria', 'Auditoría de Seguridad'),
    ]

    PERIODO_CHOICES = [
        ('hora', 'Última Hora'),
        ('dia', 'Últimas 24 Horas'),
        ('semana', 'Última Semana'),
        ('mes', 'Último Mes'),
        ('personalizado', 'Período Personalizado'),
    ]

    # Información básica
    titulo = models.CharField(max_length=200, help_text="Título del reporte")
    descripcion = models.TextField(blank=True, help_text="Descripción del reporte")

    # Configuración del reporte
    tipo = models.CharField(max_length=20, choices=TIPO_CHOICES, help_text="Tipo de reporte de seguridad")
    periodo = models.CharField(max_length=20, choices=PERIODO_CHOICES, help_text="Período del reporte")

    # Fechas
    fecha_inicio = models.DateTimeField(help_text="Fecha y hora de inicio")
    fecha_fin = models.DateTimeField(help_text="Fecha y hora de fin")
    fecha_generacion = models.DateTimeField(auto_now_add=True, help_text="Fecha cuando se generó el reporte")

    # Usuario que generó el reporte
    generado_por = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reportes_seguridad')

    # Datos del reporte
    datos = models.JSONField(help_text="Datos del reporte en formato JSON")

    # Estadísticas resumidas
    total_eventos = models.PositiveIntegerField(default=0, help_text="Total de eventos registrados")
    eventos_criticos = models.PositiveIntegerField(default=0, help_text="Número de eventos críticos")
    alertas_generadas = models.PositiveIntegerField(default=0, help_text="Número de alertas generadas")

    # Filtros aplicados
    filtros_aplicados = models.JSONField(default=dict, help_text="Filtros aplicados al reporte")

    class Meta:
        verbose_name = "Reporte de Seguridad"
        verbose_name_plural = "Reportes de Seguridad"
        ordering = ['-fecha_generacion']

    def __str__(self):
        return f"Seguridad: {self.titulo} - {self.fecha_generacion.strftime('%d/%m/%Y %H:%M')}"


class ReporteUsoAreas(models.Model):
    """
    Modelo para reportes de uso de áreas comunes
    """

    AREA_CHOICES = [
        ('gimnasio', 'Gimnasio'),
        ('piscina', 'Piscina'),
        ('salon_eventos', 'Salón de Eventos'),
        ('estacionamiento', 'Estacionamiento'),
        ('areas_verdes', 'Áreas Verdes'),
        ('todas', 'Todas las Áreas'),
    ]

    PERIODO_CHOICES = [
        ('dia', 'Diario'),
        ('semana', 'Semanal'),
        ('mes', 'Mensual'),
        ('trimestre', 'Trimestral'),
        ('ano', 'Anual'),
    ]

    METRICA_CHOICES = [
        ('ocupacion', 'Tasa de Ocupación'),
        ('reservas', 'Número de Reservas'),
        ('tiempo_promedio', 'Tiempo Promedio de Uso'),
        ('patrones_horarios', 'Patrones Horarios'),
        ('comparativo', 'Comparativo Periódico'),
    ]

    # Información básica
    titulo = models.CharField(max_length=200, help_text="Título del reporte")
    descripcion = models.TextField(blank=True, help_text="Descripción del reporte")

    # Configuración del reporte
    area = models.CharField(max_length=20, choices=AREA_CHOICES, help_text="Área común a reportar")
    periodo = models.CharField(max_length=20, choices=PERIODO_CHOICES, help_text="Período del reporte")
    metrica_principal = models.CharField(max_length=20, choices=METRICA_CHOICES, help_text="Métrica principal")

    # Fechas
    fecha_inicio = models.DateField(help_text="Fecha de inicio del período")
    fecha_fin = models.DateField(help_text="Fecha de fin del período")
    fecha_generacion = models.DateTimeField(auto_now_add=True, help_text="Fecha cuando se generó el reporte")

    # Usuario que generó el reporte
    generado_por = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reportes_uso_areas')

    # Datos del reporte
    datos = models.JSONField(help_text="Datos del reporte en formato JSON")

    # Estadísticas resumidas
    total_reservas = models.PositiveIntegerField(default=0, help_text="Total de reservas en el período")
    horas_ocupacion = models.DecimalField(max_digits=8, decimal_places=2, default=0, help_text="Horas totales de ocupación")
    tasa_ocupacion_promedio = models.DecimalField(max_digits=5, decimal_places=2, default=0, validators=[MinValueValidator(0), MaxValueValidator(100)], help_text="Tasa de ocupación promedio (%)")

    # Filtros aplicados
    filtros_aplicados = models.JSONField(default=dict, help_text="Filtros aplicados al reporte")

    class Meta:
        verbose_name = "Reporte de Uso de Áreas"
        verbose_name_plural = "Reportes de Uso de Áreas"
        ordering = ['-fecha_generacion']

    def __str__(self):
        return f"Uso Áreas: {self.titulo} - {self.fecha_generacion.strftime('%d/%m/%Y')}"


class PrediccionMorosidad(models.Model):
    """
    Modelo para predicciones de morosidad usando IA
    """

    MODELO_CHOICES = [
        ('grok-4-fast-free', 'Grok 4 Fast Free'),
    ]

    NIVEL_CONFIANZA_CHOICES = [
        ('bajo', 'Bajo (60-70%)'),
        ('medio', 'Medio (70-80%)'),
        ('alto', 'Alto (80-90%)'),
        ('muy_alto', 'Muy Alto (90-95%)'),
    ]

    # Información básica
    titulo = models.CharField(max_length=200, help_text="Título de la predicción")
    descripcion = models.TextField(blank=True, help_text="Descripción de la predicción")

    # Configuración del modelo
    modelo_usado = models.CharField(max_length=20, choices=MODELO_CHOICES, help_text="Modelo de IA utilizado")
    nivel_confianza = models.CharField(max_length=10, choices=NIVEL_CONFIANZA_CHOICES, help_text="Nivel de confianza del modelo")

    # Fechas
    fecha_prediccion = models.DateTimeField(auto_now_add=True, help_text="Fecha cuando se realizó la predicción")
    periodo_predicho = models.CharField(max_length=100, help_text="Período que se está prediciendo")

    # Usuario que generó la predicción
    generado_por = models.ForeignKey(User, on_delete=models.CASCADE, related_name='predicciones_morosidad')

    # Residente específico (opcional para predicciones individuales)
    residente_especifico = models.BooleanField(default=False, help_text="Indica si la predicción es para un residente específico")
    residente = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='predicciones_morosidad_individual', help_text="Residente específico para predicción individual")

    # Datos de entrada para la predicción
    datos_entrada = models.JSONField(help_text="Datos utilizados como entrada para la predicción")

    # Resultados de la predicción
    resultados = models.JSONField(help_text="Resultados de la predicción en formato JSON")

    # Estadísticas de la predicción
    total_residentes_analizados = models.PositiveIntegerField(default=0, help_text="Total de residentes analizados")
    residentes_riesgo_alto = models.PositiveIntegerField(default=0, help_text="Residentes con alto riesgo de morosidad")
    residentes_riesgo_medio = models.PositiveIntegerField(default=0, help_text="Residentes con medio riesgo de morosidad")
    precision_modelo = models.DecimalField(max_digits=5, decimal_places=2, default=0, validators=[MinValueValidator(0), MaxValueValidator(100)], help_text="Precisión del modelo (%)")

    # Metadatos del modelo
    parametros_modelo = models.JSONField(default=dict, help_text="Parámetros utilizados en el modelo")
    metricas_evaluacion = models.JSONField(default=dict, help_text="Métricas de evaluación del modelo")

    class Meta:
        verbose_name = "Predicción de Morosidad"
        verbose_name_plural = "Predicciones de Morosidad"
        ordering = ['-fecha_prediccion']

    def __str__(self):
        return f"Predicción: {self.titulo} - {self.fecha_prediccion.strftime('%d/%m/%Y %H:%M')}"

    def get_riesgo_porcentaje(self):
        """Calcula el porcentaje de residentes en riesgo"""
        if self.total_residentes_analizados == 0:
            return 0
        return round(((self.residentes_riesgo_alto + self.residentes_riesgo_medio) / self.total_residentes_analizados) * 100, 2)