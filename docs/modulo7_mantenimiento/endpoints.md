# Endpoints API - Módulo 7: Gestión de Mantenimiento

## Base URL
```
http://localhost:8000/api/maintenance/
```

## Autenticación
Todos los endpoints requieren autenticación Token:
```
Authorization: Token <token>
```

## Endpoints de Solicitudes

### 1. Listar Solicitudes
**GET** `/api/maintenance/solicitudes/`

**Permisos:** Según rol del usuario

**Filtros Query Parameters:**
- `estado`: pendiente, asignada, en_progreso, completada, cancelada
- `prioridad`: baja, media, alta, urgente

**Respuesta Exitosa (200):**
```json
[
  {
    "id": 1,
    "solicitante_info": {
      "id": 1,
      "username": "residente1",
      "nombre_completo": "Juan Pérez"
    },
    "descripcion": "La luz del pasillo no funciona",
    "ubicacion": "Pasillo piso 3",
    "prioridad": "media",
    "prioridad_display": "Media",
    "estado": "pendiente",
    "estado_display": "Pendiente",
    "fecha_solicitud": "2025-09-28T10:30:00Z",
    "fecha_solicitud_display": "28/09/2025 10:30",
    "fecha_actualizacion": "2025-09-28T10:30:00Z"
  }
]
```

### 2. Crear Solicitud
**POST** `/api/maintenance/solicitudes/`

**Permisos:** Residentes autenticados

**Body:**
```json
{
  "descripcion": "La luz del pasillo del piso 3 no funciona",
  "ubicacion": "Pasillo piso 3, cerca del ascensor",
  "prioridad": "media"
}
```

**Respuesta Exitosa (201):**
```json
{
  "id": 1,
  "solicitante_info": {
    "id": 1,
    "username": "residente1",
    "nombre_completo": "Juan Pérez"
  },
  "descripcion": "La luz del pasillo del piso 3 no funciona",
  "ubicacion": "Pasillo piso 3, cerca del ascensor",
  "prioridad": "media",
  "prioridad_display": "Media",
  "estado": "pendiente",
  "estado_display": "Pendiente",
  "fecha_solicitud": "2025-09-28T10:30:00Z",
  "fecha_solicitud_display": "28/09/2025 10:30",
  "fecha_actualizacion": "2025-09-28T10:30:00Z",
  "tarea_info": null
}
```

### 3. Detalle de Solicitud
**GET** `/api/maintenance/solicitudes/{id}/`

**Respuesta Exitosa (200):** Similar al listado pero con tarea_info si existe

### 4. Asignar Tarea
**POST** `/api/maintenance/solicitudes/{id}/asignar_tarea/`

**Permisos:** Admin o Mantenimiento

**Body:**
```json
{
  "asignado_a_id": 2,
  "descripcion_tarea": "Revisar y reparar instalación eléctrica en pasillo piso 3",
  "notas": "Verificar circuito principal y reemplazar bombilla si es necesario"
}
```

**Respuesta Exitosa (201):**
```json
{
  "id": 1,
  "solicitud_info": {
    "id": 1,
    "descripcion": "La luz del pasillo del piso 3 no funciona",
    "ubicacion": "Pasillo piso 3, cerca del ascensor",
    "prioridad": "media",
    "prioridad_display": "Media"
  },
  "asignado_a_info": {
    "id": 2,
    "username": "mantenimiento1",
    "nombre_completo": "Carlos López",
    "role": "maintenance"
  },
  "descripcion_tarea": "Revisar y reparar instalación eléctrica en pasillo piso 3",
  "estado": "asignada",
  "estado_display": "Asignada",
  "fecha_asignacion": "2025-09-28T10:35:00Z",
  "fecha_asignacion_display": "28/09/2025 10:35",
  "fecha_completado": null,
  "fecha_completado_display": null,
  "notas": "Verificar circuito principal y reemplazar bombilla si es necesario"
}
```

## Endpoints de Tareas

### 5. Listar Tareas
**GET** `/api/maintenance/tareas/`

**Filtros Query Parameters:**
- `estado`: pendiente, asignada, en_progreso, completada, cancelada
- `asignado_a`: ID del usuario asignado

**Respuesta Exitosa (200):** Array de tareas con estructura similar al detalle

### 6. Detalle de Tarea
**GET** `/api/maintenance/tareas/{id}/`

**Respuesta Exitosa (200):**
```json
{
  "id": 1,
  "solicitud_info": {
    "id": 1,
    "descripcion": "La luz del pasillo del piso 3 no funciona",
    "ubicacion": "Pasillo piso 3, cerca del ascensor",
    "prioridad": "media",
    "prioridad_display": "Media"
  },
  "asignado_a_info": {
    "id": 2,
    "username": "mantenimiento1",
    "nombre_completo": "Carlos López",
    "role": "maintenance"
  },
  "descripcion_tarea": "Revisar y reparar instalación eléctrica en pasillo piso 3",
  "estado": "en_progreso",
  "estado_display": "En Progreso",
  "fecha_asignacion": "2025-09-28T10:35:00Z",
  "fecha_asignacion_display": "28/09/2025 10:35",
  "fecha_completado": null,
  "fecha_completado_display": null,
  "notas": "Verificar circuito principal y reemplazar bombilla si es necesario\nmantenimiento1 (28/09/2025 11:00): Iniciando revisión del circuito eléctrico"
}
```

### 7. Actualizar Estado de Tarea
**POST** `/api/maintenance/tareas/{id}/actualizar_estado/`

**Permisos:** Usuario asignado o Admin

**Body:**
```json
{
  "estado": "completada",
  "notas": "Circuito reparado. Bombilla reemplazada. Funcionando correctamente."
}
```

**Respuesta Exitosa (200):** Tarea actualizada con nuevo estado y notas agregadas

## Códigos de Error

### 400 Bad Request
- Datos inválidos en el body
- Estados no permitidos
- Usuario no encontrado

### 401 Unauthorized
- Token no proporcionado o inválido

### 403 Forbidden
- Usuario no tiene permisos para la acción
- Intentando modificar tarea no asignada

### 404 Not Found
- Solicitud o tarea no existe

### 409 Conflict
- Solicitud ya tiene tarea asignada

## Ejemplos de Uso Completo

### Flujo Típico de Mantenimiento

1. **Residente crea solicitud:**
   ```bash
   POST /api/maintenance/solicitudes/
   {
     "descripcion": "Fuga de agua en baño 2B",
     "ubicacion": "Baño apartamento 2B",
     "prioridad": "alta"
   }
   ```

2. **Admin asigna tarea:**
   ```bash
   POST /api/maintenance/solicitudes/1/asignar_tarea/
   {
     "asignado_a_id": 3,
     "descripcion_tarea": "Reparar fuga de agua en baño",
     "notas": "Revisar grifería y tuberías"
   }
   ```

3. **Mantenimiento inicia trabajo:**
   ```bash
   POST /api/maintenance/tareas/1/actualizar_estado/
   {
     "estado": "en_progreso",
     "notas": "Identificada fuga en grifo del lavabo"
   }
   ```

4. **Mantenimiento completa trabajo:**
   ```bash
   POST /api/maintenance/tareas/1/actualizar_estado/
   {
     "estado": "completada",
     "notas": "Grifo reparado. Fuga solucionada."
   }
   ```

## Rate Limiting
- No implementado actualmente
- Recomendado: 100 requests/minuto por usuario

## Versionado
- API Version: v1
- Compatibilidad: Se mantendrá hacia atrás
- Deprecaciones: Notificadas con 6 meses de anticipación