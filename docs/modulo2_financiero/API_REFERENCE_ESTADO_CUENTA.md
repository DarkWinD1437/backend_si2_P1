# API Reference - Estado de Cuenta

## Endpoint Principal

### `GET /api/finances/cargos/estado_cuenta/`

Consultar estado de cuenta completo de un residente.

#### Descripción
Endpoint que proporciona una vista integral del estado financiero de un residente, incluyendo cargos pendientes, vencidos, historial de pagos, alertas y resúmenes estadísticos.

#### Parámetros de Consulta

| Parámetro | Tipo | Requerido | Descripción |
|-----------|------|-----------|-------------|
| `residente` | integer | No | ID del residente (solo para administradores) |

#### Headers Requeridos

| Header | Valor | Descripción |
|--------|-------|-------------|
| `Authorization` | `Token {token}` | Token de autenticación del usuario |
| `Content-Type` | `application/json` | Tipo de contenido |

#### Códigos de Respuesta

| Código | Descripción |
|--------|-------------|
| `200` | Estado de cuenta obtenido exitosamente |
| `401` | Token de autenticación inválido o faltante |
| `403` | Sin permisos para consultar el residente especificado |
| `404` | Residente no encontrado (cuando se especifica ID) |
| `500` | Error interno del servidor |

## Estructura de Respuesta Detallada

### Objeto Principal

```json
{
  "residente_info": { /* ResidenteInfo */ },
  "fecha_consulta": "string (date)",
  "resumen_general": { /* ResumenGeneral */ },
  "cargos_pendientes": [ /* Array de CargoFinanciero */ ],
  "cargos_vencidos": [ /* Array de CargoFinanciero */ ],
  "historial_pagos": [ /* Array de CargoFinanciero */ ],
  "desglose_por_tipo": [ /* Array de DesgloseTipo */ ],
  "proximo_vencimiento": { /* ProximoVencimiento */ },
  "ultimo_pago": { /* UltimoPago */ },
  "alertas": [ /* Array de Alerta */ ]
}
```

### ResidenteInfo

```json
{
  "id": "integer",
  "username": "string",
  "email": "string",
  "nombre_completo": "string",
  "first_name": "string",
  "last_name": "string"
}
```

### ResumenGeneral

```json
{
  "total_pendiente": "decimal (10,2)",
  "total_vencido": "decimal (10,2)",
  "total_al_dia": "decimal (10,2)",
  "cantidad_cargos_pendientes": "integer",
  "cantidad_cargos_vencidos": "integer", 
  "total_pagado_mes_actual": "decimal (10,2)",
  "total_pagado_6_meses": "decimal (12,2)"
}
```

### CargoFinanciero

```json
{
  "id": "integer",
  "concepto_nombre": "string",
  "concepto_tipo": "string",
  "residente_username": "string",
  "residente_nombre": "string",
  "monto": "decimal (10,2)",
  "estado": "string",
  "estado_display": "string",
  "fecha_aplicacion": "string (date)",
  "fecha_vencimiento": "string (date)",
  "esta_vencido": "boolean"
}
```

### DesgloseTipo

```json
{
  "concepto__tipo": "string",
  "concepto__nombre": "string", 
  "cantidad": "integer",
  "total": "decimal (10,2)"
}
```

### ProximoVencimiento

```json
{
  "cargo": { /* CargoFinanciero o null */ },
  "fecha": "string (date) | null",
  "dias_restantes": "integer | null"
}
```

### UltimoPago

```json
{
  "cargo": { /* CargoFinanciero o null */ },
  "fecha": "string (datetime) | null",
  "hace_dias": "integer | null"
}
```

### Alerta

```json
{
  "tipo": "string",
  "severidad": "string (baja|media|alta)",
  "titulo": "string",
  "mensaje": "string",
  "accion": "string"
}
```

## Ejemplos de Uso

### Ejemplo 1: Consulta por Residente

**Request:**
```bash
curl -X GET "http://localhost:8000/api/finances/cargos/estado_cuenta/" \
     -H "Authorization: Token abc123def456" \
     -H "Content-Type: application/json"
```

**Response (200):**
```json
{
  "residente_info": {
    "id": 5,
    "username": "resident1",
    "email": "resident1@condominio.com",
    "nombre_completo": "María González",
    "first_name": "María",
    "last_name": "González"
  },
  "fecha_consulta": "2024-12-19",
  "resumen_general": {
    "total_pendiente": "175000.00",
    "total_vencido": "25000.00",
    "total_al_dia": "150000.00", 
    "cantidad_cargos_pendientes": 2,
    "cantidad_cargos_vencidos": 1,
    "total_pagado_mes_actual": "0.00",
    "total_pagado_6_meses": "450000.00"
  },
  "cargos_pendientes": [
    {
      "id": 25,
      "concepto_nombre": "Cuota de Mantenimiento Mensual",
      "concepto_tipo": "cuota_mensual",
      "residente_username": "resident1", 
      "residente_nombre": "María González",
      "monto": "150000.00",
      "estado": "pendiente",
      "estado_display": "Pendiente",
      "fecha_aplicacion": "2024-12-01",
      "fecha_vencimiento": "2024-12-15",
      "esta_vencido": false
    }
  ],
  "cargos_vencidos": [
    {
      "id": 22,
      "concepto_nombre": "Multa por Parqueo en Lugar Prohibido",
      "concepto_tipo": "multa_estacionamiento",
      "residente_username": "resident1",
      "residente_nombre": "María González", 
      "monto": "25000.00",
      "estado": "vencido",
      "estado_display": "Vencido",
      "fecha_aplicacion": "2024-11-20",
      "fecha_vencimiento": "2024-12-05",
      "esta_vencido": true
    }
  ],
  "historial_pagos": [
    {
      "id": 18,
      "concepto_nombre": "Cuota de Mantenimiento Mensual",
      "concepto_tipo": "cuota_mensual",
      "residente_username": "resident1",
      "residente_nombre": "María González",
      "monto": "150000.00", 
      "estado": "pagado",
      "estado_display": "Pagado",
      "fecha_aplicacion": "2024-11-01",
      "fecha_vencimiento": "2024-11-15",
      "esta_vencido": false
    }
  ],
  "desglose_por_tipo": [
    {
      "concepto__tipo": "cuota_mensual",
      "concepto__nombre": "Cuota de Mantenimiento Mensual",
      "cantidad": 1,
      "total": "150000.00"
    },
    {
      "concepto__tipo": "multa_estacionamiento", 
      "concepto__nombre": "Multa por Parqueo en Lugar Prohibido",
      "cantidad": 1,
      "total": "25000.00"
    }
  ],
  "proximo_vencimiento": {
    "cargo": {
      "id": 25,
      "concepto_nombre": "Cuota de Mantenimiento Mensual",
      "concepto_tipo": "cuota_mensual",
      "residente_username": "resident1",
      "residente_nombre": "María González",
      "monto": "150000.00",
      "estado": "pendiente",
      "estado_display": "Pendiente", 
      "fecha_aplicacion": "2024-12-01",
      "fecha_vencimiento": "2024-12-15",
      "esta_vencido": false
    },
    "fecha": "2024-12-15",
    "dias_restantes": 4
  },
  "ultimo_pago": {
    "cargo": {
      "id": 18,
      "concepto_nombre": "Cuota de Mantenimiento Mensual",
      "concepto_tipo": "cuota_mensual",
      "residente_username": "resident1",
      "residente_nombre": "María González", 
      "monto": "150000.00",
      "estado": "pagado",
      "estado_display": "Pagado",
      "fecha_aplicacion": "2024-11-01",
      "fecha_vencimiento": "2024-11-15",
      "esta_vencido": false
    },
    "fecha": "2024-11-12T14:30:00Z",
    "hace_dias": 37
  },
  "alertas": [
    {
      "tipo": "vencido",
      "severidad": "alta",
      "titulo": "Tiene 1 cargo(s) vencido(s)",
      "mensaje": "Total vencido: $25000.00. Se recomienda realizar el pago lo antes posible.",
      "accion": "Pagar cargos vencidos"
    },
    {
      "tipo": "vencimiento_proximo",
      "severidad": "media",
      "titulo": "Cargo próximo a vencer",
      "mensaje": "Cuota de Mantenimiento Mensual vence en 4 día(s)",
      "accion": "Revisar y programar pago"
    }
  ]
}
```

### Ejemplo 2: Consulta por Administrador

**Request:**
```bash
curl -X GET "http://localhost:8000/api/finances/cargos/estado_cuenta/?residente=7" \
     -H "Authorization: Token admin_token_xyz" \
     -H "Content-Type: application/json"
```

**Response (200):** Similar al anterior, pero con información del residente ID 7.

### Ejemplo 3: Error de Permisos

**Request:**
```bash
curl -X GET "http://localhost:8000/api/finances/cargos/estado_cuenta/?residente=8" \
     -H "Authorization: Token resident_token_abc" \
     -H "Content-Type: application/json"
```

**Response (403):**
```json
{
  "error": "No tiene permisos para consultar el estado de cuenta de otros residentes"
}
```

### Ejemplo 4: Token Inválido

**Request:**
```bash
curl -X GET "http://localhost:8000/api/finances/cargos/estado_cuenta/" \
     -H "Authorization: Token invalid_token" \
     -H "Content-Type: application/json"
```

**Response (401):**
```json
{
  "detail": "Invalid token."
}
```

## Tipos de Conceptos Financieros

| Tipo | Código | Descripción |
|------|--------|-------------|
| Cuota Mensual | `cuota_mensual` | Cuota regular mensual de mantenimiento |
| Cuota Extraordinaria | `cuota_extraordinaria` | Cuotas especiales para proyectos |
| Multa Ruido | `multa_ruido` | Infracciones por ruido nocturno |
| Multa Áreas Comunes | `multa_areas_comunes` | Mal uso de áreas comunes |
| Multa Estacionamiento | `multa_estacionamiento` | Parqueo en lugares prohibidos |
| Multa Mascota | `multa_mascota` | Mascotas sin registro |
| Otros | `otros` | Otros conceptos diversos |

## Estados de Cargos

| Estado | Código | Descripción |
|--------|--------|-------------|
| Pendiente | `pendiente` | Cargo aplicado, pendiente de pago |
| Pagado | `pagado` | Cargo saldado completamente |
| Vencido | `vencido` | Cargo pendiente que superó fecha límite |
| Cancelado | `cancelado` | Cargo anulado por administración |

## Tipos de Alertas

| Tipo | Severidad | Condición |
|------|-----------|-----------|
| `vencido` | Alta | Existen cargos vencidos |
| `vencimiento_proximo` | Media/Alta | Cargo vence en ≤ 7 días |

## Validaciones y Reglas de Negocio

### Permisos
- **Residentes**: Solo pueden consultar su propio estado de cuenta
- **Administradores**: Pueden consultar cualquier residente usando `?residente=ID`
- **Sin parámetro `residente`**: Consulta el estado de cuenta del usuario autenticado

### Cálculos
- **Total al día**: `total_pendiente - total_vencido`
- **Días restantes**: Diferencia entre `fecha_vencimiento` y fecha actual
- **Hace días**: Diferencia entre fecha actual y `fecha_pago`
- **Está vencido**: `fecha_vencimiento < fecha_actual AND estado = 'pendiente'`

### Límites
- **Historial de pagos**: Máximo 20 registros más recientes
- **Período historial**: Últimos 6 meses para estadísticas
- **Alertas vencimiento**: Se generan con 7 días de anticipación

## Optimizaciones

### Base de Datos
- Uso de `select_related()` para evitar N+1 queries
- Agregaciones con `Sum()` y `Count()` ejecutadas en DB
- Índices en campos de consulta frecuente (`residente`, `estado`, `fecha_vencimiento`)

### Rendimiento
- Cálculos en memoria para campos derivados
- Filtrado por fechas optimizado
- Respuestas estructuradas para minimizar procesamiento en frontend