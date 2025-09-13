# 🚀 API Reference - Módulo Financiero
## Referencia Rápida de Endpoints

---

## 🔐 Autenticación
Todos los endpoints requieren autenticación con token:
```
Authorization: Token <tu_token_aqui>
Content-Type: application/json
```

---

## 📋 Conceptos Financieros

### GET `/api/finances/conceptos/`
Listar todos los conceptos financieros

**Permisos**: Todos los usuarios autenticados

**Filtros opcionales**:
- `?tipo=cuota_mensual` - Filtrar por tipo
- `?estado=activo` - Filtrar por estado  
- `?vigente=true` - Solo conceptos vigentes

**Respuesta**:
```json
{
  "count": 6,
  "results": [
    {
      "id": 1,
      "nombre": "Cuota de Mantenimiento Mensual",
      "tipo": "cuota_mensual",
      "tipo_display": "Cuota Mensual",
      "monto": "180.00",
      "estado": "activo",
      "esta_vigente": true
    }
  ]
}
```

### POST `/api/finances/conceptos/`
Crear nuevo concepto financiero

**Permisos**: Solo administradores

**Body**:
```json
{
  "nombre": "Multa por Ruido",
  "descripcion": "Multa aplicada por ruido excesivo",
  "tipo": "multa_ruido",
  "monto": "50.00",
  "es_recurrente": false,
  "aplica_a_todos": false,
  "fecha_vigencia_desde": "2025-09-13"
}
```

### GET `/api/finances/conceptos/{id}/`
Obtener detalle de un concepto

**Respuesta**:
```json
{
  "id": 1,
  "nombre": "Cuota de Mantenimiento Mensual",
  "descripcion": "Cuota mensual para mantenimiento",
  "tipo": "cuota_mensual",
  "monto": "180.00",
  "estado": "activo",
  "fecha_vigencia_desde": "2025-01-01",
  "fecha_vigencia_hasta": "2025-12-31",
  "es_recurrente": true,
  "aplica_a_todos": true,
  "esta_vigente": true,
  "creado_por_info": {
    "id": 1,
    "username": "admin",
    "nombre_completo": "Admin Sistema"
  },
  "fecha_creacion": "2025-09-13T06:15:30Z"
}
```

### GET `/api/finances/conceptos/vigentes/`
Obtener solo conceptos vigentes

**Respuesta**: Array de conceptos activos y en periodo de vigencia

### POST `/api/finances/conceptos/{id}/toggle_estado/`
Activar/desactivar un concepto

**Permisos**: Solo administradores

**Respuesta**:
```json
{
  "mensaje": "Concepto Multa por Ruido ahora está Inactivo",
  "concepto": { /* datos del concepto */ }
}
```

---

## 💰 Cargos Financieros

### GET `/api/finances/cargos/`
Listar cargos financieros

**Permisos**: 
- Administradores: Ven todos los cargos
- Residentes: Solo sus propios cargos

**Filtros opcionales**:
- `?estado=pendiente` - Filtrar por estado
- `?residente=1` - Filtrar por residente (solo admin)
- `?concepto=1` - Filtrar por concepto
- `?vencidos=true` - Solo cargos vencidos

**Respuesta**:
```json
{
  "count": 8,
  "results": [
    {
      "id": 1,
      "concepto_nombre": "Cuota de Mantenimiento Mensual",
      "concepto_tipo": "cuota_mensual",
      "residente_username": "carlos",
      "residente_nombre": "Carlos Rodriguez",
      "monto": "180.00",
      "estado": "pendiente",
      "estado_display": "Pendiente",
      "fecha_aplicacion": "2025-09-13",
      "fecha_vencimiento": "2025-10-13",
      "esta_vencido": false
    }
  ]
}
```

### POST `/api/finances/cargos/`
Aplicar nuevo cargo a un residente

**Permisos**: Solo administradores

**Body**:
```json
{
  "concepto": 1,
  "residente": 3,
  "monto": "180.00",
  "fecha_vencimiento": "2025-10-13",
  "observaciones": "Cargo mensual aplicado"
}
```

**Respuesta**:
```json
{
  "id": 9,
  "concepto_info": {
    "id": 1,
    "nombre": "Cuota de Mantenimiento Mensual"
  },
  "residente_info": {
    "id": 3,
    "username": "carlos",
    "nombre_completo": "Carlos Rodriguez"
  },
  "monto": "180.00",
  "estado": "pendiente",
  "fecha_aplicacion": "2025-09-13",
  "fecha_vencimiento": "2025-10-13",
  "dias_para_vencimiento": 30
}
```

### GET `/api/finances/cargos/mis_cargos/`
Obtener cargos del usuario actual

**Permisos**: Todos los usuarios autenticados

**Respuesta**: Array de cargos del usuario actual

### POST `/api/finances/cargos/{id}/pagar/`
Marcar un cargo como pagado

**Permisos**: Administradores o el propio residente

**Body**:
```json
{
  "referencia_pago": "PAGO-2025-001",
  "observaciones": "Pago procesado en línea"
}
```

**Respuesta**:
```json
{
  "mensaje": "Cargo pagado exitosamente",
  "cargo": {
    "id": 1,
    "estado": "pagado",
    "fecha_pago": "2025-09-13T06:33:59Z",
    "referencia_pago": "PAGO-2025-001"
  }
}
```

### GET `/api/finances/cargos/vencidos/`
Obtener cargos vencidos

**Permisos**: Solo administradores

**Respuesta**: Array de cargos con estado pendiente y fecha de vencimiento pasada

### GET `/api/finances/cargos/resumen/{user_id}/`
Obtener resumen financiero de un residente

**Permisos**: Administradores o el propio usuario

**Respuesta**:
```json
{
  "residente_info": {
    "id": 3,
    "username": "carlos",
    "nombre_completo": "Carlos Rodriguez"
  },
  "total_pendiente": "360.00",
  "total_vencido": "0.00",
  "total_pagado_mes": "180.00",
  "cantidad_cargos_pendientes": 2,
  "cantidad_cargos_vencidos": 0,
  "ultimo_pago": "2025-09-13T06:33:59Z"
}
```

---

## 📊 Estadísticas

### GET `/api/finances/estadisticas/`
Obtener estadísticas financieras generales

**Permisos**: Solo administradores

**Respuesta**:
```json
{
  "total_conceptos_activos": 7,
  "total_cargos_pendientes": 5,
  "monto_total_pendiente": "910.00",
  "total_cargos_vencidos": 0,
  "monto_total_vencido": "0.00",
  "total_pagos_mes_actual": "510.00",
  "conceptos_mas_aplicados": [
    {
      "concepto__nombre": "Cuota de Mantenimiento Mensual",
      "concepto__tipo": "cuota_mensual",
      "cantidad": 4
    }
  ]
}
```

---

## 🚫 Códigos de Error Comunes

### 400 - Bad Request
```json
{
  "error": "Datos inválidos",
  "monto": ["El monto debe ser mayor a 0"],
  "fecha_vencimiento": ["La fecha de vencimiento no puede ser anterior a la fecha de aplicación"]
}
```

### 401 - Unauthorized
```json
{
  "detail": "Las credenciales de autenticación no se proveyeron."
}
```

### 403 - Forbidden
```json
{
  "error": "No tiene permisos para realizar esta acción"
}
```

### 404 - Not Found
```json
{
  "detail": "No encontrado."
}
```

---

## 📝 Tipos de Datos

### Tipos de Concepto
- `cuota_mensual` - Cuota Mensual
- `cuota_extraordinaria` - Cuota Extraordinaria  
- `multa_ruido` - Multa por Ruido
- `multa_areas_comunes` - Multa Áreas Comunes
- `multa_estacionamiento` - Multa Estacionamiento
- `multa_mascota` - Multa por Mascota
- `otros` - Otros

### Estados de Concepto
- `activo` - Activo
- `inactivo` - Inactivo
- `suspendido` - Suspendido

### Estados de Cargo
- `pendiente` - Pendiente
- `pagado` - Pagado
- `vencido` - Vencido
- `cancelado` - Cancelado

---

## 🔧 Ejemplos de Uso Rápido

### JavaScript/React
```javascript
// Obtener mis cargos
fetch('http://127.0.0.1:8000/api/finances/cargos/mis_cargos/', {
  headers: { 'Authorization': `Token ${token}` }
})
.then(res => res.json())
.then(data => console.log('Mis cargos:', data));

// Pagar un cargo
fetch('http://127.0.0.1:8000/api/finances/cargos/1/pagar/', {
  method: 'POST',
  headers: {
    'Authorization': `Token ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    referencia_pago: 'PAGO-001',
    observaciones: 'Pago en línea'
  })
})
.then(res => res.json())
.then(data => console.log('Pago procesado:', data));
```

### curl
```bash
# Listar conceptos vigentes
curl -H "Authorization: Token YOUR_TOKEN" \
  "http://127.0.0.1:8000/api/finances/conceptos/vigentes/"

# Crear concepto (admin)
curl -X POST \
  -H "Authorization: Token YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"nombre":"Nueva Multa","tipo":"multa_ruido","monto":"25.00"}' \
  "http://127.0.0.1:8000/api/finances/conceptos/"

# Pagar cargo
curl -X POST \
  -H "Authorization: Token YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"referencia_pago":"PAGO-123"}' \
  "http://127.0.0.1:8000/api/finances/cargos/1/pagar/"
```

### Python
```python
import requests

token = "your_token_here"
headers = {"Authorization": f"Token {token}"}

# Obtener mis cargos
response = requests.get(
    "http://127.0.0.1:8000/api/finances/cargos/mis_cargos/",
    headers=headers
)
cargos = response.json()

# Pagar cargo
pago_data = {
    "referencia_pago": "PAGO-001",
    "observaciones": "Pago procesado"
}
response = requests.post(
    "http://127.0.0.1:8000/api/finances/cargos/1/pagar/",
    json=pago_data,
    headers=headers
)
resultado = response.json()
```

---

## 🎯 Casos de Uso Comunes

### Para Administradores Web (React)
1. **Dashboard financiero**: GET `/estadisticas/`
2. **Gestionar conceptos**: CRUD en `/conceptos/`
3. **Aplicar cargos**: POST `/cargos/`
4. **Ver todos los cargos**: GET `/cargos/`
5. **Procesar pagos manuales**: POST `/cargos/{id}/pagar/`

### Para Residentes Móvil (Flutter)
1. **Ver mis cargos**: GET `/cargos/mis_cargos/`
2. **Ver mi resumen**: GET `/cargos/resumen/{user_id}/`
3. **Pagar cargo**: POST `/cargos/{id}/pagar/`
4. **Ver conceptos**: GET `/conceptos/vigentes/`

### Para Seguridad (Flutter)
1. **Consultar conceptos**: GET `/conceptos/vigentes/`
2. **Ver información general**: Solo endpoints de lectura

---

**🔄 Actualizado**: 13 de septiembre de 2025  
**📊 Base URL**: `http://127.0.0.1:8000/api/finances/`  
**🔐 Autenticación**: Token requerido en todos los endpoints