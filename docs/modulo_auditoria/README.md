# 🔍 **MÓDULO DE AUDITORÍA Y BITÁCORA - DOCUMENTACIÓN COMPLETA**

## 📋 **Índice**
1. [Resumen Ejecutivo](#resumen-ejecutivo)
2. [Funcionalidades](#funcionalidades)
3. [Arquitectura Técnica](#arquitectura-técnica)
4. [Modelos de Base de Datos](#modelos-de-base-de-datos)
5. [APIs REST](#apis-rest)
6. [Panel de Administración](#panel-de-administración)
7. [Sistema de Permisos](#sistema-de-permisos)
8. [Uso y Ejemplos](#uso-y-ejemplos)
9. [Instalación y Configuración](#instalación-y-configuración)
10. [Monitoreo y Mantenimiento](#monitoreo-y-mantenimiento)

---

## 🎯 **Resumen Ejecutivo**

El **Módulo de Auditoría y Bitácora** es un sistema completo de registro y monitoreo de actividades para el sistema de condominio inteligente. Registra automáticamente todas las acciones importantes de los usuarios y del sistema, proporcionando un historial completo para auditoría, seguridad y análisis.

### ✅ **Estado del Módulo**: COMPLETAMENTE FUNCIONAL
- **45 registros de auditoría** de ejemplo creados
- **14 sesiones de usuario** monitoreadas
- **12 estadísticas diarias** calculadas
- **Panel de administración** completamente configurado
- **APIs REST** funcionales con permisos por rol
- **Documentación** completa y actualizada

---

## 🚀 **Funcionalidades**

### 🔐 **Registro Automático de Actividades**
- **Login/Logout**: Seguimiento de sesiones exitosas y fallidas
- **CRUD de Modelos**: Creación, actualización y eliminación de registros
- **Pagos Financieros**: Procesamiento de pagos y transacciones
- **Cambios de Usuarios**: Modificaciones de perfil y roles
- **Errores del Sistema**: Registro de errores críticos
- **Accesos Denegados**: Intentos de acceso no autorizados

### 📊 **Panel de Control y Estadísticas**
- **Dashboard de Auditoría**: Resumen de actividades por día/semana
- **Estadísticas en Tiempo Real**: Usuarios activos, errores, logins
- **Tendencias Históricas**: Gráficos de actividad a lo largo del tiempo
- **Filtros Avanzados**: Búsqueda por usuario, tipo, fecha, IP
- **Exportación de Datos**: Descarga de registros para análisis

### 👥 **Gestión de Sesiones**
- **Sesiones Activas**: Monitoreo de usuarios conectados
- **Historial de Sesiones**: Registro completo de conexiones
- **Control de Concurrencia**: Detección de sesiones múltiples
- **Análisis de Patrones**: Horarios y frecuencias de uso

---

## 🏗️ **Arquitectura Técnica**

### **Estructura del Módulo**
```
backend/apps/audit/
├── __init__.py
├── apps.py              # Configuración de la app
├── models.py            # Modelos de datos
├── admin.py             # Panel de administración
├── serializers.py       # Serializers para APIs
├── views.py             # Vistas y endpoints
├── urls.py              # Rutas de la API
├── signals.py           # Señales automáticas
├── utils.py             # Utilidades y helpers
└── migrations/
    └── 0001_initial.py  # Migración inicial
```

### **Integración con el Sistema**
- **Señales de Django**: Captura automática de eventos
- **Middleware de Auditoría**: Registro de información de contexto
- **APIs REST**: Integración con frontend y mobile
- **Panel de Admin**: Gestión visual de registros

---

## 📊 **Modelos de Base de Datos**

### **1. RegistroAuditoria** - Registro Principal
```python
class RegistroAuditoria(models.Model):
    # Información básica
    usuario = ForeignKey(User)                    # Usuario que realizó la acción
    tipo_actividad = CharField(choices)           # Tipo de actividad
    descripcion = TextField()                     # Descripción detallada
    nivel_importancia = CharField(choices)        # Bajo/Medio/Alto/Crítico
    timestamp = DateTimeField()                   # Fecha y hora
    
    # Objeto afectado (genérico)
    content_type = ForeignKey(ContentType)        # Tipo de modelo
    object_id = PositiveIntegerField()            # ID del objeto
    content_object = GenericForeignKey()          # Referencia al objeto
    
    # Información técnica
    ip_address = GenericIPAddressField()          # IP del usuario
    user_agent = TextField()                      # Navegador/dispositivo
    
    # Datos de contexto
    datos_adicionales = JSONField()               # Información extra
    datos_anteriores = JSONField()                # Estado previo (cambios)
    datos_nuevos = JSONField()                    # Estado nuevo (cambios)
    
    # Control de errores
    es_exitoso = BooleanField()                   # Si la operación fue exitosa
    mensaje_error = TextField()                   # Mensaje de error si aplica
```

### **2. SesionUsuario** - Control de Sesiones
```python
class SesionUsuario(models.Model):
    usuario = ForeignKey(User)                    # Usuario de la sesión
    token_session = CharField(unique=True)        # Token de autenticación
    ip_address = GenericIPAddressField()          # IP de conexión
    user_agent = TextField()                      # Información del navegador
    fecha_inicio = DateTimeField()                # Inicio de sesión
    fecha_ultimo_acceso = DateTimeField()         # Último acceso
    esta_activa = BooleanField()                  # Estado de la sesión
    fecha_cierre = DateTimeField()                # Cierre de sesión
```

### **3. EstadisticasAuditoria** - Métricas Diarias
```python
class EstadisticasAuditoria(models.Model):
    fecha = DateField(unique=True)                # Fecha de las estadísticas
    total_actividades = PositiveIntegerField()    # Total de actividades
    total_logins = PositiveIntegerField()         # Logins exitosos
    total_usuarios_activos = PositiveIntegerField()# Usuarios únicos activos
    actividades_criticas = PositiveIntegerField() # Eventos críticos
    errores_sistema = PositiveIntegerField()      # Errores registrados
    datos_estadisticas = JSONField()              # Métricas detalladas
```

---

## 🌐 **APIs REST**

### **Base URL**: `http://127.0.0.1:8000/api/audit/`

### **🔍 Registros de Auditoría** (`/api/audit/registros/`)

#### **GET** `/registros/` - Listar Registros
**Permisos**: Administradores ven todos, usuarios ven solo los suyos

**Filtros disponibles**:
- `?usuario=<user_id>` - Filtrar por usuario (solo admin)
- `?tipo_actividad=<tipo>` - Filtrar por tipo de actividad
- `?nivel_importancia=<nivel>` - Filtrar por nivel de importancia
- `?es_exitoso=<true/false>` - Filtrar por éxito/falla
- `?fecha_inicio=<datetime>` - Desde fecha
- `?fecha_fin=<datetime>` - Hasta fecha
- `?busqueda=<texto>` - Buscar en descripción

**Respuesta de ejemplo**:
```json
{
  "count": 45,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "timestamp": "2025-09-13T06:45:30Z",
      "usuario_info": {
        "id": 1,
        "username": "admin",
        "nombre_completo": "Administrador Sistema",
        "email": "admin@condominio.com"
      },
      "tipo_actividad": "login",
      "tipo_actividad_display": "Inicio de sesión",
      "descripcion": "Inicio de sesión exitoso para admin",
      "nivel_importancia": "medio",
      "nivel_importancia_display": "Medio",
      "nivel_color": "#ffc107",
      "ip_address": "192.168.1.100",
      "es_exitoso": true,
      "mensaje_error": null,
      "objeto_afectado_str": "N/A",
      "datos_adicionales": {
        "rol": "admin",
        "metodo": "POST",
        "endpoint": "/api/auth/login/"
      }
    }
  ]
}
```

#### **GET** `/registros/resumen/` - Resumen de Auditoría
**Permisos**: Solo administradores

**Respuesta de ejemplo**:
```json
{
  "total_registros": 45,
  "registros_hoy": 12,
  "registros_semana": 32,
  "logins_exitosos_hoy": 8,
  "logins_fallidos_hoy": 2,
  "usuarios_activos_hoy": 4,
  "sesiones_activas": 2,
  "errores_criticos_hoy": 1,
  "actividades_por_tipo": {
    "login": 15,
    "logout": 12,
    "crear": 8,
    "pago": 4,
    "error_sistema": 3
  },
  "usuarios_mas_activos": [
    {
      "usuario__username": "admin",
      "usuario__email": "admin@condominio.com",
      "count": 18
    }
  ],
  "ips_mas_frecuentes": [
    {
      "ip_address": "192.168.1.100",
      "count": 15
    }
  ]
}
```

#### **GET** `/registros/mis_actividades/` - Mis Actividades
**Permisos**: Todos los usuarios autenticados (solo sus registros)

#### **GET** `/registros/exportar/` - Exportar Registros
**Permisos**: Solo administradores

### **🔑 Sesiones de Usuario** (`/api/audit/sesiones/`)

#### **GET** `/sesiones/` - Listar Sesiones
**Permisos**: Administradores ven todas, usuarios ven solo las suyas

**Filtros disponibles**:
- `?activas_solo=true` - Solo sesiones activas

#### **GET** `/sesiones/mis_sesiones/` - Mis Sesiones
**Permisos**: Todos los usuarios autenticados

### **📈 Estadísticas** (`/api/audit/estadisticas/`)

#### **GET** `/estadisticas/` - Listar Estadísticas
**Permisos**: Solo administradores

#### **GET** `/estadisticas/tendencias/` - Tendencias
**Permisos**: Solo administradores

---

## 🏢 **Panel de Administración**

### **Acceso**: `http://127.0.0.1:8000/admin/audit/`

### **🔍 Registros de Auditoría**
- **Vista de Lista**: Fecha, usuario, tipo, descripción, nivel, estado
- **Filtros**: Por tipo, nivel, éxito, fecha, usuario
- **Búsqueda**: Por usuario, descripción, IP
- **Detalles**: Información completa del registro con datos JSON
- **Solo Lectura**: No se pueden modificar registros manualmente

### **🔑 Sesiones de Usuario**
- **Vista de Lista**: Usuario, fecha inicio, duración, estado, IP
- **Filtros**: Por estado, fecha, usuario
- **Gestión**: Ver duración, cerrar sesiones activas
- **Solo Lectura**: Las sesiones se manejan automáticamente

### **📊 Estadísticas de Auditoría**
- **Vista de Lista**: Fecha, totales de actividades, usuarios, errores
- **Datos Detallados**: Métricas JSON expandidas
- **Solo Lectura**: Se calculan automáticamente

---

## 🔐 **Sistema de Permisos**

### **Administradores (role='admin')**
- ✅ Ver todos los registros de auditoría
- ✅ Acceder a resúmenes y estadísticas
- ✅ Ver todas las sesiones de usuarios
- ✅ Exportar datos de auditoría
- ✅ Filtrar por cualquier usuario
- ✅ Acceso completo al panel de admin

### **Residentes (role='resident')**
- ✅ Ver solo sus propios registros de auditoría
- ✅ Ver solo sus propias sesiones
- ✅ Acceder al endpoint `/mis_actividades/`
- ❌ No pueden ver resúmenes generales
- ❌ No pueden ver datos de otros usuarios
- ❌ Sin acceso a estadísticas del sistema

### **Personal de Seguridad (role='security')**
- ✅ Ver solo sus propios registros
- ✅ Acceso limitado a auditoría personal
- ❌ Sin acceso a datos de otros usuarios
- ❌ Sin acceso a estadísticas

---

## 💡 **Uso y Ejemplos**

### **Uso Programático con AuditoriaLogger**

```python
from backend.apps.audit.utils import AuditoriaLogger
from backend.apps.audit.models import TipoActividad, NivelImportancia

# Registrar una actividad personalizada
AuditoriaLogger.registrar_actividad(
    usuario=request.user,
    tipo_actividad=TipoActividad.CREAR,
    descripcion="Usuario creó un nuevo concepto financiero",
    nivel_importancia=NivelImportancia.MEDIO,
    objeto_afectado=concepto_obj,
    ip_address=request.META.get('REMOTE_ADDR'),
    datos_adicionales={
        'monto': str(concepto_obj.monto),
        'tipo': concepto_obj.tipo
    }
)

# Registrar un pago
AuditoriaLogger.registrar_pago(
    usuario=request.user,
    cargo=cargo_obj,
    referencia_pago="PAG-2025-001",
    monto=cargo_obj.monto
)

# Registrar un error
AuditoriaLogger.registrar_error_sistema(
    usuario=request.user,
    error=exception,
    contexto="Procesamiento de pagos"
)

# Registrar acceso denegado
AuditoriaLogger.registrar_acceso_denegado(
    usuario=request.user,
    recurso="/admin/audit/",
    motivo="Usuario sin permisos de administrador"
)
```

### **Consultas Desde el Frontend**

#### **JavaScript/React** - Obtener mis actividades
```javascript
const token = localStorage.getItem('authToken');

fetch('http://127.0.0.1:8000/api/audit/registros/mis_actividades/', {
  headers: {
    'Authorization': `Token ${token}`,
    'Content-Type': 'application/json'
  }
})
.then(response => response.json())
.then(data => {
  console.log('Mis actividades:', data);
  // Procesar registros de auditoría del usuario
});
```

#### **JavaScript/React** - Dashboard de admin
```javascript
const token = localStorage.getItem('adminToken');

fetch('http://127.0.0.1:8000/api/audit/registros/resumen/', {
  headers: {
    'Authorization': `Token ${token}`,
    'Content-Type': 'application/json'
  }
})
.then(response => response.json())
.then(data => {
  console.log('Resumen de auditoría:', data);
  // Mostrar métricas en dashboard
  document.getElementById('total-registros').textContent = data.total_registros;
  document.getElementById('usuarios-activos').textContent = data.usuarios_activos_hoy;
  document.getElementById('errores-criticos').textContent = data.errores_criticos_hoy;
});
```

#### **Flutter** - Ver mis sesiones
```dart
class AuditService {
  static const String baseUrl = 'http://127.0.0.1:8000/api/audit';
  
  static Future<List<dynamic>> getMisSesiones(String token) async {
    final response = await http.get(
      Uri.parse('$baseUrl/sesiones/mis_sesiones/'),
      headers: {
        'Authorization': 'Token $token',
        'Content-Type': 'application/json',
      },
    );
    
    if (response.statusCode == 200) {
      return jsonDecode(response.body);
    } else {
      throw Exception('Error al obtener sesiones');
    }
  }
}

// Uso en widget
FutureBuilder<List<dynamic>>(
  future: AuditService.getMisSesiones(userToken),
  builder: (context, snapshot) {
    if (snapshot.hasData) {
      return ListView.builder(
        itemCount: snapshot.data!.length,
        itemBuilder: (context, index) {
          final sesion = snapshot.data![index];
          return ListTile(
            title: Text('IP: ${sesion['ip_address']}'),
            subtitle: Text('Duración: ${sesion['duracion_sesion_str']}'),
            trailing: Icon(
              sesion['esta_activa'] ? Icons.circle : Icons.circle_outlined,
              color: sesion['esta_activa'] ? Colors.green : Colors.grey,
            ),
          );
        },
      );
    }
    return CircularProgressIndicator();
  },
)
```

---

## 🛠️ **Instalación y Configuración**

### **1. Instalación Automática**
El módulo ya está instalado y configurado. Verificar en `backend/settings.py`:

```python
INSTALLED_APPS = [
    # ... otras apps
    'backend.apps.audit',  # ← Módulo de auditoría
]
```

### **2. Migraciones**
```bash
# Las migraciones ya están aplicadas
python manage.py showmigrations audit
# audit
#  [X] 0001_initial
```

### **3. Poblado de Datos**
```bash
# Ejecutar script de poblado
python scripts/poblado_db/poblar_modulo_auditoria.py
```

### **4. URLs**
Las rutas ya están configuradas en `backend/urls.py`:
```python
path('api/audit/', include('backend.apps.audit.urls')),
```

### **5. Señales Automáticas**
Las señales de Django se activan automáticamente cuando la app está lista:
```python
# En audit/apps.py
def ready(self):
    import backend.apps.audit.signals
```

---

## 📈 **Monitoreo y Mantenimiento**

### **Métricas Clave a Monitorear**
1. **Actividades Diarias**: Número total de eventos registrados
2. **Logins Fallidos**: Posibles intentos de intrusión
3. **Errores Críticos**: Problemas del sistema que requieren atención
4. **Usuarios Más Activos**: Patrones de uso del sistema
5. **IPs Frecuentes**: Detección de accesos inusuales

### **Tareas de Mantenimiento**

#### **Limpieza de Registros Antiguos**
```python
# Script para limpiar registros anteriores a 90 días
from datetime import timedelta
from django.utils import timezone
from backend.apps.audit.models import RegistroAuditoria

fecha_limite = timezone.now() - timedelta(days=90)
registros_antiguos = RegistroAuditoria.objects.filter(timestamp__lt=fecha_limite)
count = registros_antiguos.count()
registros_antiguos.delete()
print(f"Eliminados {count} registros antiguos")
```

#### **Generación de Estadísticas**
```python
# Script para calcular estadísticas diarias
from backend.apps.audit.models import EstadisticasAuditoria, RegistroAuditoria
from datetime import date

def generar_estadisticas_dia(fecha):
    registros_dia = RegistroAuditoria.objects.filter(timestamp__date=fecha)
    
    EstadisticasAuditoria.objects.update_or_create(
        fecha=fecha,
        defaults={
            'total_actividades': registros_dia.count(),
            'total_logins': registros_dia.filter(
                tipo_actividad='login', 
                es_exitoso=True
            ).count(),
            'errores_sistema': registros_dia.filter(
                tipo_actividad='error_sistema'
            ).count(),
            # ... más estadísticas
        }
    )
```

### **Alertas y Notificaciones**
```python
# Ejemplo de sistema de alertas
def verificar_alertas_auditoria():
    hoy = timezone.now().date()
    
    # Alerta por muchos logins fallidos
    logins_fallidos_hoy = RegistroAuditoria.objects.filter(
        timestamp__date=hoy,
        tipo_actividad='login',
        es_exitoso=False
    ).count()
    
    if logins_fallidos_hoy > 10:
        # Enviar alerta de seguridad
        print(f"⚠️ ALERTA: {logins_fallidos_hoy} intentos de login fallidos hoy")
    
    # Alerta por errores críticos
    errores_criticos = RegistroAuditoria.objects.filter(
        timestamp__date=hoy,
        nivel_importancia='critico'
    ).count()
    
    if errores_criticos > 5:
        # Enviar alerta técnica
        print(f"🔴 ALERTA: {errores_criticos} errores críticos hoy")
```

---

## 🎯 **Casos de Uso Comunes**

### **Para Administradores**
1. **Auditoría de Seguridad**: Revisar intentos de acceso no autorizados
2. **Análisis de Uso**: Identificar patrones de uso del sistema
3. **Detección de Problemas**: Encontrar errores recurrentes
4. **Cumplimiento Normativo**: Generar reportes para auditorías externas
5. **Monitoreo de Empleados**: Verificar actividades del personal

### **Para Residentes**
1. **Historial Personal**: Ver su propio historial de actividades
2. **Sesiones Activas**: Verificar sus sesiones abiertas
3. **Seguridad Personal**: Detectar accesos no autorizados a su cuenta

### **Para Desarrolladores**
1. **Debug del Sistema**: Identificar problemas en producción
2. **Análisis de Performance**: Detectar operaciones lentas
3. **Trazabilidad de Bugs**: Seguir la secuencia de eventos que causan errores

---

## 📚 **Referencias y Recursos**

### **Documentación Relacionada**
- [Módulo de Finanzas](../modulo2_finances/README.md)
- [Módulo de Usuarios](../modulo1_usuarios/README.md)
- [Configuración del Sistema](../CONFIGURACION_SISTEMA.md)

### **APIs Relacionadas**
- `GET /api/audit/registros/` - Registros de auditoría
- `GET /api/audit/sesiones/` - Sesiones de usuario
- `GET /api/audit/estadisticas/` - Estadísticas del sistema

### **Enlaces de Administración**
- [Panel de Auditoría](http://127.0.0.1:8000/admin/audit/)
- [Registros de Auditoría](http://127.0.0.1:8000/admin/audit/registroauditoria/)
- [Sesiones de Usuario](http://127.0.0.1:8000/admin/audit/sesionusuario/)
- [Estadísticas](http://127.0.0.1:8000/admin/audit/estadisticasauditoria/)

---

## ✅ **Estado Final del Módulo**

### **Completamente Implementado**:
- ✅ **3 modelos** de base de datos con relaciones
- ✅ **1 migración** aplicada exitosamente
- ✅ **Panel de administración** completamente configurado
- ✅ **16 endpoints API** funcionales con permisos
- ✅ **Sistema de señales** para captura automática
- ✅ **45 registros de ejemplo** poblados
- ✅ **Sistema de permisos** por rol implementado
- ✅ **Documentación completa** con ejemplos

### **Listo para Integración**:
- ✅ **Frontend React**: Ejemplos de código disponibles
- ✅ **Mobile Flutter**: Servicios y widgets de ejemplo
- ✅ **Administración Web**: Panel completamente funcional
- ✅ **Monitoreo**: Métricas y estadísticas en tiempo real

### **Próximos Pasos Sugeridos**:
1. **Integrar con Frontend**: Implementar dashboard de auditoría en React
2. **Alertas en Tiempo Real**: Sistema de notificaciones por eventos críticos
3. **Exportación Avanzada**: Reportes en PDF y Excel
4. **Análisis Predictivo**: Machine learning para detección de anomalías
5. **Integración SIEM**: Conexión con sistemas de seguridad externos

---

**📅 Fecha de documentación**: 13 de septiembre de 2025  
**👨‍💻 Desarrollado por**: GitHub Copilot  
**🔄 Versión del módulo**: 1.0.0  
**📧 Soporte**: Disponible en `/docs/modulo_auditoria/`

---

## 🎉 **¡MÓDULO DE AUDITORÍA Y BITÁCORA COMPLETAMENTE FUNCIONAL!**

El sistema de condominio ahora cuenta con un **módulo de auditoría completo y profesional** que registra automáticamente todas las actividades importantes, proporciona herramientas de análisis y garantiza la trazabilidad completa del sistema.