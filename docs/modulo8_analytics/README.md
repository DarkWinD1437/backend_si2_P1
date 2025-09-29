# Módulo 8: Reportes y Analítica

## Descripción General

El **Módulo de Reportes y Analítica** proporciona herramientas avanzadas para generar reportes financieros, de seguridad, de uso de áreas comunes y predicciones de morosidad utilizando inteligencia artificial. Este módulo está diseñado para ayudar a la administración del condominio a tomar decisiones informadas basadas en datos históricos y análisis predictivos.

## Funcionalidades Principales

### 1. 📊 Generar Reporte Financiero
- **Tipos de reportes**: Ingresos, Egresos, Balance General, Estado de Cuenta, Morosidad, Presupuesto
- **Formatos**: JSON, PDF, Excel, CSV
- **Períodos**: Diario, Semanal, Mensual, Trimestral, Anual
- **Filtros avanzados** por fechas, categorías y usuarios

### 2. 🔒 Generar Reporte de Seguridad
- **Tipos de reportes**: Accesos, Incidentes, Alertas, Patrones, Auditoría
- **Métricas**: Eventos críticos, alertas generadas, tiempos de respuesta
- **Análisis de patrones** de comportamiento y seguridad
- **Reportes en tiempo real** y históricos

### 3. 🏊 Generar Reporte de Uso de Áreas Comunes
- **Áreas comunes**: Gimnasio, Piscina, Salón de Eventos, Estacionamiento, Áreas Verdes
- **Métricas**: Tasa de ocupación, reservas, tiempo promedio, patrones horarios
- **Análisis comparativo** entre períodos
- **Optimización de recursos** basada en datos

### 4. 🤖 Generar Predicción de Morosidad con IA
- **Modelos de IA**: Regresión Logística, Random Forest, XGBoost, Red Neuronal, Ensemble
- **Análisis predictivo** de riesgo de morosidad
- **Métricas de evaluación**: Precisión, recall, F1-score, AUC-ROC
- **Niveles de confianza**: Bajo, Medio, Alto, Muy Alto

## Arquitectura del Sistema

### Modelos de Datos

#### ReporteFinanciero
```python
- titulo: CharField (Título del reporte)
- tipo: ChoiceField (ingresos, egresos, balance, etc.)
- periodo: ChoiceField (diario, semanal, mensual, etc.)
- formato: ChoiceField (json, pdf, excel, csv)
- fecha_inicio/fech_fin: DateField
- generado_por: ForeignKey(User)
- datos: JSONField (Datos del reporte)
- filtros_aplicados: JSONField
```

#### ReporteSeguridad
```python
- titulo: CharField
- tipo: ChoiceField (accesos, incidentes, alertas, etc.)
- periodo: ChoiceField
- fecha_inicio/fecha_fin: DateTimeField
- generado_por: ForeignKey(User)
- datos: JSONField
- total_eventos: PositiveIntegerField
- eventos_criticos: PositiveIntegerField
- alertas_generadas: PositiveIntegerField
```

#### ReporteUsoAreas
```python
- titulo: CharField
- area: ChoiceField (gimnasio, piscina, etc.)
- periodo: ChoiceField
- metrica_principal: ChoiceField
- fecha_inicio/fecha_fin: DateField
- generado_por: ForeignKey(User)
- datos: JSONField
- total_reservas: PositiveIntegerField
- horas_ocupacion: DecimalField
- tasa_ocupacion_promedio: DecimalField
```

#### PrediccionMorosidad
```python
- titulo: CharField
- modelo_usado: ChoiceField
- nivel_confianza: ChoiceField
- fecha_prediccion: DateTimeField
- generado_por: ForeignKey(User)
- datos_entrada: JSONField
- resultados: JSONField
- precision_modelo: DecimalField
- metricas_evaluacion: JSONField
```

## API Endpoints

### Reportes Financieros
```
GET    /api/analytics/reportes-financieros/                    # Listar reportes
POST   /api/analytics/reportes-financieros/                    # Crear reporte
GET    /api/analytics/reportes-financieros/{id}/               # Detalle reporte
POST   /api/analytics/reportes-financieros/generar_reporte/    # Generar reporte financiero
```

### Reportes de Seguridad
```
GET    /api/analytics/reportes-seguridad/                      # Listar reportes
POST   /api/analytics/reportes-seguridad/                      # Crear reporte
GET    /api/analytics/reportes-seguridad/{id}/                 # Detalle reporte
POST   /api/analytics/reportes-seguridad/generar_reporte/      # Generar reporte de seguridad
```

### Reportes de Uso de Áreas
```
GET    /api/analytics/reportes-uso-areas/                      # Listar reportes
POST   /api/analytics/reportes-uso-areas/                      # Crear reporte
GET    /api/analytics/reportes-uso-areas/{id}/                 # Detalle reporte
POST   /api/analytics/reportes-uso-areas/generar_reporte/      # Generar reporte de uso de áreas
```

### Predicciones de Morosidad
```
GET    /api/analytics/predicciones-morosidad/                  # Listar predicciones
POST   /api/analytics/predicciones-morosidad/                  # Crear predicción
GET    /api/analytics/predicciones-morosidad/{id}/             # Detalle predicción
POST   /api/analytics/predicciones-morosidad/generar_prediccion/ # Generar predicción con IA
```

## Permisos y Seguridad

### Niveles de Acceso
- **Administradores**: Acceso completo a todos los reportes y predicciones
- **Staff (Mantenimiento/Seguridad)**: Acceso de solo lectura a reportes
- **Residentes**: Sin acceso al módulo

### Autenticación
- Requiere autenticación Token/JWT
- Validación de roles por endpoint
- Logs de auditoría para todas las operaciones

## Casos de Uso

### 1. Reporte Financiero Mensual
```json
POST /api/analytics/reportes-financieros/generar_reporte/
{
  "titulo": "Balance Financiero Agosto 2024",
  "descripcion": "Análisis completo de ingresos y egresos",
  "tipo": "balance",
  "periodo": "mensual",
  "formato": "pdf",
  "fecha_inicio": "2024-08-01",
  "fecha_fin": "2024-08-31"
}
```

### 2. Reporte de Seguridad Semanal
```json
POST /api/analytics/reportes-seguridad/generar_reporte/
{
  "titulo": "Incidentes de Seguridad - Semana 35",
  "descripcion": "Análisis de eventos de seguridad",
  "tipo": "incidentes",
  "periodo": "semanal",
  "fecha_inicio": "2024-08-26T00:00:00Z",
  "fecha_fin": "2024-09-01T23:59:59Z"
}
```

### 3. Reporte de Uso de Piscina
```json
POST /api/analytics/reportes-uso-areas/generar_reporte/
{
  "titulo": "Ocupación Piscina Verano 2024",
  "descripcion": "Análisis de uso de piscina",
  "area": "piscina",
  "periodo": "mensual",
  "metrica_principal": "ocupacion",
  "fecha_inicio": "2024-06-01",
  "fecha_fin": "2024-08-31"
}
```

### 4. Predicción de Morosidad
```json
POST /api/analytics/predicciones-morosidad/generar_prediccion/
{
  "titulo": "Predicción Morosidad Q4 2024",
  "descripcion": "Análisis predictivo de riesgo de morosidad",
  "modelo_usado": "random_forest",
  "periodo_predicho": "Próximos 3 meses"
}
```

## Panel de Administración

### 🔧 Sección: Gestión de Mantenimiento
- **Solicitudes de Mantenimiento**: Gestión completa de solicitudes reportadas por residentes
- **Tareas de Mantenimiento**: Asignación, seguimiento y resolución de tareas
- **Estados**: Pendiente, En Progreso, Completado, Cancelado
- **Prioridades**: Baja, Media, Alta, Urgente

### 📊 Sección: Reportes y Analíticas
- **Reportes Financieros**: Ingresos, egresos, balances y análisis financiero
- **Reportes de Seguridad**: Incidentes, accesos y eventos de seguridad
- **Reportes de Uso de Áreas**: Ocupación y métricas de áreas comunes
- **Predicciones de Morosidad**: Análisis predictivo con modelos de IA

### Características del Panel
- **Navegación organizada** por secciones temáticas
- **Iconos visuales** para identificación rápida
- **Filtros avanzados** y búsqueda en tiempo real
- **Campos de solo lectura** para datos generados automáticamente
- **Enlaces relacionados** entre modelos dependientes

## Tecnologías Utilizadas

- **Backend**: Django 5.2 + Django REST Framework
- **Base de Datos**: PostgreSQL con JSONField para datos flexibles
- **Autenticación**: Token Authentication + JWT
- **Documentación**: drf-spectacular (Swagger/ReDoc)
- **IA/ML**: Scikit-learn, TensorFlow (para predicciones futuras)
- **Formateo**: ReportLab (PDF), OpenPyXL (Excel), Pandas (CSV)

## Próximas Funcionalidades

- [ ] Dashboards en tiempo real
- [ ] Alertas automáticas basadas en predicciones
- [ ] Integración con Power BI/Tableau
- [ ] Modelos de IA más avanzados (Deep Learning)
- [ ] API para integración con sistemas externos
- [ ] Reportes programados automáticos

## Documentación Relacionada

- [Modelos de Datos](modelos.md)
- [Endpoints API](endpoints.md)
- [Permisos y Seguridad](permisos.md)
- [Panel de Administración](admin_panel.md)
- [Guía de Testing](testing.md)