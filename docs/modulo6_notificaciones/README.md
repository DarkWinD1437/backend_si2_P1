# Módulo 6: Notificaciones - SmartCondominium

## Descripción General

El módulo de notificaciones permite enviar notificaciones push, email y SMS a los usuarios del condominio. Incluye gestión de dispositivos, preferencias de notificación por usuario y un sistema completo de envío de notificaciones.

## ⚠️ ACTUALIZACIÓN IMPORTANTE: FCM HTTP v1 API

El módulo ha sido actualizado para usar la nueva **API HTTP v1 de Firebase Cloud Messaging** que requiere autenticación OAuth 2.0 en lugar de la server key legacy.

## Características Principales

- **Notificaciones Push**: Soporte para FCM HTTP v1 (Android, iOS, Web)
- **Preferencias por Usuario**: Configuración granular por tipo de notificación
- **Múltiples Canales**: Push, Email y SMS
- **Gestión de Dispositivos**: Registro y gestión de tokens de dispositivos
- **Historial Completo**: Registro de todas las notificaciones enviadas
- **Priorización**: Sistema de prioridades para notificaciones críticas

## Estructura del Módulo

```
modulo6_notificaciones/
├── README.md                           # Este archivo
├── documentacion_completa.md          # Documentación técnica completa
├── endpoints_api.md                   # Referencia de endpoints
├── integracion_frontend.md            # Guías de integración React/Flutter
├── configuracion.md                   # Configuración legacy (obsoleta)
├── configuracion_fcm_v1.md           # ✅ Configuración FCM HTTP v1 (actual)
└── testing/
    └── test_notificaciones.py         # Tests completos del módulo
```

## Archivos Importantes

- **Código Backend**: `backend/apps/modulo_notificaciones/`
- **Tests**: `tests/modulo6_notificaciones/test_notificaciones.py`
- **Documentación**: `docs/modulo6_notificaciones/`

## Inicio Rápido

### 1. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 2. Configurar Variables de Entorno
```env
# Firebase Cloud Messaging (API HTTP v1 - OAuth 2.0)
FCM_PROJECT_ID=your-firebase-project-id
FCM_CREDENTIALS_PATH=/path/to/your/service-account.json
VAPID_PUBLIC_KEY=your-vapid-public-key-here
VAPID_PRIVATE_KEY=your-vapid-private-key-here
VAPID_CLAIMS_SUB=email@example.com
```

### 3. Configurar Firebase
Sigue la **[Guía Completa de Configuración Firebase](guia_configuracion_firebase.md)** para configurar tu proyecto de Firebase paso a paso.

### 4. Probar el Sistema
```bash
# Ejecutar pruebas completas
python scripts/test_notificaciones.py --full-test

# O probar componentes individuales
python scripts/test_notificaciones.py --test-connection
python scripts/test_notificaciones.py --test-notification
```

### 5. Probar API con Postman
```bash
# Endpoint de prueba (sin autenticación)
POST http://localhost:8000/api/notificaciones/test/
Content-Type: application/json

{
  "titulo": "¡Hola desde Postman!",
  "mensaje": "Probando notificaciones push",
  "tipo": "prueba"
}
```

### 6. Ver Documentación
- 📖 **[Configuración FCM v1](configuracion_fcm_v1.md)** - Guía técnica de FCM
- � **[Integración Firebase Completa](../../integracion_firebase_completa.md)** - Documentación detallada de toda la integración
- �🚀 **[Guía Completa Firebase](guia_configuracion_firebase.md)** - Configuración paso a paso
- 🔌 **[Integración Frontend](integracion_frontend.md)** - React y Flutter
- 📋 **[Endpoints API](endpoints_api.md)** - Referencia completa

## Herramientas de Testing y Desarrollo

### Script de Pruebas Automatizadas
```bash
# Ubicación: scripts/test_notificaciones.py

# Probar todo el sistema
python scripts/test_notificaciones.py --full-test

# Probar solo conexión con Firebase
python scripts/test_notificaciones.py --test-connection

# Enviar notificación de prueba
python scripts/test_notificaciones.py --test-notification

# Registrar dispositivo de prueba
python scripts/test_notificaciones.py --test-device
```

### Endpoint de Prueba API
```bash
# POST /api/notificaciones/test/
# Endpoint sin autenticación para testing rápido

curl -X POST http://localhost:8000/api/notificaciones/test/ \
  -H "Content-Type: application/json" \
  -d '{
    "titulo": "¡Prueba desde cURL!",
    "mensaje": "Notificación enviada correctamente",
    "tipo": "prueba"
  }'
```

### Tests Unitarios
```bash
# Ejecutar solo tests del módulo
python manage.py test tests.modulo6_notificaciones -v 2

# Ejecutar con coverage
coverage run --source='backend.apps.modulo_notificaciones' manage.py test tests.modulo6_notificaciones
coverage report
```

## Endpoints Principales

- `POST /api/notificaciones/dispositivos/` - Registrar dispositivo
- `GET /api/notificaciones/preferencias/` - Obtener preferencias
- `GET /api/notificaciones/` - Listar notificaciones
- `POST /api/notificaciones/enviar/` - Enviar notificación (admin)

## Próximos Pasos

- [ ] Implementar envío real de emails
- [ ] Integrar servicio de SMS
- [ ] Agregar templates de notificación personalizables
- [ ] Implementar notificaciones programadas
- [ ] Agregar analytics de notificaciones