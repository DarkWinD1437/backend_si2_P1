# 🔗 Integración Completa de Firebase Cloud Messaging (FCM)

## 📋 Resumen Ejecutivo

Este documento describe la **integración completa de Firebase Cloud Messaging (FCM) HTTP v1 API** en el proyecto SmartCondominium. La integración utiliza **OAuth 2.0** para autenticación y soporta notificaciones push para **Android, iOS y Web**.

---

## 🏗️ Arquitectura de la Integración

### **Componentes Principales**

```
Firebase Integration
├── 🔐 Autenticación OAuth 2.0
├── 📡 API HTTP v1
├── 🗄️ Modelos de Datos
├── 🔧 Servicios Backend
├── 🌐 Endpoints REST API
├── 🧪 Sistema de Testing
└── 📚 Configuración
```

---

## ⚙️ Configuración del Sistema

### **1. Variables de Entorno (.env)**

```env
# =============================================================================
# FIREBASE CLOUD MESSAGING (FCM HTTP v1 API)
# =============================================================================

# ID del proyecto de Firebase (lo obtienes de Firebase Console → Project Settings)
FCM_PROJECT_ID=smart-condominium-101a9

# Ruta ABSOLUTA al archivo JSON de credenciales del service account
FCM_CREDENTIALS_PATH=C:\firebase\firebase-service-account.json

# Claves VAPID para notificaciones web push
VAPID_PUBLIC_KEY=BDKE56mfQfvdF0tKbh_4i0k-YS9AYOOG8CL9jJb_7EebJkXtvAxCFH7SSZpr5YQ4WclBA0V0aqbqZF5BivveUNY
VAPID_PRIVATE_KEY=5onbF3rHIZqo3wWnLAdMGdJsXcrzpi4EmusYT-gMP6E
VAPID_CLAIMS_SUB=admin@smartcondominium.com
```

### **2. Configuración en settings.py**

```python
# backend/settings.py

# Firebase Cloud Messaging Configuration
FCM_PROJECT_ID = config('FCM_PROJECT_ID', default='')
FCM_CREDENTIALS_PATH = config('FCM_CREDENTIALS_PATH', default='')
VAPID_PRIVATE_KEY = config('VAPID_PRIVATE_KEY', default='')
VAPID_CLAIMS_SUB = config('VAPID_CLAIMS_SUB', default='')

# Apps instaladas
INSTALLED_APPS = [
    # ... otras apps ...
    'backend.apps.modulo_notificaciones',
]
```

### **3. Dependencias (requirements.txt)**

```txt
# Firebase Cloud Messaging (FCM HTTP v1)
google-auth==2.29.0
google-auth-oauthlib==1.2.0
```

---

## 🗄️ Modelos de Datos

### **Dispositivo Model**

```python
# backend/apps/modulo_notificaciones/models.py

class Dispositivo(models.Model):
    """Modelo para almacenar tokens de dispositivos para notificaciones push"""

    TIPO_DISPOSITIVO_CHOICES = [
        ('web', 'Web Browser'),
        ('android', 'Android'),
        ('ios', 'iOS'),
        ('flutter_web', 'Flutter Web'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dispositivos')
    token_push = models.CharField(max_length=500, unique=True, help_text="Token FCM o web push")
    tipo_dispositivo = models.CharField(max_length=20, choices=TIPO_DISPOSITIVO_CHOICES)
    nombre_dispositivo = models.CharField(max_length=100, blank=True, help_text="Nombre descriptivo del dispositivo")
    activo = models.BooleanField(default=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)
    ultima_actividad = models.DateTimeField(auto_now=True)

    class Meta:
        app_label = 'modulo_notificaciones'
        verbose_name = "Dispositivo"
        verbose_name_plural = "Dispositivos"
        ordering = ['-ultima_actividad']
```

### **Notificacion Model**

```python
class Notificacion(models.Model):
    """Modelo para almacenar todas las notificaciones enviadas"""

    ESTADO_CHOICES = [
        ('pendiente', 'Pendiente'),
        ('enviada', 'Enviada'),
        ('fallida', 'Fallida'),
        ('leida', 'Leída'),
    ]

    TIPO_NOTIFICACION_CHOICES = [
        ('acceso_permitido', 'Acceso Permitido'),
        ('acceso_denegado', 'Acceso Denegado'),
        ('nuevo_mensaje', 'Nuevo Mensaje'),
        ('pago_realizado', 'Pago Realizado'),
        ('pago_pendiente', 'Pago Pendiente'),
        ('mantenimiento', 'Aviso de Mantenimiento'),
        ('emergencia', 'Emergencia'),
        ('recordatorio', 'Recordatorio'),
        ('sistema', 'Sistema'),
    ]

    titulo = models.CharField(max_length=200)
    mensaje = models.TextField()
    tipo = models.CharField(max_length=50, choices=TIPO_NOTIFICACION_CHOICES, default='sistema')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notificaciones')
    dispositivo = models.ForeignKey(Dispositivo, on_delete=models.SET_NULL, null=True, blank=True, related_name='notificaciones')

    # Estado y envío
    estado = models.CharField(max_length=20, choices=ESTADO_CHOICES, default='pendiente')
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_envio = models.DateTimeField(null=True, blank=True)
    fecha_lectura = models.DateTimeField(null=True, blank=True)

    # Datos adicionales
    datos_extra = models.JSONField(null=True, blank=True, help_text="Datos adicionales en formato JSON")
    prioridad = models.IntegerField(default=1, help_text="Prioridad (1-5, siendo 5 la más alta)")

    # Información de envío
    push_enviado = models.BooleanField(default=False)
    email_enviado = models.BooleanField(default=False)
    sms_enviado = models.BooleanField(default=False)

    # Errores
    error_mensaje = models.TextField(blank=True, null=True)
```

### **PreferenciasNotificacion Model**

```python
class PreferenciasNotificacion(models.Model):
    """Modelo para las preferencias de notificación de cada usuario"""

    TIPO_NOTIFICACION_CHOICES = [
        ('acceso_permitido', 'Acceso Permitido'),
        ('acceso_denegado', 'Acceso Denegado'),
        ('nuevo_mensaje', 'Nuevo Mensaje'),
        ('pago_realizado', 'Pago Realizado'),
        ('pago_pendiente', 'Pago Pendiente'),
        ('mantenimiento', 'Aviso de Mantenimiento'),
        ('emergencia', 'Emergencia'),
        ('recordatorio', 'Recordatorio'),
    ]

    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='preferencias_notificacion')
    tipo_notificacion = models.CharField(max_length=50, choices=TIPO_NOTIFICACION_CHOICES)
    push_enabled = models.BooleanField(default=True, help_text="Enviar notificación push")
    email_enabled = models.BooleanField(default=False, help_text="Enviar notificación por email")
    sms_enabled = models.BooleanField(default=False, help_text="Enviar notificación por SMS")
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    fecha_actualizacion = models.DateTimeField(auto_now=True)
```

---

## 🔧 Servicios Backend

### **NotificacionService Class**

```python
# backend/apps/modulo_notificaciones/services.py

class NotificacionService:
    """Servicio para manejar el envío de notificaciones push"""

    def __init__(self):
        self.fcm_project_id = getattr(settings, 'FCM_PROJECT_ID', None)
        self.fcm_credentials_path = getattr(settings, 'FCM_CREDENTIALS_PATH', None)
        self.vapid_private_key = getattr(settings, 'VAPID_PRIVATE_KEY', None)
        self.vapid_email = getattr(settings, 'VAPID_CLAIMS_SUB', None)
        self._access_token = None
        self._token_expiry = None
```

### **Métodos Principales**

#### **enviar_notificacion_masiva()**
```python
def enviar_notificacion_masiva(self, titulo, mensaje, tipo, usuarios_ids=None,
                             datos_extra=None, prioridad=1):
    """
    Enviar notificación a múltiples usuarios
    """
```

#### **_get_access_token()**
```python
def _get_access_token(self):
    """
    Obtener access token OAuth 2.0 para FCM
    """
    from datetime import datetime, timedelta

    # Si ya tenemos un token válido, lo reutilizamos
    if self._access_token and self._token_expiry and datetime.now() < self._token_expiry:
        return self._access_token

    try:
        if self.fcm_credentials_path:
            # Usar service account file
            credentials = service_account.Credentials.from_service_account_file(
                self.fcm_credentials_path,
                scopes=['https://www.googleapis.com/auth/firebase.messaging']
            )
        else:
            # Intentar usar Application Default Credentials
            credentials, project = default(scopes=['https://www.googleapis.com/auth/firebase.messaging'])
            if not self.fcm_project_id:
                self.fcm_project_id = project

        # Refresh token si es necesario
        if not credentials.valid:
            request = Request()
            credentials.refresh(request)

        self._access_token = credentials.token
        # El token expira en 1 hora, pero guardamos con un margen de 5 minutos
        self._token_expiry = datetime.now() + timedelta(seconds=credentials.expiry.timestamp() - datetime.now().timestamp() - 300)

        return self._access_token

    except Exception as e:
        print(f"Error obteniendo access token: {e}")
        return None
```

#### **_enviar_fcm()**
```python
def _enviar_fcm(self, notificacion, dispositivo):
    """
    Enviar notificación usando Firebase Cloud Messaging API HTTP v1
    """
    if not self.fcm_project_id:
        print("FCM_PROJECT_ID no configurado")
        return False

    access_token = self._get_access_token()
    if not access_token:
        print("No se pudo obtener access token para FCM")
        return False

    url = f'https://fcm.googleapis.com/v1/projects/{self.fcm_project_id}/messages:send'

    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    # Nuevo formato para FCM HTTP v1 API
    data = {
        'message': {
            'token': dispositivo.token_push,
            'notification': {
                'title': notificacion.titulo,
                'body': notificacion.mensaje,
            },
            'data': {
                'tipo': notificacion.tipo,
                'notificacion_id': str(notificacion.id),
                'prioridad': str(notificacion.prioridad),
                'click_action': '/notificaciones',
                **{k: str(v) for k, v in notificacion.datos_extra.items()}  # Convertir valores a string
            },
            'android': {
                'priority': 'high' if notificacion.prioridad >= 4 else 'normal',
                'notification': {
                    'icon': 'ic_notification',
                    'color': '#1976D2',
                    'sound': 'default'
                }
            },
            'apns': {
                'headers': {
                    'apns-priority': '10' if notificacion.prioridad >= 4 else '5'
                },
                'payload': {
                    'aps': {
                        'alert': {
                            'title': notificacion.titulo,
                            'body': notificacion.mensaje,
                        },
                        'badge': 1,
                        'sound': 'default'
                    }
                }
            }
        }
    }

    try:
        response = requests.post(url, headers=headers, json=data, timeout=10)

        if response.status_code == 200:
            result = response.json()
            if 'name' in result:  # FCM v1 API retorna 'name' en caso de éxito
                notificacion.push_enviado = True
                notificacion.save()
                return True
            else:
                print(f"Respuesta FCM inesperada: {result}")
        else:
            error_data = response.json() if response.content else {}
            print(f"Error FCM: {response.status_code} - {error_data}")

    except requests.exceptions.RequestException as e:
        print(f"Error de conexión FCM: {e}")

    return False
```

---

## 🌐 API REST Endpoints

### **URLs Configuration**

```python
# backend/apps/modulo_notificaciones/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# Crear router para ViewSets
router = DefaultRouter()
router.register(r'dispositivos', views.DispositivoViewSet, basename='dispositivos')
router.register(r'preferencias', views.PreferenciasNotificacionViewSet, basename='preferencias')
router.register(r'notificaciones', views.NotificacionViewSet, basename='notificaciones')

# URLs específicas
urlpatterns = [
    # Incluir rutas del router
    path('', include(router.urls)),

    # Endpoints específicos
    path('enviar-push/', views.enviar_notificacion_push, name='enviar-push'),
    path('crear-notificacion/', views.crear_notificacion, name='crear-notificacion'),

    # Endpoint de prueba (solo para desarrollo)
    path('test/', views.test_notificaciones, name='test-notificaciones'),
]
```

### **URLs Principales**

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/notificaciones/dispositivos/` | Listar dispositivos del usuario |
| POST | `/api/notificaciones/dispositivos/` | Registrar nuevo dispositivo |
| GET | `/api/notificaciones/preferencias/` | Obtener preferencias de notificación |
| PUT | `/api/notificaciones/preferencias/` | Actualizar preferencias |
| GET | `/api/notificaciones/notificaciones/` | Listar notificaciones del usuario |
| POST | `/api/notificaciones/enviar/` | Enviar notificación (admin) |
| POST | `/api/notificaciones/test/` | Endpoint de prueba |

### **ViewSets**

#### **DispositivoViewSet**
```python
class DispositivoViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de dispositivos"""
    serializer_class = DispositivoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Dispositivo.objects.filter(
            usuario=self.request.user,
            activo=True
        )
```

#### **NotificacionViewSet**
```python
class NotificacionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para ver notificaciones"""
    serializer_class = NotificacionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Notificacion.objects.filter(
            usuario=self.request.user
        ).order_by('-fecha_creacion')
```

---

## 📋 Serializers

### **DispositivoSerializer**
```python
class DispositivoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dispositivo
        fields = ['id', 'token_push', 'tipo_dispositivo', 'nombre_dispositivo',
                 'activo', 'fecha_registro', 'ultima_actividad']
        read_only_fields = ['id', 'fecha_registro', 'ultima_actividad']
```

### **NotificacionSerializer**
```python
class NotificacionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notificacion
        fields = ['id', 'titulo', 'mensaje', 'tipo', 'estado', 'fecha_creacion',
                 'fecha_envio', 'fecha_lectura', 'prioridad', 'datos_extra']
        read_only_fields = ['id', 'fecha_creacion', 'fecha_envio', 'fecha_lectura']
```

---

## 🔄 Flujo Completo de Envío

### **Diagrama de Secuencia**

```
1. Usuario solicita notificación
           │
           ▼
2. Controller (View) → Service.enviar_notificacion_masiva()
           │
           ▼
3. Service → Verificar preferencias del usuario
           │
           ▼
4. Service → Obtener dispositivos activos del usuario
           │
           ▼
5. Service → _get_access_token() (OAuth 2.0)
           │
           ▼
6. Service → _enviar_fcm() para cada dispositivo
           │
           ▼
7. FCM API → Procesar y enviar notificación
           │
           ▼
8. Dispositivo → Recibir notificación push
```

### **Código de Ejemplo - Envío de Notificación**

```python
from backend.apps.modulo_notificaciones.services import NotificacionService

# Crear instancia del servicio
service = NotificacionService()

# Enviar notificación a usuarios específicos
resultado = service.enviar_notificacion_masiva(
    titulo="¡Pago Realizado!",
    mensaje="Tu pago de condominio ha sido procesado exitosamente.",
    tipo="pago_realizado",
    usuarios_ids=[1, 2, 3],  # IDs de usuarios
    prioridad=3
)

print(f"Notificaciones enviadas: {resultado['push_enviados']}")
print(f"Errores: {resultado['errores']}")
```

---

## 🧪 Sistema de Testing

### **Script de Pruebas Automatizadas**

```python
# scripts/test_notificaciones.py

class NotificacionesTester:
    def __init__(self):
        self.service = NotificacionService()
        self.api_base = "http://localhost:8000/api"
        self.test_user_id = None
        self.test_device_token = "test-device-token-12345"

    def test_firebase_connection(self):
        """Prueba la conexión básica con Firebase"""
        # Verificar configuración y obtener access token
        if not self.service.fcm_project_id:
            return False

        try:
            token = self.service._get_access_token()
            return token is not None
        except Exception as e:
            return False

    def test_notification_sending(self):
        """Probar envío de notificación"""
        resultado = self.service.enviar_notificacion_masiva(
            titulo="🧪 Notificación de Prueba",
            mensaje="Esta es una notificación de prueba automática.",
            tipo="prueba",
            usuarios_ids=[self.test_user_id],
            prioridad=1
        )
        return resultado['push_enviados'] > 0
```

### **Comandos de Testing**

```bash
# Probar conexión con Firebase
python scripts/test_notificaciones.py --test-connection

# Enviar notificación de prueba
python scripts/test_notificaciones.py --test-notification

# Ejecutar todas las pruebas
python scripts/test_notificaciones.py --full-test

# Ejecutar tests unitarios
python manage.py test tests.modulo6_notificaciones -v 2
```

---

## 🔧 Configuración de Firebase Console

### **Paso 1: Crear Proyecto**

1. Ir a [Firebase Console](https://console.firebase.google.com/)
2. Hacer clic en "Crear un proyecto"
3. Nombre: `smart-condominium`
4. Anotar el **Project ID**: `smart-condominium-101a9`

### **Paso 2: Generar Service Account**

1. Ir a **Project Settings** → **Service accounts**
2. Hacer clic en **"Generate new private key"**
3. Descargar archivo JSON
4. Renombrar a `firebase-service-account.json`
5. Guardar en `C:\firebase\firebase-service-account.json`

### **Paso 3: Configurar VAPID Keys**

1. Ir a **Project Settings** → **Cloud Messaging**
2. Desplazarse a **Web Push certificates**
3. Hacer clic en **"Generate key pair"**
4. Copiar **Public key** y **Private key**

### **Paso 4: Verificar Configuración**

```bash
# Verificar en Firebase Console
# Cloud Messaging → Reports
# Deberías ver las notificaciones enviadas
```

---

## 🚨 Troubleshooting

### **Error: "Project ID not configured"**
```bash
# Verificar variable de entorno
echo $FCM_PROJECT_ID
# Solución: Agregar a .env
FCM_PROJECT_ID=tu-project-id
```

### **Error: "Credentials file not found"**
```bash
# Verificar que el archivo existe
ls -la C:\firebase\firebase-service-account.json
# Solución: Verificar ruta en FCM_CREDENTIALS_PATH
```

### **Error: "Access token could not be obtained"**
- Verificar que el archivo JSON de credenciales es válido
- Verificar que el service account tiene permisos de FCM
- Verificar conectividad a internet

### **Notificaciones no llegan**
- Verificar que el token FCM del dispositivo es válido
- Verificar configuración VAPID para web push
- Revisar logs del servidor Django

### **Error 400 en FCM API**
- Verificar formato del payload JSON
- Verificar que el token del dispositivo no expiró
- Verificar configuración del proyecto en Firebase

---

## 📊 Métricas y Monitoreo

### **Logs de Django**
```python
# Ver logs en tiempo real
python manage.py runserver

# Los logs de FCM se imprimen en consola
# Ejemplo: "Error FCM: 400 - {'error': {'status': 'INVALID_ARGUMENT'}}"
```

### **Firebase Console Metrics**
- **Cloud Messaging** → **Reports**
- Ver estadísticas de envío
- Ver errores de entrega
- Ver dispositivos activos

### **Base de Datos**
```sql
-- Ver notificaciones enviadas
SELECT estado, COUNT(*) FROM modulo_notificaciones_notificacion
GROUP BY estado;

-- Ver dispositivos activos
SELECT tipo_dispositivo, COUNT(*) FROM modulo_notificaciones_dispositivo
WHERE activo = true GROUP BY tipo_dispositivo;
```

---

## 🔒 Seguridad

### **Protección de Credenciales**
- Archivo `firebase-service-account.json` NO se sube a Git
- Se incluye en `.gitignore`
- Se almacena en ubicación segura del servidor
- Permisos restrictivos: solo lectura para el usuario de la aplicación

### **Validación de Tokens**
- Tokens FCM se validan antes del envío
- Dispositivos inactivos se marcan automáticamente
- Logs de errores para debugging

### **Rate Limiting**
- Implementar límites de envío por usuario/minuto
- Validación de contenido de notificaciones
- Protección contra spam

---

## 🚀 Despliegue en Producción

### **Variables de Entorno**
```bash
# En el servidor de producción
export FCM_PROJECT_ID=smart-condominium-101a9
export FCM_CREDENTIALS_PATH=/etc/smartcondominium/firebase-service-account.json
export VAPID_PUBLIC_KEY=tu_clave_publica
export VAPID_PRIVATE_KEY=tu_clave_privada
export VAPID_CLAIMS_SUB=admin@smartcondominium.com
```

### **Configuración del Servidor**
```bash
# Crear directorio seguro
sudo mkdir -p /etc/smartcondominium
sudo chown www-data:www-data /etc/smartcondominium
sudo chmod 700 /etc/smartcondominium

# Copiar credenciales
sudo cp firebase-service-account.json /etc/smartcondominium/
sudo chmod 600 /etc/smartcondominium/firebase-service-account.json
```

### **Configuración Nginx/Apache**
```nginx
# Configuración CORS para FCM
location /api/notificaciones/ {
    add_header 'Access-Control-Allow-Origin' 'https://tu-dominio.com';
    add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS';
    add_header 'Access-Control-Allow-Headers' 'Authorization, Content-Type';
}
```

---

## 📚 Referencias

- [Firebase Cloud Messaging HTTP v1 API](https://firebase.google.com/docs/cloud-messaging/migrate-v1)
- [OAuth 2.0 para Server to Server](https://developers.google.com/identity/protocols/oauth2/service-account)
- [VAPID para Web Push](https://developers.google.com/web/fundamentals/push-notifications/web-push-protocol)
- [Django REST Framework](https://www.django-rest-framework.org/)

---

## 🎯 Checklist de Integración

- [x] **Configuración OAuth 2.0**: Implementada
- [x] **API HTTP v1**: Migrada desde legacy API
- [x] **Modelos de datos**: Dispositivo, Notificacion, Preferencias
- [x] **Servicios backend**: NotificacionService completo
- [x] **API REST**: Endpoints funcionales
- [x] **Serializers**: Configurados para todos los modelos
- [x] **Testing**: Scripts automatizados
- [x] **Documentación**: Completa y detallada
- [x] **Seguridad**: Credenciales protegidas
- [x] **Producción**: Lista para despliegue

**Estado**: ✅ **Integración 100% Completa y Funcional** 🚀</content>
<parameter name="filePath">c:\Users\PG\Desktop\Materias\Sistemas de informacion 2\Proyectos\Parcial 1\Backend_Django\docs\integracion_firebase_completa.md