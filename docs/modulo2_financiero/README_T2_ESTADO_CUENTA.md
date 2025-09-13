# Módulo 2: Gestión Financiera Básica - T2: Consultar Estado de Cuenta

## 📋 Descripción General

El endpoint **estado de cuenta** permite a los residentes consultar su situación financiera completa y a los administradores revisar el estado financiero de cualquier residente. Proporciona una vista integral que incluye cargos pendientes, vencidos, historial de pagos y alertas relevantes.

## 🎯 Funcionalidades Implementadas

### ✅ Para Residentes
- Consulta de su propio estado de cuenta
- Visualización de cargos pendientes y vencidos
- Historial de pagos de los últimos 6 meses
- Alertas automáticas sobre vencimientos
- Resumen de totales y estadísticas personales

### ✅ Para Administradores
- Consulta de estado de cuenta propio
- Consulta de estado de cuenta de cualquier residente
- Acceso completo a toda la información financiera
- Capacidad de filtrar por residente específico

## 🔗 Endpoints Principales

### `GET /api/finances/cargos/estado_cuenta/`
**Consultar estado de cuenta completo**

#### Parámetros
- `residente` (opcional, solo admin): ID del residente a consultar

#### Permisos
- **Residentes**: Solo pueden consultar su propio estado de cuenta
- **Administradores**: Pueden consultar cualquier estado de cuenta

#### Ejemplo de Uso - Residente
```bash
# Consultar propio estado de cuenta
curl -X GET "http://localhost:8000/api/finances/cargos/estado_cuenta/" \
     -H "Authorization: Token {resident_token}"
```

#### Ejemplo de Uso - Administrador
```bash
# Consultar estado de cuenta de residente específico
curl -X GET "http://localhost:8000/api/finances/cargos/estado_cuenta/?residente=5" \
     -H "Authorization: Token {admin_token}"

# Consultar propio estado de cuenta (admin)
curl -X GET "http://localhost:8000/api/finances/cargos/estado_cuenta/" \
     -H "Authorization: Token {admin_token}"
```

## 📊 Estructura de Respuesta

```json
{
  "residente_info": {
    "id": 5,
    "username": "resident1",
    "email": "resident1@example.com",
    "nombre_completo": "Juan Pérez",
    "first_name": "Juan",
    "last_name": "Pérez"
  },
  "fecha_consulta": "2024-12-19",
  "resumen_general": {
    "total_pendiente": "225000.00",
    "total_vencido": "50000.00", 
    "total_al_dia": "175000.00",
    "cantidad_cargos_pendientes": 3,
    "cantidad_cargos_vencidos": 1,
    "total_pagado_mes_actual": "0.00",
    "total_pagado_6_meses": "300000.00"
  },
  "cargos_pendientes": [
    {
      "id": 15,
      "concepto_nombre": "Cuota de Mantenimiento Mensual",
      "concepto_tipo": "cuota_mensual",
      "residente_username": "resident1",
      "residente_nombre": "Juan Pérez",
      "monto": "150000.00",
      "estado": "pendiente",
      "estado_display": "Pendiente",
      "fecha_aplicacion": "2024-11-19",
      "fecha_vencimiento": "2024-12-04",
      "esta_vencido": false
    }
  ],
  "cargos_vencidos": [
    {
      "id": 18,
      "concepto_nombre": "Multa por Ruido Nocturno", 
      "concepto_tipo": "multa_ruido",
      "residente_username": "resident1",
      "residente_nombre": "Juan Pérez",
      "monto": "50000.00",
      "estado": "vencido",
      "estado_display": "Vencido",
      "fecha_aplicacion": "2024-11-29",
      "fecha_vencimiento": "2024-12-14",
      "esta_vencido": true
    }
  ],
  "historial_pagos": [
    {
      "id": 12,
      "concepto_nombre": "Cuota de Mantenimiento Mensual",
      "concepto_tipo": "cuota_mensual", 
      "residente_username": "resident1",
      "residente_nombre": "Juan Pérez",
      "monto": "150000.00",
      "estado": "pagado",
      "estado_display": "Pagado",
      "fecha_aplicacion": "2024-09-19",
      "fecha_vencimiento": "2024-10-04",
      "esta_vencido": false
    }
  ],
  "desglose_por_tipo": [
    {
      "concepto__tipo": "cuota_mensual",
      "concepto__nombre": "Cuota de Mantenimiento Mensual",
      "cantidad": 2,
      "total": "300000.00"
    },
    {
      "concepto__tipo": "multa_ruido", 
      "concepto__nombre": "Multa por Ruido Nocturno",
      "cantidad": 1,
      "total": "50000.00"
    }
  ],
  "proximo_vencimiento": {
    "cargo": {
      "id": 15,
      "concepto_nombre": "Cuota de Mantenimiento Mensual",
      "monto": "150000.00",
      "fecha_vencimiento": "2024-12-04"
    },
    "fecha": "2024-12-04",
    "dias_restantes": 5
  },
  "ultimo_pago": {
    "cargo": {
      "id": 12,
      "concepto_nombre": "Cuota de Mantenimiento Mensual", 
      "monto": "150000.00"
    },
    "fecha": "2024-10-01T10:30:00Z",
    "hace_dias": 79
  },
  "alertas": [
    {
      "tipo": "vencimiento_proximo",
      "severidad": "media",
      "titulo": "Cargo próximo a vencer",
      "mensaje": "Cuota de Mantenimiento Mensual vence en 5 día(s)",
      "accion": "Revisar y programar pago"
    },
    {
      "tipo": "vencido",
      "severidad": "alta", 
      "titulo": "Tiene 1 cargo(s) vencido(s)",
      "mensaje": "Total vencido: $50000.00. Se recomienda realizar el pago lo antes posible.",
      "accion": "Pagar cargos vencidos"
    }
  ]
}
```

## 🔒 Control de Permisos

### Sistema de Autorización
- **Token de autenticación**: Requerido en todas las consultas
- **Verificación de roles**: Diferenciación entre admin y resident
- **Restricción de acceso**: Residentes solo ven su información

### Validaciones Implementadas
- Usuario autenticado válido
- Token activo y no expirado
- Permisos según el rol del usuario
- Validación de existencia del residente consultado (admin)

## 📈 Funcionalidades Destacadas

### 🚨 Sistema de Alertas
- **Cargos vencidos**: Alerta de alta severidad
- **Vencimientos próximos**: Alertas con 7 días de antelación
- **Severidad graduada**: Baja, media y alta según urgencia

### 📊 Resumen Inteligente
- **Totales calculados**: Pendiente, vencido, al día
- **Períodos específicos**: Mes actual, últimos 6 meses
- **Contadores**: Cantidad de cargos por estado
- **Desglose por tipo**: Agrupación por conceptos

### 🕐 Información Temporal
- **Próximo vencimiento**: Cargo más urgente pendiente
- **Último pago**: Referencia del pago más reciente
- **Días calculados**: Días restantes y días transcurridos

## 🧪 Testing y Validación

### Script de Testing
```bash
python scripts/testing_manual/test_estado_cuenta_completo.py
```

### Casos de Prueba Cubiertos
1. **Autenticación**: Admin y residente
2. **Consulta propia**: Ambos roles
3. **Consulta cruzada**: Admin consultando residentes
4. **Restricciones**: Residente intentando consultar otros
5. **Estructura**: Validación completa de respuesta
6. **Endpoints complementarios**: mis_cargos, conceptos vigentes

## 📋 Poblado de Datos

### Script de Poblado
```bash
python manage.py shell < scripts/poblado_db/poblar_modulo_financiero.py
```

### Datos Generados
- **7 conceptos financieros**: Cuotas mensuales, extraordinarias y multas
- **Cargos por residente**: Historial realista de 3 meses
- **Estados variados**: Pendientes, pagados y vencidos
- **Referencias de pago**: Para cargos pagados

## 🔗 Endpoints Relacionados

### Complementarios
- `GET /api/finances/cargos/mis_cargos/` - Lista simple de cargos del usuario
- `GET /api/finances/conceptos/vigentes/` - Conceptos financieros activos
- `GET /api/finances/cargos/resumen/{user_id}/` - Resumen básico (legacy)

### Administrativos
- `GET /api/finances/cargos/vencidos/` - Solo cargos vencidos (admin)
- `GET /api/finances/estadisticas/` - Estadísticas generales (admin)

## ⚡ Optimizaciones Implementadas

### Performance
- **Select Related**: Optimización de consultas DB
- **Límites de historial**: Máximo 20 pagos recientes
- **Agregaciones**: Uso de Sum() y Count() en DB
- **Índices**: En modelos para búsquedas frecuentes

### Usabilidad
- **Campos calculados**: Días restantes, está vencido
- **Información contextual**: Nombres completos, displays legibles
- **Estructura organizada**: Separación clara de secciones

## 🎯 Casos de Uso Principales

### Para Residentes
1. **Consulta regular**: "¿Cuánto debo del condominio?"
2. **Planificación**: "¿Cuándo vencen mis próximos pagos?"
3. **Historial**: "¿Qué pagos he hecho este año?"
4. **Alertas**: "¿Tengo cargos vencidos?"

### Para Administradores
1. **Seguimiento**: "¿Cómo está el residente X financieramente?"
2. **Cobranza**: "¿Qué residentes tienen cargos vencidos?"
3. **Análisis**: "¿Cuál es el patrón de pagos de un residente?"
4. **Soporte**: "Ayudar a residente con su estado de cuenta"

## 🔧 Configuración y Requisitos

### Dependencias
- Django 5.x
- Django REST Framework
- PostgreSQL (para agregaciones optimizadas)
- Módulo de usuarios con roles (admin/resident)

### Variables de Configuración
- Días para alerta de vencimiento: 7 días
- Límite de historial: 20 registros
- Período de historial: 6 meses
- Días para considerar vencido: Fecha pasada

## 🚀 Próximas Mejoras

### Funcionalidades Futuras
- **Exportación**: PDF y Excel del estado de cuenta
- **Notificaciones**: Email automático de vencimientos
- **Gráficos**: Visualización de tendencias de pago
- **Proyecciones**: Predicción de próximos cargos

### Optimizaciones Técnicas
- **Cache**: Redis para consultas frecuentes
- **Paginación**: Para historiales muy extensos
- **Filtros avanzados**: Por fechas, tipos, montos
- **WebSockets**: Actualizaciones en tiempo real

---

*Documentación generada para Módulo 2: Gestión Financiera Básica - T2: Consultar Estado de Cuenta*
*Fecha: Diciembre 2024*