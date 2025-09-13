# MÓDULO 2: GESTIÓN FINANCIERA BÁSICA
## T3: PAGAR CUOTA EN LÍNEA - DOCUMENTACIÓN COMPLETA

### 🎯 OBJETIVO
Implementar un sistema completo de pagos en línea que permita a los residentes pagar sus cuotas desde la aplicación móvil y a los administradores procesar pagos presenciales en nombre de los residentes.

---

## 📋 ENDPOINTS IMPLEMENTADOS

### 1. **POST /api/finances/cargos/{id}/pagar/**
Procesar pago de un cargo específico.

#### **Permisos:**
- **Residentes**: Solo pueden pagar sus propios cargos con método 'online'
- **Administradores**: Pueden pagar cualquier cargo con cualquier método

#### **Parámetros de URL:**
- `id` (required): ID del cargo a pagar

#### **Body Request:**
```json
{
    "referencia_pago": "TXN_20250913_040620",
    "observaciones": "Pago realizado desde app móvil",
    "metodo_pago": "online",
    "monto_pagado": 150.00,
    "confirmar_pago": true
}
```

#### **Campos del Request:**

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `referencia_pago` | string | No | Referencia del pago (voucher, transacción, etc.) |
| `observaciones` | string | No | Observaciones adicionales sobre el pago |
| `metodo_pago` | string | No | Método: `online`, `efectivo`, `transferencia`, `cheque`, `tarjeta` |
| `monto_pagado` | decimal | No | Monto pagado (por defecto el monto del cargo) |
| `confirmar_pago` | boolean | Sí | Confirmación de procesamiento |

#### **Métodos de Pago por Rol:**

| Método | Residentes | Administradores |
|--------|------------|-----------------|
| `online` | ✅ | ✅ |
| `efectivo` | ❌ | ✅ |
| `transferencia` | ❌ | ✅ |
| `cheque` | ❌ | ✅ |
| `tarjeta` | ❌ | ✅ |

#### **Response Exitoso (200):**
```json
{
    "exito": true,
    "mensaje": "Pago procesado exitosamente",
    "pago_info": {
        "cargo_id": 10,
        "residente": "prueba2",
        "concepto": "Cuota de Mantenimiento Enero 2025",
        "monto_original": 150.0,
        "monto_pagado": 150.0,
        "fecha_pago": "2025-09-13T08:06:20.195587Z",
        "referencia_pago": "TXN_20250913_040620",
        "procesado_por": "prueba2",
        "es_pago_admin": false,
        "estado_anterior": "pendiente",
        "estado_actual": "Pagado"
    },
    "cargo": {
        "id": 10,
        "concepto_info": {
            "id": 1,
            "nombre": "Cuota de Mantenimiento Enero 2025",
            "tipo": "cuota_mensual",
            "monto": "150.00"
        },
        "residente_info": {
            "id": 10,
            "username": "prueba2",
            "nombre_completo": "pruebin pruebote"
        },
        "monto": "150.00",
        "estado": "pagado",
        "estado_display": "Pagado",
        "fecha_aplicacion": "2025-08-24",
        "fecha_vencimiento": "2025-09-23",
        "fecha_pago": "2025-09-13T08:06:20.195587Z",
        "referencia_pago": "TXN_20250913_040620",
        "observaciones": "Pago realizado desde app móvil"
    }
}
```

#### **Errores Comunes:**

**400 - Bad Request:**
```json
{
    "error": "No se puede pagar un cargo en estado \"Pagado\"",
    "estado_actual": "pagado",
    "cargo_id": 10
}
```

**403 - Forbidden:**
```json
{
    "error": "No tiene permisos para pagar este cargo"
}
```

**Validaciones del Serializer:**
```json
{
    "confirmar_pago": ["Debe confirmar que desea procesar el pago"],
    "metodo_pago": ["Los residentes solo pueden usar pago en línea"],
    "monto_pagado": ["El monto pagado no puede ser menor al monto del cargo ($150.00)"]
}
```

---

### 2. **GET /api/finances/cargos/pagos/**
Consultar historial de pagos realizados.

#### **Permisos:**
- **Residentes**: Solo ven sus propios pagos
- **Administradores**: Ven todos los pagos, pueden filtrar por residente

#### **Query Parameters:**

| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| `residente` | int | ID del residente (solo admins) |
| `fecha_desde` | date | Fecha inicial (formato: YYYY-MM-DD) |
| `fecha_hasta` | date | Fecha final (formato: YYYY-MM-DD) |
| `concepto` | int | ID del concepto financiero |

#### **Ejemplo de Request:**
```
GET /api/finances/cargos/pagos/?fecha_desde=2025-09-01&fecha_hasta=2025-09-30&residente=10
```

#### **Response Exitoso (200):**
```json
{
    "pagos": [
        {
            "id": 12,
            "concepto_nombre": "Cuota Extraordinaria - Mejoras",
            "concepto_tipo": "cuota_extraordinaria",
            "residente_username": "prueba2",
            "residente_nombre": "pruebin pruebote",
            "monto": "75000.00",
            "estado": "pagado",
            "estado_display": "Pagado",
            "fecha_aplicacion": "2025-08-24",
            "fecha_vencimiento": "2025-09-28",
            "esta_vencido": false
        }
    ],
    "estadisticas": {
        "total_pagos": 3,
        "monto_total": 75300.0,
        "periodo_consultado": {
            "fecha_desde": "2025-09-01",
            "fecha_hasta": "2025-09-30"
        }
    }
}
```

#### **Paginación:**
El endpoint soporta paginación automática:
```json
{
    "count": 50,
    "next": "http://localhost:8000/api/finances/cargos/pagos/?page=2",
    "previous": null,
    "results": [...],
    "estadisticas": {...}
}
```

---

## 🔒 VALIDACIONES DE SEGURIDAD

### **1. Validaciones de Estado**
- ✅ Solo se pueden pagar cargos en estado "pendiente"
- ✅ Cargos ya pagados, cancelados o anulados son rechazados
- ✅ Verificación de integridad del estado del cargo

### **2. Validaciones de Permisos**
- ✅ Residentes solo pueden pagar sus propios cargos
- ✅ Administradores pueden pagar cargos de cualquier residente
- ✅ Validación de rol y autorización en cada request

### **3. Validaciones de Método de Pago**
- ✅ Residentes limitados a pagos 'online' únicamente
- ✅ Administradores pueden usar todos los métodos disponibles
- ✅ Validación de referencia requerida para transferencias y cheques

### **4. Validaciones de Monto**
- ✅ Monto debe ser mayor a 0
- ✅ Monto no puede ser menor al monto del cargo
- ✅ Para cargos vencidos, se valida monto con recargo (si aplica)
- ✅ Validación de precisión decimal (2 lugares)

### **5. Validaciones de Negocio**
- ✅ Confirmación obligatoria de pago (`confirmar_pago: true`)
- ✅ Prevención de pagos duplicados
- ✅ Registro de auditoría completo (quien procesó el pago)

---

## 💳 CASOS DE USO

### **Caso 1: Pago en Línea por Residente**

**Flujo:**
1. Residente consulta sus cargos pendientes
2. Selecciona cargo a pagar
3. Confirma pago con método 'online'
4. Sistema procesa y actualiza estado
5. Se genera referencia automática
6. Estado de cuenta se actualiza inmediatamente

**Request:**
```bash
POST /api/finances/cargos/10/pagar/
Authorization: Token 1516f052537c3d7c9d18...

{
    "referencia_pago": "TXN_20250913_040620",
    "observaciones": "Pago desde app móvil",
    "metodo_pago": "online",
    "confirmar_pago": true
}
```

### **Caso 2: Pago Presencial por Administrador**

**Flujo:**
1. Residente llega a oficina administrativa
2. Admin busca cargos pendientes del residente
3. Procesa pago con método presencial
4. Registra referencia (voucher/recibo)
5. Sistema marca diferencia (pago procesado por admin)
6. Se notifica al residente (futuro)

**Request:**
```bash
POST /api/finances/cargos/12/pagar/
Authorization: Token 24dab09045b5d1dabb12...

{
    "referencia_pago": "VOUCHER_20250913_040620",
    "observaciones": "Pago en efectivo - oficina administrativa",
    "metodo_pago": "efectivo",
    "confirmar_pago": true
}
```

### **Caso 3: Consulta de Historial**

**Flujo:**
1. Usuario consulta historial de pagos
2. Aplica filtros opcionales (fechas, conceptos)
3. Sistema devuelve pagos paginados
4. Incluye estadísticas del período

**Request:**
```bash
GET /api/finances/cargos/pagos/?fecha_desde=2025-09-01
Authorization: Token 1516f052537c3d7c9d18...
```

---

## 🔄 INTEGRACIÓN CON OTROS MÓDULOS

### **1. Estado de Cuenta (T2)**
- ✅ Los pagos se reflejan inmediatamente en `/api/finances/cargos/estado_cuenta/`
- ✅ Actualización de totales pendientes, vencidos y pagados
- ✅ Cálculo automático de último pago y estadísticas

### **2. Notificaciones (Futuro)**
- 📧 Confirmación de pago por email
- 📱 Notificación push a app móvil
- 🏢 Notificación a admin en pagos presenciales

### **3. Reportes Financieros (Futuro)**
- 📊 Inclusión en reportes de ingresos
- 📈 Estadísticas de métodos de pago
- 💰 Conciliación bancaria

---

## 🧪 PRUEBAS IMPLEMENTADAS

### **Script de Pruebas: `test_pagos_completo.py`**

**Casos Validados:**
1. ✅ Login de admin y residente
2. ✅ Obtención de cargos pendientes
3. ✅ Validaciones de seguridad (confirmación, método de pago)
4. ✅ Pago exitoso por residente
5. ✅ Prevención de pagos duplicados
6. ✅ Pago por admin en nombre de residente
7. ✅ Historial de pagos con estadísticas
8. ✅ Integración con estado de cuenta

**Resultados de Pruebas:**
```
✅ Pago en línea por residentes
✅ Pago presencial por administradores  
✅ Validaciones de seguridad y negocio
✅ Historial completo de pagos
✅ Integración con estado de cuenta
✅ Múltiples métodos de pago
✅ Referencias y observaciones
✅ Control de permisos por roles
```

---

## 🛠️ IMPLEMENTACIÓN TÉCNICA

### **Modelos Involucrados:**
- `CargoFinanciero`: Almacena los cargos y su estado de pago
- `ConceptoFinanciero`: Define tipos de cargos/cuotas
- `User`: Sistema de usuarios con roles

### **Métodos del Modelo:**
```python
def marcar_como_pagado(self, referencia_pago='', usuario_proceso=None):
    """Marca el cargo como pagado y registra información de auditoría"""
    self.estado = EstadoCargo.PAGADO
    self.fecha_pago = timezone.now()
    self.referencia_pago = referencia_pago
    if usuario_proceso:
        self.observaciones += f"\nProcesado por: {usuario_proceso.username}"
    self.save()
```

### **Serializers:**
- `PagarCargoSerializer`: Validación de datos de pago
- `CargoFinancieroSerializer`: Respuesta completa del cargo
- `CargoFinancieroListSerializer`: Lista de pagos en historial

### **ViewSets y Actions:**
- `CargoFinancieroViewSet.pagar()`: Procesamiento de pagos
- `CargoFinancieroViewSet.pagos()`: Historial de pagos

---

## 📱 INTEGRACIÓN CON FLUTTER

### **Flujo Recomendado para App Móvil:**

1. **Pantalla de Estado de Cuenta:**
   ```dart
   GET /api/finances/cargos/estado_cuenta/
   // Mostrar cargos pendientes con botón "Pagar"
   ```

2. **Pantalla de Pago:**
   ```dart
   // Mostrar detalles del cargo
   // Formulario de confirmación
   // Botón "Procesar Pago"
   ```

3. **Procesamiento de Pago:**
   ```dart
   POST /api/finances/cargos/{id}/pagar/
   {
     "referencia_pago": "generada_por_app",
     "observaciones": "Pago desde app móvil",
     "metodo_pago": "online",
     "confirmar_pago": true
   }
   ```

4. **Confirmación:**
   ```dart
   // Mostrar información del pago
   // Actualizar estado de cuenta
   // Opción de ver historial
   ```

### **Manejo de Errores en Flutter:**
```dart
if (response.statusCode == 400) {
  // Mostrar errores de validación
  // Permitir corrección de datos
} else if (response.statusCode == 403) {
  // Error de permisos
  // Redirigir a login o mostrar mensaje
}
```

---

## 📊 ESTADÍSTICAS Y MÉTRICAS

### **Datos Disponibles:**
- Total de pagos realizados
- Monto total pagado por período
- Métodos de pago más utilizados
- Tiempo promedio entre aplicación y pago de cargo
- Pagos procesados por administradores vs residentes

### **Consultas Optimizadas:**
- Índices en fecha_pago, estado, residente_id
- Consultas agregadas para estadísticas
- Paginación para listas grandes

---

## 🚀 PRÓXIMAS MEJORAS

### **Funcionalidades Sugeridas:**
1. **Pagos Parciales**: Permitir abonos a cuenta
2. **Planes de Pago**: Facilidades de pago en cuotas
3. **Descuentos**: Por pronto pago o usuario frecuente
4. **Integración Bancaria**: API de bancos para validación automática
5. **Códigos QR**: Para facilitar pagos presenciales
6. **Notificaciones**: Email/SMS de confirmación
7. **Recibos PDF**: Generación automática de comprobantes

### **Mejoras Técnicas:**
1. **Webhooks**: Para notificar pagos a sistemas externos
2. **Logs Detallados**: Auditoría completa de transacciones
3. **Cache**: Para mejorar rendimiento de consultas
4. **Backup**: Respaldo automático de datos financieros

---

## ✅ RESUMEN DE IMPLEMENTACIÓN

### **Estado: COMPLETAMENTE FUNCIONAL ✅**

**Endpoints Implementados:**
- ✅ POST `/api/finances/cargos/{id}/pagar/` - Procesar pago
- ✅ GET `/api/finances/cargos/pagos/` - Historial de pagos

**Funcionalidades Validadas:**
- ✅ Pagos en línea para residentes
- ✅ Pagos presenciales para administradores
- ✅ Validaciones completas de seguridad
- ✅ Historial con filtros y estadísticas
- ✅ Integración con estado de cuenta
- ✅ Múltiples métodos de pago
- ✅ Sistema de referencias y observaciones
- ✅ Control de permisos por roles

**Archivos Clave:**
- `backend/apps/finances/views.py` - Lógica de endpoints
- `backend/apps/finances/serializers.py` - Validaciones
- `test_pagos_completo.py` - Pruebas automatizadas
- `docs/modulo2_financiero/T3_PAGAR_CUOTA_ONLINE.md` - Esta documentación

**Listo para:**
- 🚀 Integración con frontend Flutter
- 📱 Despliegue en producción
- 🔄 Extensión con nuevas funcionalidades

---

*Documentación generada: 13 de Septiembre, 2025*  
*Versión: 1.0*  
*Estado: Producción*