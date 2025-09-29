# Configuración - Módulo de Notificaciones

## Variables de Entorno

Agregar las siguientes variables al archivo `.env`:

```env
# Firebase Cloud Messaging
FCM_SERVER_KEY=your_fcm_server_key_here

# Web Push (VAPID)
VAPID_PUBLIC_KEY=your_vapid_public_key
VAPID_PRIVATE_KEY=your_vapid_private_key
VAPID_CLAIMS_SUB=email@example.com

# Configuración adicional (opcional)
NOTIFICATION_DEFAULT_PRIORITY=3
NOTIFICATION_MAX_RETRIES=3
NOTIFICATION_BATCH_SIZE=100
```

## Configuración en settings.py

El módulo ya está configurado automáticamente en `backend/settings.py`. Las configuraciones aplicadas son:

```python
# Apps instaladas
INSTALLED_APPS = [
    # ... otras apps
    'backend.apps.modulo_notificaciones',
    'fcm_django',  # Para Firebase Cloud Messaging
    'webpush',     # Para Web Push
]

# Configuración FCM
FCM_SERVER_KEY = env('FCM_SERVER_KEY')

# Configuración VAPID para Web Push
WEBPUSH_SETTINGS = {
    "VAPID_PUBLIC_KEY": env('VAPID_PUBLIC_KEY'),
    "VAPID_PRIVATE_KEY": env('VAPID_PRIVATE_KEY'),
    "VAPID_ADMIN_EMAIL": env('VAPID_CLAIMS_SUB')
}

# Configuración de notificaciones (opcional)
NOTIFICATION_SETTINGS = {
    'DEFAULT_PRIORITY': env.int('NOTIFICATION_DEFAULT_PRIORITY', default=3),
    'MAX_RETRIES': env.int('NOTIFICATION_MAX_RETRIES', default=3),
    'BATCH_SIZE': env.int('NOTIFICATION_BATCH_SIZE', default=100),
}
```

## Configuración de Firebase

### 1. Crear Proyecto en Firebase Console

1. Ir a [Firebase Console](https://console.firebase.google.com/)
2. Crear un nuevo proyecto o seleccionar uno existente
3. Habilitar Firebase Cloud Messaging (FCM)

### 2. Obtener FCM Server Key

1. En Firebase Console, ir a **Project Settings** > **Cloud Messaging**
2. En "Server Key", copiar la clave
3. Agregarla como `FCM_SERVER_KEY` en el archivo `.env`

### 3. Configurar VAPID Keys para Web Push

1. En Firebase Console, ir a **Project Settings** > **Web Push certificates**
2. Generar un nuevo par de claves VAPID
3. Copiar la clave pública y privada
4. Agregarla como `VAPID_PUBLIC_KEY` y `VAPID_PRIVATE_KEY` en el archivo `.env`
5. Usar un email válido como `VAPID_CLAIMS_SUB`

## Configuración de Base de Datos

El módulo incluye migraciones automáticas. Para aplicarlas:

```bash
python manage.py migrate
```

Las tablas creadas serán:
- `modulo_notificaciones_dispositivo`
- `modulo_notificaciones_preferenciasnotificacion`
- `modulo_notificaciones_notificacion`

## Configuración de URLs

Las URLs del módulo se registran automáticamente en `backend/urls.py`:

```python
urlpatterns = [
    # ... otras URLs
    path('api/notificaciones/', include('backend.apps.modulo_notificaciones.urls')),
]
```

## Configuración de Permisos

### Permisos de Usuario

- **Usuario Regular**: Puede gestionar sus propios dispositivos, preferencias y notificaciones
- **Administrador**: Puede enviar notificaciones a cualquier usuario

### Configuración de CORS (si es necesario)

Si usas CORS, asegúrate de que los orígenes de tus aplicaciones frontend estén permitidos:

```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",  # React dev
    "http://localhost:3001",  # Otro puerto
    "https://tu-dominio.com", # Producción
]
```

## Configuración de Logging

Para debugging de notificaciones, puedes agregar configuración de logging:

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'backend.apps.modulo_notificaciones': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

## Configuración de Tareas Asíncronas (Opcional)

Para envío masivo de notificaciones, considera usar Celery:

```python
# settings.py
CELERY_BROKER_URL = env('REDIS_URL', default='redis://localhost:6379/0')
CELERY_RESULT_BACKEND = env('REDIS_URL', default='redis://localhost:6379/0')

# Tareas
from celery import shared_task

@shared_task
def send_bulk_notifications(notification_ids, user_ids):
    # Lógica para envío masivo
    pass
```

## Configuración de Testing

Para ejecutar solo los tests del módulo:

```bash
# Tests unitarios
python manage.py test tests.modulo6_notificaciones -v 2

# Con coverage
coverage run --source='backend.apps.modulo_notificaciones' manage.py test tests.modulo6_notificaciones
coverage report
```

## Configuración de Producción

### Variables de Entorno de Producción

```env
# Producción
FCM_SERVER_KEY=your_production_fcm_key
VAPID_PUBLIC_KEY=your_production_vapid_public
VAPID_PRIVATE_KEY=your_production_vapid_private
VAPID_CLAIMS_SUB=noreply@tu-dominio.com

# Configuración adicional
NOTIFICATION_DEFAULT_PRIORITY=3
NOTIFICATION_MAX_RETRIES=5
NOTIFICATION_BATCH_SIZE=500
```

### Configuración de Redis (para caching)

```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': env('REDIS_URL', default='redis://127.0.0.1:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

### Configuración de Email (para notificaciones por email)

```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = env('EMAIL_HOST')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL')
```

## Verificación de Configuración

Para verificar que todo está configurado correctamente:

```python
# En shell de Django
python manage.py shell

from django.apps import apps
from backend.apps.modulo_notificaciones.models import Dispositivo, PreferenciasNotificacion, Notificacion

# Verificar que las apps están registradas
print("Apps registradas:")
for app in apps.get_app_configs():
    if 'notificaciones' in app.name:
        print(f"- {app.name}")

# Verificar modelos
print("\nModelos disponibles:")
print(f"- Dispositivo: {Dispositivo._meta.app_label}")
print(f"- PreferenciasNotificacion: {PreferenciasNotificacion._meta.app_label}")
print(f"- Notificacion: {Notificacion._meta.app_label}")

# Verificar configuración FCM
from django.conf import settings
print(f"\nFCM Server Key configurado: {bool(getattr(settings, 'FCM_SERVER_KEY', None))}")
print(f"WebPush configurado: {bool(getattr(settings, 'WEBPUSH_SETTINGS', None))}")
```

## Troubleshooting

### Error: "App 'modulo_notificaciones' not found"

**Solución**: Verificar que la app esté en `INSTALLED_APPS` en `settings.py`

### Error: "FCM server key not found"

**Solución**: Verificar que `FCM_SERVER_KEY` esté configurada en variables de entorno

### Error: "VAPID keys not configured"

**Solución**: Verificar que las claves VAPID estén configuradas correctamente

### Error: "No such table" en tests

**Solución**: Ejecutar `python manage.py migrate` antes de los tests

### Notificaciones no llegan

**Posibles causas**:
1. Token FCM inválido o expirado
2. Permisos no concedidos en el dispositivo
3. FCM server key incorrecta
4. Problemas de conectividad con Firebase