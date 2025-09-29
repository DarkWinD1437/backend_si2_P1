# Permisos y Roles - Módulo 8: Reportes y Analítica

## Descripción

Este documento describe el sistema de permisos y roles implementado en el Módulo de Reportes y Analítica, incluyendo niveles de acceso, restricciones y validaciones.

## Roles del Sistema

### 1. Administrador (admin)
**Permisos completos sobre todos los módulos**

- **Reportes Financieros**:
  - Crear, leer, actualizar, eliminar reportes
  - Generar reportes de cualquier tipo y período
  - Acceder a datos sensibles (montos, detalles personales)
  - Configurar filtros avanzados

- **Reportes de Seguridad**:
  - Acceso completo a todos los eventos de seguridad
  - Generar reportes de incidentes críticos
  - Ver datos de cámaras y sensores
  - Configurar alertas de seguridad

- **Reportes de Uso de Áreas**:
  - Acceso a todas las métricas de ocupación
  - Generar reportes históricos completos
  - Ver patrones de uso detallados
  - Configurar métricas personalizadas

- **Predicciones de Morosidad**:
  - Ejecutar modelos de IA sin restricciones
  - Acceder a datos históricos completos
  - Configurar parámetros de modelos
  - Ver predicciones de alto riesgo

### 2. Personal Administrativo (staff)
**Acceso limitado a reportes operativos**

- **Reportes Financieros**:
  - Leer reportes existentes
  - Generar reportes básicos (ingresos, egresos)
  - No puede acceder a datos de balances completos
  - Limitado a períodos recientes (últimos 6 meses)

- **Reportes de Seguridad**:
  - Leer reportes de incidentes no críticos
  - Generar reportes de eventos diarios
  - No puede acceder a datos de cámaras
  - Limitado a eventos de baja/mediana criticidad

- **Reportes de Uso de Áreas**:
  - Leer métricas de ocupación
  - Generar reportes semanales/mensuales
  - Acceso limitado a datos históricos (últimos 3 meses)

- **Predicciones de Morosidad**:
  - Solo puede ver predicciones existentes
  - No puede ejecutar nuevos modelos de IA
  - Acceso limitado a resultados de riesgo medio

### 3. Residente (resident)
**Acceso básico y limitado a información personal**

- **Reportes Financieros**:
  - Solo puede ver sus propios pagos y deudas
  - Acceso limitado a extractos personales
  - No puede generar reportes generales

- **Reportes de Seguridad**:
  - No tiene acceso a reportes de seguridad
  - Solo puede reportar incidentes personales

- **Reportes de Uso de Áreas**:
  - Puede ver disponibilidad de áreas comunes
  - Acceso limitado a estadísticas generales
  - No puede ver datos de uso específicos de otros residentes

- **Predicciones de Morosidad**:
  - No tiene acceso a predicciones
  - Solo puede ver su propio estado de cuenta

## Validaciones de Permisos

### Validaciones Automáticas

#### 1. Validación de Rol por Endpoint
```python
def has_required_role(user, required_roles):
    """Valida si el usuario tiene alguno de los roles requeridos"""
    return user.role in required_roles
```

#### 2. Validación de Propiedad de Datos
```python
def is_owner_or_admin(user, obj):
    """Valida si el usuario es propietario del objeto o administrador"""
    return obj.generado_por == user or user.role == 'admin'
```

#### 3. Validación de Período Temporal
```python
def validate_time_period(user, fecha_inicio, fecha_fin):
    """Valida límites temporales según rol del usuario"""
    if user.role == 'staff':
        max_period = timedelta(days=180)  # 6 meses
    elif user.role == 'resident':
        max_period = timedelta(days=30)  # 1 mes
    else:
        return True  # Admin sin límites

    period = fecha_fin - fecha_inicio
    return period <= max_period
```

### Restricciones por Endpoint

#### Reportes Financieros

| Endpoint | Admin | Staff | Resident |
|----------|-------|-------|----------|
| GET /list | ✅ | ✅ (limitado) | ❌ |
| POST /create | ✅ | ✅ (básico) | ❌ |
| POST /generar_reporte | ✅ | ✅ (básico) | ❌ |
| PUT /update | ✅ | ❌ | ❌ |
| DELETE /delete | ✅ | ❌ | ❌ |

#### Reportes de Seguridad

| Endpoint | Admin | Staff | Resident |
|----------|-------|-------|----------|
| GET /list | ✅ | ✅ (no crítico) | ❌ |
| POST /generar_reporte | ✅ | ✅ (diario) | ❌ |
| GET /detalle/{id} | ✅ | ✅ (no crítico) | ❌ |

#### Reportes de Uso de Áreas

| Endpoint | Admin | Staff | Resident |
|----------|-------|-------|----------|
| GET /list | ✅ | ✅ | ✅ (general) |
| POST /generar_reporte | ✅ | ✅ | ❌ |
| GET /estadisticas | ✅ | ✅ | ✅ (básico) |

#### Predicciones de Morosidad

| Endpoint | Admin | Staff | Resident |
|----------|-------|-------|----------|
| GET /list | ✅ | ✅ (medio riesgo) | ❌ |
| POST /generar_prediccion | ✅ | ❌ | ❌ |
| GET /prediccion/{id} | ✅ | ✅ (medio riesgo) | ❌ |

## Filtros Automáticos por Rol

### Filtros de Queryset

#### Para Staff
```python
def filter_by_role(self, queryset, user):
    if user.role == 'staff':
        # Limitar a últimos 6 meses
        six_months_ago = timezone.now() - timedelta(days=180)
        queryset = queryset.filter(fecha_generacion__gte=six_months_ago)

        # Filtrar datos sensibles
        queryset = queryset.exclude(tipo='balance_completo')

    return queryset
```

#### Para Residentes
```python
def filter_resident_data(self, queryset, user):
    if user.role == 'resident':
        # Solo datos relacionados con el residente
        queryset = queryset.filter(
            Q(residente=user) |
            Q(generado_por=user)
        ).exclude(tipo__in=['balance_completo', 'seguridad'])

    return queryset
```

## Validaciones de Datos Sensibles

### Campos Restringidos

#### Información Financiera Sensible
- Montos totales de balances completos
- Detalles de pagos de otros residentes
- Información de morosidad de terceros

#### Información de Seguridad
- Datos de cámaras y sensores
- Incidentes críticos o personales
- Ubicaciones exactas de eventos

#### Información Personal
- Datos demográficos completos
- Historial de uso detallado
- Predicciones de riesgo individual

### Enmascaramiento de Datos

#### Para Staff
```python
def mask_sensitive_data(data, user):
    if user.role == 'staff':
        # Enmascarar montos específicos
        if 'monto_total' in data:
            data['monto_total'] = "***.***"

        # Ocultar datos personales
        if 'residentes' in data:
            for residente in data['residentes']:
                residente['cedula'] = "XXX-XXXXXXX-X"
                residente['telefono'] = "XXX-XXX-XXXX"

    return data
```

## Rate Limiting por Rol

### Límites de Uso

| Rol | Reportes/Hora | Predicciones/Día | Consultas/Minuto |
|-----|---------------|------------------|-------------------|
| Admin | 50 | 20 | 100 |
| Staff | 10 | 5 | 30 |
| Resident | 2 | 0 | 10 |

### Implementación
```python
@ratelimit(key='user', rate='10/h', method='POST')
def generar_reporte(self, request):
    if request.user.role == 'resident':
        return Response(
            {"error": "Residentes no pueden generar reportes"},
            status=status.HTTP_403_FORBIDDEN
        )
    # ... resto de la lógica
```

## Auditoría de Acceso

### Registro de Acciones

#### Acciones Auditadas
- Generación de reportes
- Acceso a datos sensibles
- Modificación de configuraciones
- Ejecución de modelos de IA

#### Log de Auditoría
```python
def log_access(user, action, resource, details=None):
    AuditLog.objects.create(
        usuario=user,
        accion=action,
        recurso=resource,
        detalles=details,
        timestamp=timezone.now(),
        ip_address=get_client_ip(request)
    )
```

### Alertas de Seguridad

#### Umbrales de Alerta
- Múltiples accesos fallidos a datos sensibles
- Generación excesiva de reportes
- Acceso a predicciones de IA fuera de horario laboral

## Manejo de Errores de Permisos

### Mensajes de Error Estandarizados

#### Sin Permisos
```json
{
  "error": "No tienes permisos suficientes para realizar esta acción",
  "required_role": "admin",
  "user_role": "staff"
}
```

#### Datos No Accesibles
```json
{
  "error": "Los datos solicitados no están disponibles para tu rol",
  "reason": "informacion_sensible",
  "contact_admin": true
}
```

#### Límite Excedido
```json
{
  "error": "Has excedido el límite de uso permitido",
  "limit_type": "reportes_por_hora",
  "current_usage": 12,
  "limit": 10,
  "reset_time": "2024-09-01T12:00:00Z"
}
```

## Configuración de Permisos

### Variables de Entorno
```bash
# Niveles de acceso
ANALYTICS_ADMIN_ROLES=admin
ANALYTICS_STAFF_ROLES=staff,manager
ANALYTICS_RESIDENT_ROLES=resident,owner

# Límites de rate limiting
RATE_LIMIT_ADMIN=50/h
RATE_LIMIT_STAFF=10/h
RATE_LIMIT_RESIDENT=2/h

# Períodos de retención
DATA_RETENTION_ADMIN=unlimited
DATA_RETENTION_STAFF=180_days
DATA_RETENTION_RESIDENT=30_days
```

### Configuración en Settings
```python
ANALYTICS_PERMISSIONS = {
    'admin': {
        'can_generate_reports': True,
        'can_access_sensitive_data': True,
        'data_retention_days': None,
        'rate_limits': {'reports': '50/h', 'predictions': '20/d'}
    },
    'staff': {
        'can_generate_reports': True,
        'can_access_sensitive_data': False,
        'data_retention_days': 180,
        'rate_limits': {'reports': '10/h', 'predictions': '5/d'}
    },
    'resident': {
        'can_generate_reports': False,
        'can_access_sensitive_data': False,
        'data_retention_days': 30,
        'rate_limits': {'reports': '2/h', 'predictions': '0/d'}
    }
}
```

## Pruebas de Permisos

### Casos de Prueba

#### Validación de Roles
- [ ] Admin puede acceder a todos los endpoints
- [ ] Staff puede generar reportes básicos pero no sensibles
- [ ] Resident solo puede ver información personal
- [ ] Usuario sin rol es rechazado

#### Rate Limiting
- [ ] Límites se aplican correctamente por rol
- [ ] Mensajes de error informativos
- [ ] Reset de límites funciona

#### Filtros de Datos
- [ ] Datos sensibles se enmascaran para staff
- [ ] Residentes solo ven sus propios datos
- [ ] Filtros temporales se aplican correctamente

### Comando de Pruebas
```bash
# Ejecutar pruebas de permisos
python manage.py test analytics.tests.test_permissions --verbosity=2

# Ejecutar pruebas de rate limiting
python manage.py test analytics.tests.test_rate_limiting --verbosity=2
```