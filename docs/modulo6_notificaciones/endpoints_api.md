# Endpoints API - Módulo de Notificaciones

## Base URL
```
/api/notificaciones/
```

## Autenticación
Todos los endpoints requieren autenticación JWT. Incluir el token en el header:
```
Authorization: Bearer <token>
```

---

## Gestión de Dispositivos

### POST /api/notificaciones/dispositivos/
**Registrar un nuevo dispositivo para notificaciones push.**

**Request Body:**
```json
{
    "token_push": "fcm_token_o_web_push_token",
    "tipo_dispositivo": "android",
    "nombre_dispositivo": "Mi teléfono"
}
```

**Response (201 Created):**
```json
{
    "id": 1,
    "usuario": 1,
    "token_push": "fcm_token...",
    "tipo_dispositivo": "android",
    "nombre_dispositivo": "Mi teléfono",
    "activo": true,
    "fecha_registro": "2024-01-01T10:00:00Z",
    "ultima_actividad": "2024-01-01T10:00:00Z"
}
```

**Errores:**
- `400 Bad Request`: Token ya registrado o datos inválidos
- `401 Unauthorized`: Usuario no autenticado

### GET /api/notificaciones/dispositivos/
**Listar dispositivos del usuario autenticado.**

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "token_push": "fcm_token...",
        "tipo_dispositivo": "android",
        "nombre_dispositivo": "Mi teléfono",
        "activo": true,
        "fecha_registro": "2024-01-01T10:00:00Z",
        "ultima_actividad": "2024-01-01T10:00:00Z"
    }
]
```

### PATCH /api/notificaciones/dispositivos/{id}/desactivar/
**Desactivar un dispositivo.**

**Response (200 OK):**
```json
{
    "id": 1,
    "activo": false,
    "ultima_actividad": "2024-01-01T10:00:00Z"
}
```

---

## Preferencias de Notificación

### GET /api/notificaciones/preferencias/
**Obtener preferencias de notificación del usuario.**

**Response (200 OK):**
```json
[
    {
        "id": 1,
        "tipo_notificacion": "acceso_permitido",
        "push_enabled": true,
        "email_enabled": false,
        "sms_enabled": false,
        "fecha_creacion": "2024-01-01T10:00:00Z",
        "fecha_actualizacion": "2024-01-01T10:00:00Z"
    }
]
```

### POST /api/notificaciones/preferencias/
**Crear una preferencia de notificación.**

**Request Body:**
```json
{
    "tipo_notificacion": "acceso_permitido",
    "push_enabled": true,
    "email_enabled": false,
    "sms_enabled": false
}
```

**Response (201 Created):**
```json
{
    "id": 1,
    "usuario": 1,
    "tipo_notificacion": "acceso_permitido",
    "push_enabled": true,
    "email_enabled": false,
    "sms_enabled": false,
    "fecha_creacion": "2024-01-01T10:00:00Z",
    "fecha_actualizacion": "2024-01-01T10:00:00Z"
}
```

### PATCH /api/notificaciones/preferencias/bulk-update/
**Actualizar múltiples preferencias a la vez.**

**Request Body:**
```json
{
    "preferencias": [
        {
            "tipo_notificacion": "acceso_permitido",
            "push_enabled": true,
            "email_enabled": true
        },
        {
            "tipo_notificacion": "emergencia",
            "push_enabled": true,
            "sms_enabled": true
        }
    ]
}
```

**Response (200 OK):**
```json
{
    "message": "Preferencias actualizadas exitosamente",
    "updated_count": 2
}
```

---

## Notificaciones

### GET /api/notificaciones/
**Listar notificaciones del usuario (paginadas).**

**Parámetros de Query:**
- `estado`: Filtrar por estado (pendiente, enviada, fallida, leida)
- `tipo`: Filtrar por tipo
- `page`: Página para paginación

**Response (200 OK):**
```json
{
    "count": 25,
    "next": "http://api.example.com/api/notificaciones/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "titulo": "Acceso Permitido",
            "mensaje": "Se ha permitido el acceso al residente Juan Pérez",
            "tipo": "acceso_permitido",
            "estado": "enviada",
            "prioridad": 3,
            "fecha_creacion": "2024-01-01T10:00:00Z",
            "fecha_envio": "2024-01-01T10:01:00Z",
            "fecha_lectura": null,
            "datos_extra": {
                "residente_id": 1,
                "puerta": "Principal"
            }
        }
    ]
}
```

### POST /api/notificaciones/enviar/
**Enviar una notificación (requiere permisos de administrador).**

**Request Body:**
```json
{
    "titulo": "Acceso Permitido",
    "mensaje": "Se ha permitido el acceso al residente Juan Pérez",
    "tipo": "acceso_permitido",
    "usuario_id": 1,
    "prioridad": 3,
    "datos_extra": {
        "residente_id": 1,
        "puerta": "Principal"
    }
}
```

**Response (200 OK):**
```json
{
    "message": "Notificación enviada exitosamente",
    "notificacion_id": 1
}
```

### PATCH /api/notificaciones/{id}/marcar-leida/
**Marcar una notificación como leída.**

**Response (200 OK):**
```json
{
    "id": 1,
    "estado": "leida",
    "fecha_lectura": "2024-01-01T10:05:00Z"
}
```

### PATCH /api/notificaciones/marcar-todas-leidas/
**Marcar todas las notificaciones del usuario como leídas.**

**Response (200 OK):**
```json
{
    "message": "Todas las notificaciones han sido marcadas como leídas",
    "updated_count": 5
}
```

---

## Códigos de Estado HTTP

- `200 OK`: Operación exitosa
- `201 Created`: Recurso creado exitosamente
- `400 Bad Request`: Datos inválidos o solicitud malformada
- `401 Unauthorized`: Usuario no autenticado
- `403 Forbidden`: Usuario no autorizado para esta acción
- `404 Not Found`: Recurso no encontrado
- `500 Internal Server Error`: Error del servidor

## Rate Limiting

- Endpoints de listado: 100 requests/minuto por usuario
- Endpoints de creación/modificación: 30 requests/minuto por usuario
- Envío de notificaciones: 10 requests/minuto por usuario administrador