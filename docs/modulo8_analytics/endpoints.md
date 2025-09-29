# Endpoints API - Módulo 8: Reportes y Analítica

## Descripción

Este documento describe todos los endpoints disponibles en el Módulo de Reportes y Analítica, incluyendo parámetros, respuestas y ejemplos de uso.

## Autenticación

Todos los endpoints requieren autenticación mediante Token o JWT. Incluir el header:

```
Authorization: Token <token>
```

## Endpoints de Reportes Financieros

### 1. Listar Reportes Financieros

**GET** `/api/analytics/reportes-financieros/`

Lista todos los reportes financieros accesibles para el usuario.

#### Parámetros de Query
- `tipo`: Filtrar por tipo (ingresos, egresos, balance, etc.)
- `periodo`: Filtrar por período (diario, semanal, mensual, etc.)
- `fecha_generacion_after`: Fecha de generación posterior a
- `fecha_generacion_before`: Fecha de generación anterior a

#### Respuesta Exitosa (200)
```json
[
  {
    "id": 1,
    "titulo": "Balance Mensual Agosto 2024",
    "tipo": "balance",
    "periodo": "mensual",
    "formato": "pdf",
    "fecha_inicio": "2024-08-01",
    "fecha_fin": "2024-08-31",
    "fecha_generacion": "2024-09-01T10:30:00Z",
    "generado_por_info": {
      "username": "admin",
      "role": "admin"
    },
    "total_registros": 150
  }
]
```

### 2. Crear Reporte Financiero

**POST** `/api/analytics/reportes-financieros/`

Crea un nuevo reporte financiero (solo estructura, sin generar datos).

#### Body
```json
{
  "titulo": "Balance Financiero Agosto 2024",
  "descripcion": "Análisis completo de ingresos y egresos",
  "tipo": "balance",
  "periodo": "mensual",
  "formato": "pdf",
  "fecha_inicio": "2024-08-01",
  "fecha_fin": "2024-08-31",
  "filtros_aplicados": {
    "categoria": "todas",
    "incluir_multas": true
  }
}
```

#### Respuesta Exitosa (201)
```json
{
  "id": 1,
  "titulo": "Balance Financiero Agosto 2024",
  "descripcion": "Análisis completo de ingresos y egresos",
  "tipo": "balance",
  "periodo": "mensual",
  "formato": "pdf",
  "fecha_inicio": "2024-08-01",
  "fecha_fin": "2024-08-31",
  "fecha_generacion": "2024-09-01T10:30:00Z",
  "generado_por": 1,
  "generado_por_info": {
    "id": 1,
    "username": "admin",
    "email": "admin@condominio.com",
    "role": "admin"
  },
  "datos": {},
  "total_registros": 0,
  "filtros_aplicados": {
    "categoria": "todas",
    "incluir_multas": true
  }
}
```

### 3. Generar Reporte Financiero

**POST** `/api/analytics/reportes-financieros/generar_reporte/`

Genera un reporte financiero completo con datos procesados.

#### Body
```json
{
  "titulo": "Ingresos Mensuales Agosto 2024",
  "descripcion": "Detalle de todos los ingresos del mes",
  "tipo": "ingresos",
  "periodo": "mensual",
  "formato": "json",
  "fecha_inicio": "2024-08-01",
  "fecha_fin": "2024-08-31",
  "filtros_aplicados": {
    "fuente": "cuotas_mantenimiento"
  }
}
```

#### Respuesta Exitosa (201)
```json
{
  "id": 2,
  "titulo": "Ingresos Mensuales Agosto 2024",
  "tipo": "ingresos",
  "periodo": "mensual",
  "formato": "json",
  "fecha_inicio": "2024-08-01",
  "fecha_fin": "2024-08-31",
  "fecha_generacion": "2024-09-01T10:35:00Z",
  "generado_por": 1,
  "generado_por_info": {
    "username": "admin",
    "role": "admin"
  },
  "datos": {
    "total_ingresos": 15000.00,
    "ingresos_por_mes": {
      "2024-08": 15000.00
    },
    "fuentes_ingreso": {
      "cuotas_mantenimiento": 12000.00,
      "multas": 500.00,
      "otros": 2500.00
    },
    "total_registros": 150
  },
  "total_registros": 150,
  "filtros_aplicados": {
    "fuente": "cuotas_mantenimiento"
  }
}
```

## Endpoints de Reportes de Seguridad

### 1. Generar Reporte de Seguridad

**POST** `/api/analytics/reportes-seguridad/generar_reporte/`

Genera un reporte de seguridad con análisis de eventos.

#### Body
```json
{
  "titulo": "Incidentes de Seguridad - Semana 35",
  "descripcion": "Análisis de eventos de seguridad",
  "tipo": "incidentes",
  "periodo": "semanal",
  "fecha_inicio": "2024-08-26T00:00:00Z",
  "fecha_fin": "2024-09-01T23:59:59Z",
  "filtros_aplicados": {
    "nivel_critico": true
  }
}
```

#### Respuesta Exitosa (201)
```json
{
  "id": 1,
  "titulo": "Incidentes de Seguridad - Semana 35",
  "tipo": "incidentes",
  "periodo": "semanal",
  "fecha_inicio": "2024-08-26T00:00:00Z",
  "fecha_fin": "2024-09-01T23:59:59Z",
  "fecha_generacion": "2024-09-01T11:00:00Z",
  "generado_por": 1,
  "generado_por_info": {
    "username": "admin",
    "role": "admin"
  },
  "datos": {
    "total_incidentes": 12,
    "incidentes_por_tipo": {
      "intento_fuerza": 3,
      "codigo_incorrecto": 8,
      "sospechoso": 1
    },
    "incidentes_resueltos": 11,
    "incidentes_pendientes": 1,
    "tiempo_respuesta_promedio": "5.2 minutos"
  },
  "total_eventos": 12,
  "eventos_criticos": 3,
  "alertas_generadas": 12,
  "filtros_aplicados": {
    "nivel_critico": true
  }
}
```

## Endpoints de Reportes de Uso de Áreas

### 1. Generar Reporte de Uso de Áreas

**POST** `/api/analytics/reportes-uso-areas/generar_reporte/`

Genera un reporte de uso de áreas comunes.

#### Body
```json
{
  "titulo": "Ocupación Piscina Verano 2024",
  "descripcion": "Análisis de uso de piscina",
  "area": "piscina",
  "periodo": "mensual",
  "metrica_principal": "ocupacion",
  "fecha_inicio": "2024-06-01",
  "fecha_fin": "2024-08-31",
  "filtros_aplicados": {
    "dias_semana": ["sabado", "domingo"]
  }
}
```

#### Respuesta Exitosa (201)
```json
{
  "id": 1,
  "titulo": "Ocupación Piscina Verano 2024",
  "area": "piscina",
  "periodo": "mensual",
  "metrica_principal": "ocupacion",
  "fecha_inicio": "2024-06-01",
  "fecha_fin": "2024-08-31",
  "fecha_generacion": "2024-09-01T11:15:00Z",
  "generado_por": 1,
  "generado_por_info": {
    "username": "admin",
    "role": "admin"
  },
  "datos": {
    "tasa_ocupacion_promedio": 68.5,
    "ocupacion_por_dia": {
      "lunes": 75.0,
      "martes": 70.0,
      "miercoles": 65.0,
      "jueves": 72.0,
      "viernes": 80.0,
      "sabado": 85.0,
      "domingo": 60.0
    },
    "ocupacion_por_hora": {
      "08:00": 30.0,
      "10:00": 50.0,
      "12:00": 70.0,
      "14:00": 85.0,
      "16:00": 90.0,
      "18:00": 95.0,
      "20:00": 80.0
    }
  },
  "total_reservas": 245,
  "horas_ocupacion": 1250.5,
  "tasa_ocupacion_promedio": 68.5,
  "filtros_aplicados": {
    "dias_semana": ["sabado", "domingo"]
  }
}
```

## Endpoints de Predicciones de Morosidad

### 1. Generar Predicción de Morosidad

**POST** `/api/analytics/predicciones-morosidad/generar_prediccion/`

Genera una predicción de morosidad usando IA.

#### Body
```json
{
  "titulo": "Predicción Morosidad Q4 2024",
  "descripcion": "Análisis predictivo de riesgo de morosidad",
  "modelo_usado": "random_forest",
  "periodo_predicho": "Próximos 3 meses",
  "datos_entrada": {
    "variables_historicas": true,
    "incluir_demografia": true,
    "periodo_analisis": "12_meses"
  },
  "parametros_modelo": {
    "n_estimators": 100,
    "max_depth": 10,
    "random_state": 42
  }
}
```

#### Respuesta Exitosa (201)
```json
{
  "id": 1,
  "titulo": "Predicción Morosidad Q4 2024",
  "modelo_usado": "random_forest",
  "nivel_confianza": "alto",
  "fecha_prediccion": "2024-09-01T11:30:00Z",
  "periodo_predicho": "Próximos 3 meses",
  "generado_por": 1,
  "generado_por_info": {
    "username": "admin",
    "role": "admin"
  },
  "datos_entrada": {
    "variables_historicas": true,
    "incluir_demografia": true,
    "periodo_analisis": "12_meses"
  },
  "resultados": {
    "predicciones_por_residente": [
      {
        "residente_id": 1,
        "riesgo_morosidad": "bajo",
        "probabilidad": 0.15
      },
      {
        "residente_id": 2,
        "riesgo_morosidad": "medio",
        "probabilidad": 0.65
      }
    ],
    "estadisticas_generales": {
      "riesgo_bajo": 30,
      "riesgo_medio": 12,
      "riesgo_alto": 8,
      "precision_modelo": 85.2
    },
    "factores_riesgo_identificados": [
      "Historial de pagos atrasados",
      "Cambios en ingresos declarados",
      "Aumento en uso de servicios"
    ]
  },
  "total_residentes_analizados": 50,
  "residentes_riesgo_alto": 8,
  "residentes_riesgo_medio": 12,
  "precision_modelo": 85.2,
  "riesgo_porcentaje": 40.0,
  "parametros_modelo": {
    "n_estimators": 100,
    "max_depth": 10,
    "random_state": 42
  },
  "metricas_evaluacion": {
    "accuracy": 0.852,
    "precision": 0.82,
    "recall": 0.79,
    "f1_score": 0.80,
    "auc_roc": 0.88
  }
}
```

## Códigos de Error

### Errores Comunes

#### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

#### 403 Forbidden
```json
{
  "error": "No tienes permisos para generar reportes financieros"
}
```

#### 400 Bad Request
```json
{
  "fecha_fin": ["La fecha de fin no puede ser anterior a la fecha de inicio"]
}
```

#### 404 Not Found
```json
{
  "detail": "No ReporteFinanciero matches the given query."
}
```

## Rate Limiting

- **Generación de reportes**: Máximo 10 reportes por hora por usuario
- **Predicciones IA**: Máximo 5 predicciones por día por usuario
- **Listados**: Sin límite específico

## Formatos de Respuesta

### Paginación
Los endpoints de listado soportan paginación:

```
GET /api/analytics/reportes-financieros/?page=1&page_size=20
```

### Filtros Avanzados
Múltiples filtros pueden combinarse:

```
GET /api/analytics/reportes-financieros/?tipo=ingresos&periodo=mensual&fecha_generacion_after=2024-01-01
```

### Ordenamiento
Ordenar por cualquier campo:

```
GET /api/analytics/reportes-financieros/?ordering=-fecha_generacion
```