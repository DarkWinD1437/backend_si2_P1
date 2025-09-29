# 🚀 Guía Completa: Configurar Firebase y Probar Notificaciones Push

## Paso 1: Configurar Firebase Console

### 1.1 Crear o Acceder a tu Proyecto Firebase

1. Ve a [Firebase Console](https://console.firebase.google.com/)
2. Si no tienes cuenta, crea una cuenta gratuita de Google
3. Haz clic en **"Crear un proyecto"** o selecciona un proyecto existente

### 1.2 Configurar el Proyecto

1. **Nombre del proyecto**: `smartcondominium` (o el nombre que prefieras)
2. **Habilita Google Analytics**: Opcional, pero recomendado para analytics de notificaciones
3. Espera a que se cree el proyecto (puede tomar 1-2 minutos)

### 1.3 Anotar el Project ID

Una vez creado el proyecto:
1. Ve a **Configuración del proyecto** (icono de engranaje)
2. En la pestaña **General**, copia el **ID del proyecto**
   - Ejemplo: `smartcondominium-12345`
   - Este será tu `FCM_PROJECT_ID`

## Paso 2: Generar Credenciales de Service Account

### 2.1 Acceder a Service Accounts

1. En Firebase Console, ve a **Configuración del proyecto**
2. Ve a la pestaña **Cuentas de servicio**
3. Haz clic en **"Generar nueva clave privada"**

### 2.2 Descargar y Guardar el Archivo

1. Se descargará automáticamente un archivo JSON
2. **IMPORTANTE**: Renómbralo a `firebase-service-account.json`
3. **SEGURIDAD**: Guarda este archivo en una ubicación segura de tu servidor
   - ❌ NO lo subas a Git
   - ❌ NO lo compartas públicamente
   - ✅ Guárdalo en `/etc/smartcondominium/` o similar

### 2.3 Configurar Permisos (Opcional)

El service account generado automáticamente tiene permisos para FCM. Si necesitas verificar:
1. Ve a [Google Cloud Console](https://console.cloud.google.com/)
2. Busca tu proyecto
3. Ve a **IAM y administración** → **Cuentas de servicio**
4. Asegúrate de que tenga el rol **"Editor"** o **"Cloud Messaging"**

## Paso 3: Configurar VAPID Keys (para Web Push)

### 3.1 Generar Claves VAPID

1. En Firebase Console → **Configuración del proyecto**
2. Ve a la pestaña **Mensajería en la nube**
3. Desplázate a **Certificados push web**
4. Haz clic en **"Generar par de claves"**

### 3.2 Copiar las Claves

1. Copia la **Clave pública** (VAPID_PUBLIC_KEY)
2. Copia la **Clave privada** (VAPID_PRIVATE_KEY)
3. Para VAPID_CLAIMS_SUB usa tu email: `admin@smartcondominium.com`

## Paso 4: Configurar Variables de Entorno

### 4.1 Crear/Actualizar archivo .env

Crea o actualiza tu archivo `.env` en la raíz del proyecto Django:

```env
# Firebase Cloud Messaging (FCM HTTP v1 - OAuth 2.0)
FCM_PROJECT_ID=smartcondominium-12345
FCM_CREDENTIALS_PATH=/ruta/segura/firebase-service-account.json
VAPID_PUBLIC_KEY=BJzVx8X0qW6zXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
VAPID_PRIVATE_KEY=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
VAPID_CLAIMS_SUB=admin@smartcondominium.com
```

### 4.2 Verificar Configuración

Ejecuta este comando para verificar que las variables se cargan correctamente:

```bash
cd Backend_Django
python manage.py shell -c "
import os
from decouple import config
print('FCM_PROJECT_ID:', config('FCM_PROJECT_ID', default='NO CONFIGURADO'))
print('FCM_CREDENTIALS_PATH:', config('FCM_CREDENTIALS_PATH', default='NO CONFIGURADO'))
print('Archivo existe:', os.path.exists(config('FCM_CREDENTIALS_PATH', default='')))
"
```

## Paso 5: Probar la Conexión con Firebase

### 5.1 Verificar Acceso a Firebase

Ejecuta el siguiente comando para probar la conexión:

```bash
cd Backend_Django
python manage.py shell
```

En el shell de Django ejecuta:

```python
from backend.apps.modulo_notificaciones.services import NotificacionService

# Crear instancia del servicio
service = NotificacionService()

# Verificar configuración
print(f"✅ Project ID: {service.fcm_project_id}")
print(f"✅ Credentials path: {service.fcm_credentials_path}")
print(f"✅ Archivo existe: {service._credentials_file_exists()}")

# Probar obtener access token
try:
    token = service._get_access_token()
    print(f"✅ Access token obtenido: {token[:20]}...")
    print("🎉 ¡Conexión con Firebase exitosa!")
except Exception as e:
    print(f"❌ Error obteniendo token: {e}")
```

### 5.2 Ejecutar Tests del Módulo

```bash
cd Backend_Django
python manage.py test tests.modulo6_notificaciones -v 2
```

Deberías ver algo como:
```
Ran 13 tests in 2.345s
OK
```

## Paso 6: Probar Envío de Notificaciones

### 6.1 Crear un Dispositivo de Prueba

Primero necesitas registrar un dispositivo. Puedes usar Postman o curl:

```bash
curl -X POST http://localhost:8000/api/notificaciones/dispositivos/ \
  -H "Content-Type: application/json" \
  -d '{
    "usuario": 1,
    "token_fcm": "test-token-12345",
    "plataforma": "web",
    "activo": true
  }'
```

### 6.2 Enviar una Notificación de Prueba

```bash
curl -X POST http://localhost:8000/api/notificaciones/enviar/ \
  -H "Content-Type: application/json" \
  -d '{
    "titulo": "¡Prueba de Notificación!",
    "mensaje": "Si ves esta notificación, ¡Firebase está funcionando correctamente! 🎉",
    "tipo": "general",
    "usuario_id": 1,
    "prioridad": "normal"
  }'
```

### 6.3 Verificar en Firebase Console

1. Ve a Firebase Console → **Mensajería en la nube**
2. Ve a la pestaña **Informes**
3. Deberías ver las notificaciones enviadas

## Paso 7: Integración con Frontend

### 7.1 Para React/Flutter

Consulta la documentación específica:
- 📱 **React**: `docs/modulo6_notificaciones/integracion_frontend.md`
- 📱 **Flutter**: `docs/modulo6_notificaciones/integracion_frontend.md`

### 7.2 Endpoints Principales

```javascript
// Registrar dispositivo
POST /api/notificaciones/dispositivos/

// Obtener preferencias
GET /api/notificaciones/preferencias/

// Listar notificaciones del usuario
GET /api/notificaciones/

// Enviar notificación (solo admin)
POST /api/notificaciones/enviar/
```

## Paso 8: Troubleshooting

### Error: "Project ID not configured"
```bash
# Verificar variable de entorno
echo $FCM_PROJECT_ID
# Si está vacío, revisa tu archivo .env
```

### Error: "Credentials file not found"
```bash
# Verificar que el archivo existe
ls -la /ruta/a/tu/firebase-service-account.json
# Verificar permisos
chmod 600 /ruta/a/tu/firebase-service-account.json
```

### Error: "Access token could not be obtained"
```bash
# Verificar contenido del archivo JSON
cat /ruta/a/tu/firebase-service-account.json | head -5
# Debe contener: "type": "service_account"
```

### Error: "Invalid credentials"
- Verifica que descargaste el archivo correcto de Firebase Console
- Asegúrate de que no esté corrupto el JSON
- Revisa que el service account tenga permisos adecuados

### Notificaciones no llegan
- Verifica que el token FCM del dispositivo sea válido
- Revisa la consola del navegador para errores de JavaScript
- Verifica que el service worker esté registrado correctamente

## 🎯 Checklist Final

- [ ] Proyecto Firebase creado
- [ ] Project ID configurado en `.env`
- [ ] Archivo `firebase-service-account.json` descargado y seguro
- [ ] Ruta del archivo configurada en `FCM_CREDENTIALS_PATH`
- [ ] Claves VAPID generadas y configuradas
- [ ] Tests pasan correctamente
- [ ] Conexión con Firebase verificada
- [ ] Notificación de prueba enviada exitosamente
- [ ] Frontend integrado (opcional)

## 📞 Soporte

Si tienes problemas:
1. Revisa los logs de Django: `python manage.py runserver`
2. Verifica las variables de entorno
3. Consulta la documentación completa en `docs/modulo6_notificaciones/`
4. Revisa los tests para ejemplos de uso

¡Tu sistema de notificaciones está listo para producción! 🚀</content>
<parameter name="filePath">c:\Users\PG\Desktop\Materias\Sistemas de informacion 2\Proyectos\Parcial 1\Backend_Django\docs\modulo6_notificaciones\guia_configuracion_firebase.md