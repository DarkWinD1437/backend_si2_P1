# Modelos de Datos - Módulo 8: Reportes y Analítica

## Descripción

Este documento describe los modelos de datos utilizados en el Módulo de Reportes y Analítica, incluyendo su estructura, campos y relaciones.

## Modelos Principales

### 1. ReporteFinanciero

Modelo para almacenar reportes financieros del condominio.

#### Campos

| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|-----------|
| `titulo` | CharField(200) | Título del reporte | Sí |
| `descripcion` | TextField | Descripción detallada | No |
| `tipo` | CharField | Tipo de reporte financiero | Sí |
| `periodo` | CharField | Período del reporte | Sí |
| `formato` | CharField | Formato de salida | Sí (default: 'json') |
| `fecha_inicio` | DateField | Fecha de inicio del período | Sí |
| `fecha_fin` | DateField | Fecha de fin del período | Sí |
| `fecha_generacion` | DateTimeField | Fecha cuando se generó | Auto |
| `generado_por` | ForeignKey(User) | Usuario que generó el reporte | Auto |
| `datos` | JSONField | Datos del reporte en JSON | Sí |
| `total_registros` | PositiveIntegerField | Total de registros procesados | Sí (default: 0) |
| `filtros_aplicados` | JSONField | Filtros aplicados al reporte | Sí (default: {}) |

#### Opciones de Tipo
- `ingresos`: Reporte de ingresos
- `egresos`: Reporte de egresos
- `balance`: Balance general
- `estado_cuenta`: Estado de cuenta
- `morosidad`: Reporte de morosidad
- `presupuesto`: Análisis presupuestario

#### Opciones de Período
- `diario`: Período diario
- `semanal`: Período semanal
- `mensual`: Período mensual
- `trimestral`: Período trimestral
- `anual`: Período anual

#### Opciones de Formato
- `json`: Formato JSON
- `pdf`: Formato PDF
- `excel`: Formato Excel
- `csv`: Formato CSV

### 2. ReporteSeguridad

Modelo para almacenar reportes de seguridad del condominio.

#### Campos

| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|-----------|
| `titulo` | CharField(200) | Título del reporte | Sí |
| `descripcion` | TextField | Descripción detallada | No |
| `tipo` | CharField | Tipo de reporte de seguridad | Sí |
| `periodo` | CharField | Período del reporte | Sí |
| `fecha_inicio` | DateTimeField | Fecha/hora de inicio | Sí |
| `fecha_fin` | DateTimeField | Fecha/hora de fin | Sí |
| `fecha_generacion` | DateTimeField | Fecha cuando se generó | Auto |
| `generado_por` | ForeignKey(User) | Usuario que generó el reporte | Auto |
| `datos` | JSONField | Datos del reporte en JSON | Sí |
| `total_eventos` | PositiveIntegerField | Total de eventos registrados | Sí (default: 0) |
| `eventos_criticos` | PositiveIntegerField | Número de eventos críticos | Sí (default: 0) |
| `alertas_generadas` | PositiveIntegerField | Número de alertas generadas | Sí (default: 0) |
| `filtros_aplicados` | JSONField | Filtros aplicados al reporte | Sí (default: {}) |

#### Opciones de Tipo
- `accesos`: Accesos al condominio
- `incidentes`: Incidentes de seguridad
- `alertas`: Alertas del sistema
- `patrones`: Patrones de comportamiento
- `auditoria`: Auditoría de seguridad

#### Opciones de Período
- `hora`: Última hora
- `dia`: Últimas 24 horas
- `semana`: Última semana
- `mes`: Último mes
- `personalizado`: Período personalizado

### 3. ReporteUsoAreas

Modelo para almacenar reportes de uso de áreas comunes.

#### Campos

| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|-----------|
| `titulo` | CharField(200) | Título del reporte | Sí |
| `descripcion` | TextField | Descripción detallada | No |
| `area` | CharField | Área común a reportar | Sí |
| `periodo` | CharField | Período del reporte | Sí |
| `metrica_principal` | CharField | Métrica principal | Sí |
| `fecha_inicio` | DateField | Fecha de inicio del período | Sí |
| `fecha_fin` | DateField | Fecha de fin del período | Sí |
| `fecha_generacion` | DateTimeField | Fecha cuando se generó | Auto |
| `generado_por` | ForeignKey(User) | Usuario que generó el reporte | Auto |
| `datos` | JSONField | Datos del reporte en JSON | Sí |
| `total_reservas` | PositiveIntegerField | Total de reservas | Sí (default: 0) |
| `horas_ocupacion` | DecimalField(8,2) | Horas totales de ocupación | Sí (default: 0) |
| `tasa_ocupacion_promedio` | DecimalField(5,2) | Tasa de ocupación promedio (%) | Sí (default: 0) |
| `filtros_aplicados` | JSONField | Filtros aplicados al reporte | Sí (default: {}) |

#### Opciones de Área
- `gimnasio`: Gimnasio
- `piscina`: Piscina
- `salon_eventos`: Salón de Eventos
- `estacionamiento`: Estacionamiento
- `areas_verdes`: Áreas Verdes
- `todas`: Todas las áreas

#### Opciones de Período
- `dia`: Diario
- `semana`: Semanal
- `mes`: Mensual
- `trimestre`: Trimestral
- `ano`: Anual

#### Opciones de Métrica
- `ocupacion`: Tasa de ocupación
- `reservas`: Número de reservas
- `tiempo_promedio`: Tiempo promedio de uso
- `patrones_horarios`: Patrones horarios
- `comparativo`: Comparativo periódico

### 4. PrediccionMorosidad

Modelo para almacenar predicciones de morosidad usando IA.

#### Campos

| Campo | Tipo | Descripción | Requerido |
|-------|------|-------------|-----------|
| `titulo` | CharField(200) | Título de la predicción | Sí |
| `descripcion` | TextField | Descripción detallada | No |
| `modelo_usado` | CharField | Modelo de IA utilizado | Sí |
| `nivel_confianza` | CharField | Nivel de confianza del modelo | Sí |
| `fecha_prediccion` | DateTimeField | Fecha cuando se realizó | Auto |
| `periodo_predicho` | CharField(100) | Período que se está prediciendo | Sí |
| `generado_por` | ForeignKey(User) | Usuario que generó la predicción | Auto |
| `datos_entrada` | JSONField | Datos utilizados como entrada | Sí |
| `resultados` | JSONField | Resultados de la predicción | Sí |
| `total_residentes_analizados` | PositiveIntegerField | Total de residentes analizados | Sí (default: 0) |
| `residentes_riesgo_alto` | PositiveIntegerField | Residentes con alto riesgo | Sí (default: 0) |
| `residentes_riesgo_medio` | PositiveIntegerField | Residentes con medio riesgo | Sí (default: 0) |
| `precision_modelo` | DecimalField(5,2) | Precisión del modelo (%) | Sí (default: 0) |
| `parametros_modelo` | JSONField | Parámetros utilizados | Sí (default: {}) |
| `metricas_evaluacion` | JSONField | Métricas de evaluación | Sí (default: {}) |

#### Opciones de Modelo
- `regresion_logistica`: Regresión Logística
- `random_forest`: Random Forest
- `xgboost`: XGBoost
- `red_neuronal`: Red Neuronal
- `ensemble`: Ensemble de Modelos

#### Opciones de Nivel de Confianza
- `bajo`: Bajo (60-70%)
- `medio`: Medio (70-80%)
- `alto`: Alto (80-90%)
- `muy_alto`: Muy Alto (90-95%)

## Relaciones

### Relaciones con User
- `ReporteFinanciero.generado_por` → `User`
- `ReporteSeguridad.generado_por` → `User`
- `ReporteUsoAreas.generado_por` → `User`
- `PrediccionMorosidad.generado_por` → `User`

Todas las relaciones son ForeignKey con CASCADE en eliminación.

## Métodos del Modelo

### PrediccionMorosidad
- `get_riesgo_porcentaje()`: Calcula el porcentaje de residentes en riesgo

```python
def get_riesgo_porcentaje(self):
    """Calcula el porcentaje de residentes en riesgo"""
    if self.total_residentes_analizados == 0:
        return 0
    return round(((self.residentes_riesgo_alto + self.residentes_riesgo_medio) /
                  self.total_residentes_analizados) * 100, 2)
```

## Índices y Constraints

### Meta Configuración

```python
class Meta:
    verbose_name = "Reporte Financiero"
    verbose_name_plural = "Reportes Financieros"
    ordering = ['-fecha_generacion']
```

Todos los modelos tienen:
- `ordering = ['-fecha_generacion']` o `['-fecha_prediccion']`
- Nombres verbose en español
- Índices automáticos en campos de fecha

## Validaciones

### Validaciones de Fecha
- `fecha_fin` debe ser posterior a `fecha_inicio`
- Fechas no pueden ser futuras (excepto para predicciones)

### Validaciones Numéricas
- `tasa_ocupacion_promedio`: 0-100%
- `precision_modelo`: 0-100%
- Campos PositiveIntegerField no pueden ser negativos

## Campos Calculados

### ReporteUsoAreas
- `tasa_ocupacion_promedio`: Calculada automáticamente
- `horas_ocupacion`: Sumatoria de horas de uso

### PrediccionMorosidad
- `riesgo_porcentaje`: Calculado dinámicamente
- `nivel_confianza`: Determinado por precisión del modelo

## Serializers Asociados

Cada modelo tiene múltiples serializers:

1. **Serializer completo**: Para operaciones CRUD completas
2. **Serializer de lista**: Para listados optimizados
3. **Serializer de creación**: Para creación con validaciones específicas

Los serializers incluyen campos relacionados y métodos para información adicional del usuario generador.