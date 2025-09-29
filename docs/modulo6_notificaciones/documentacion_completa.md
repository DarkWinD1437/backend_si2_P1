# Módulo de Notificaciones - Documentación Completa

## Descripción General

El módulo de notificaciones permite enviar notificaciones push, email y SMS a los usuarios del condominio. Incluye gestión de dispositivos, preferencias de notificación por usuario y un sistema completo de envío de notificaciones.

## Características Principales

- **Notificaciones Push**: Soporte para FCM (Firebase Cloud Messaging) y Web Push
- **Preferencias por Usuario**: Cada usuario puede configurar qué tipos de notificaciones recibir
- **Múltiples Canales**: Push, Email y SMS
- **Gestión de Dispositivos**: Registro y gestión de tokens de dispositivos
- **Historial Completo**: Registro de todas las notificaciones enviadas
- **Priorización**: Sistema de prioridades para notificaciones críticas

## Modelos de Datos

### Dispositivo
- **usuario**: Usuario propietario del dispositivo
- **token_push**: Token FCM o web push (único)
- **tipo_dispositivo**: web, android, ios, flutter_web
- **nombre_dispositivo**: Nombre descriptivo opcional
- **activo**: Estado del dispositivo
- **fecha_registro**: Fecha de registro
- **ultima_actividad**: Última actividad del dispositivo

### PreferenciasNotificacion
- **usuario**: Usuario de las preferencias
- **tipo_notificacion**: Tipo de notificación (acceso_permitido, acceso_denegado, etc.)
- **push_enabled**: Habilitar notificaciones push
- **email_enabled**: Habilitar notificaciones email
- **sms_enabled**: Habilitar notificaciones SMS

### Notificacion
- **titulo**: Título de la notificación
- **mensaje**: Contenido de la notificación
- **tipo**: Tipo de notificación
- **usuario**: Destinatario
- **dispositivo**: Dispositivo específico (opcional)
- **estado**: pendiente, enviada, fallida, leida
- **prioridad**: Nivel de prioridad (1-5)
- **datos_extra**: Datos adicionales en JSON
- **push_enviado/email_enviado/sms_enviado**: Estado de envío por canal

## Endpoints API

### Gestión de Dispositivos

#### POST /api/notificaciones/dispositivos/
Registrar un nuevo dispositivo para notificaciones push.

**Request Body:**
```json
{
    "token_push": "fcm_token_o_web_push_token",
    "tipo_dispositivo": "android",
    "nombre_dispositivo": "Mi teléfono"
}
```

**Response:**
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

#### GET /api/notificaciones/dispositivos/
Listar dispositivos del usuario autenticado.

#### PATCH /api/notificaciones/dispositivos/{id}/desactivar/
Desactivar un dispositivo.

### Preferencias de Notificación

#### GET /api/notificaciones/preferencias/
Obtener preferencias de notificación del usuario.

#### POST /api/notificaciones/preferencias/
Crear una preferencia de notificación.

**Request Body:**
```json
{
    "tipo_notificacion": "acceso_permitido",
    "push_enabled": true,
    "email_enabled": false,
    "sms_enabled": false
}
```

#### PATCH /api/notificaciones/preferencias/bulk-update/
Actualizar múltiples preferencias a la vez.

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

### Notificaciones

#### GET /api/notificaciones/
Listar notificaciones del usuario (paginadas).

**Parámetros de Query:**
- `estado`: Filtrar por estado (pendiente, enviada, fallida, leida)
- `tipo`: Filtrar por tipo
- `page`: Página para paginación

#### POST /api/notificaciones/enviar/
Enviar una notificación (requiere permisos de administrador).

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

#### PATCH /api/notificaciones/{id}/marcar-leida/
Marcar una notificación como leída.

#### PATCH /api/notificaciones/marcar-todas-leidas/
Marcar todas las notificaciones del usuario como leídas.

## Configuración

### Variables de Entorno

Agregar al archivo `.env`:

```env
# Firebase Cloud Messaging
FCM_SERVER_KEY=your_fcm_server_key_here

# Web Push (VAPID)
VAPID_PUBLIC_KEY=your_vapid_public_key
VAPID_PRIVATE_KEY=your_vapid_private_key
VAPID_CLAIMS_SUB=email@example.com
```

### Configuración en settings.py

El módulo ya está configurado automáticamente. Las siguientes configuraciones se aplican:

```python
# Apps instaladas
INSTALLED_APPS = [
    # ... otras apps
    'backend.apps.modulo_notificaciones',
]

# Configuración FCM
FCM_SERVER_KEY = env('FCM_SERVER_KEY')

# Configuración VAPID para Web Push
WEBPUSH_SETTINGS = {
    "VAPID_PUBLIC_KEY": env('VAPID_PUBLIC_KEY'),
    "VAPID_PRIVATE_KEY": env('VAPID_PRIVATE_KEY'),
    "VAPID_ADMIN_EMAIL": env('VAPID_CLAIMS_SUB')
}
```

## Tipos de Notificación

- **acceso_permitido**: Cuando se permite acceso a un residente
- **acceso_denegado**: Cuando se deniega acceso
- **nuevo_mensaje**: Nuevo mensaje en comunicaciones
- **pago_realizado**: Confirmación de pago realizado
- **pago_pendiente**: Recordatorio de pago pendiente
- **mantenimiento**: Avisos de mantenimiento
- **emergencia**: Notificaciones de emergencia
- **recordatorio**: Recordatorios generales
- **sistema**: Notificaciones del sistema

## Manejo de Errores

### Errores Comunes

1. **Token FCM Inválido**: El token del dispositivo ha expirado
   - Solución: Re-registrar el dispositivo

2. **Permisos No Concedidos**: El usuario no ha dado permisos para notificaciones
   - Solución: Solicitar permisos nuevamente

3. **Servidor FCM No Configurado**: Falta la clave del servidor FCM
   - Solución: Configurar FCM_SERVER_KEY en variables de entorno

## Testing

El módulo incluye tests completos que cubren:

- Registro y gestión de dispositivos
- Creación y actualización de preferencias
- Envío de notificaciones individuales y masivas
- Marcado de notificaciones como leídas
- Validación de permisos y autenticación

Para ejecutar los tests:
```bash
python manage.py test tests.modulo6_notificaciones -v 2
```

## Próximos Pasos

- Implementar envío real de emails
- Integrar servicio de SMS
- Agregar templates de notificación personalizables
- Implementar notificaciones programadas
- Agregar analytics de notificaciones