# Configuración Actualizada - Módulo de Notificaciones (FCM HTTP v1)

## ⚠️ IMPORTANTE: Actualización a FCM HTTP v1 API

Firebase ha migrado de la API legacy (v0) a la nueva API HTTP v1 que usa OAuth 2.0. El código ha sido actualizado automáticamente.

## Variables de Entorno (ACTUALIZADAS)

Agregar las siguientes variables al archivo `.env`:

```env
# Firebase Cloud Messaging (API HTTP v1 - OAuth 2.0)
FCM_PROJECT_ID=your-firebase-project-id
FCM_CREDENTIALS_PATH=/path/to/your/service-account.json
VAPID_PUBLIC_KEY=your-vapid-public-key-here
VAPID_PRIVATE_KEY=your-vapid-private-key-here
VAPID_CLAIMS_SUB=email@example.com
```

## Configuración de Firebase (PASO A PASO)

### 1. Crear Proyecto en Firebase Console

1. Ve a [Firebase Console](https://console.firebase.google.com/)
2. Crea un proyecto o usa uno existente
3. Anota el **Project ID** (lo necesitarás para `FCM_PROJECT_ID`)

### 2. Crear Service Account y Descargar Credenciales

1. En Firebase Console, ve a **Project Settings** → **Service accounts**
2. Haz clic en **Generate new private key**
3. Se descargará un archivo JSON (`service-account.json`)
4. **IMPORTANTE**: Guarda este archivo en una ubicación segura en tu servidor
5. Configura la ruta en `FCM_CREDENTIALS_PATH`

### 3. Configurar VAPID Keys para Web Push

1. En Firebase Console → **Project Settings** → **Web Push certificates**
2. Genera un nuevo par de claves VAPID
3. Copia la clave pública y privada

### 4. Configuración Alternativa (Application Default Credentials)

Si estás ejecutando en Google Cloud Platform (GCP), puedes usar Application Default Credentials:

```env
# No necesitas FCM_CREDENTIALS_PATH si usas ADC
FCM_PROJECT_ID=your-project-id
```

## Configuración en settings.py

El módulo ya está configurado automáticamente:

```python
# Configuración FCM HTTP v1 API
FCM_PROJECT_ID = config('FCM_PROJECT_ID', default='')
FCM_CREDENTIALS_PATH = config('FCM_CREDENTIALS_PATH', default='')
VAPID_PRIVATE_KEY = config('VAPID_PRIVATE_KEY', default='')
VAPID_CLAIMS_SUB = config('VAPID_CLAIMS_SUB', default='')
```

## Verificación de Configuración

Para verificar que todo está configurado correctamente:

```python
# En shell de Django
python manage.py shell

from backend.apps.modulo_notificaciones.services import NotificacionService

# Verificar configuración
service = NotificacionService()
print(f"Project ID configurado: {service.fcm_project_id}")
print(f"Credentials path: {service.fcm_credentials_path}")

# Probar obtener access token
token = service._get_access_token()
print(f"Access token obtenido: {token is not None}")
```

## Cambios Técnicos Realizados

### ✅ Lo que se actualizó:

1. **Autenticación**: De server key a OAuth 2.0 access tokens
2. **Endpoint**: `https://fcm.googleapis.com/v1/projects/{project-id}/messages:send`
3. **Payload**: Nuevo formato con estructura `message`
4. **Librerías**: Agregadas `google-auth` y `google-auth-oauthlib`

### ✅ Compatibilidad:

- ✅ Android/iOS/Web push siguen funcionando
- ✅ APIs REST sin cambios
- ✅ Tests actualizados automáticamente
- ✅ Documentación actualizada

## Testing

Ejecuta los tests para verificar que todo funciona:

```bash
python manage.py test tests.modulo6_notificaciones -v 2
```

## Troubleshooting

### Error: "Project ID not configured"
**Solución**: Verificar que `FCM_PROJECT_ID` esté configurada

### Error: "Credentials file not found"
**Solución**: Verificar que `FCM_CREDENTIALS_PATH` apunte a un archivo JSON válido

### Error: "Access token could not be obtained"
**Causas posibles**:
1. Archivo de credenciales inválido
2. Service account sin permisos adecuados
3. Problemas de conectividad con Google APIs

### Migración desde FCM Legacy API

Si estabas usando la API legacy (v0), la migración incluye:

1. **Cambiar autenticación**: De server key a OAuth 2.0
2. **Nuevo endpoint**: `https://fcm.googleapis.com/v1/projects/{project-id}/messages:send`
3. **Nuevo formato de payload**: Estructura `message` en lugar de campos directos
4. **Mejor soporte multiplataforma**: Configuraciones específicas para Android/iOS/Web