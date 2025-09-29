# Permisos y Roles - Módulo 7: Gestión de Mantenimiento

## Sistema de Roles

El módulo utiliza el sistema de roles definido en el modelo `User` del módulo de usuarios.

### Roles Disponibles
- `admin`: Administrador del sistema
- `resident`: Residente del condominio
- `maintenance`: Personal de mantenimiento
- `security`: Personal de seguridad

## Matriz de Permisos

### Solicitudes de Mantenimiento

| Acción | Admin | Resident | Maintenance | Security |
|--------|-------|----------|-------------|----------|
| **Listar** | ✅ Todas | ✅ Propias | ✅ Todas | ✅ Todas (solo lectura) |
| **Crear** | ✅ | ✅ | ❌ | ❌ |
| **Ver Detalle** | ✅ Todas | ✅ Propias | ✅ Todas | ✅ Todas (solo lectura) |
| **Actualizar** | ✅ Todas | ❌ | ❌ | ❌ |
| **Eliminar** | ✅ Todas | ❌ | ❌ | ❌ |
| **Asignar Tarea** | ✅ | ❌ | ✅ | ❌ |

### Tareas de Mantenimiento

| Acción | Admin | Resident | Maintenance | Security |
|--------|-------|----------|-------------|----------|
| **Listar** | ✅ Todas | ✅ De sus solicitudes | ✅ Asignadas | ✅ Todas (solo lectura) |
| **Ver Detalle** | ✅ Todas | ✅ De sus solicitudes | ✅ Asignadas | ✅ Todas (solo lectura) |
| **Actualizar** | ✅ Todas | ❌ | ❌ | ❌ |
| **Eliminar** | ✅ Todas | ❌ | ❌ | ❌ |
| **Actualizar Estado** | ✅ Todas | ❌ | ✅ Asignadas | ❌ |

## Implementación Técnica

### Clase de Permisos Personalizada

```python
class IsAdminOrMaintenanceOrResident(permissions.BasePermission):
    def has_permission(self, request, view):
        # Verificación básica de autenticación
        if not request.user or not request.user.is_authenticated:
            return False

        # Permisos por rol
        user_role = getattr(request.user, 'role', None)

        if user_role == 'admin':
            return True
        elif user_role == 'resident':
            return True  # Para crear solicitudes
        elif user_role == 'maintenance':
            return True  # Para gestionar tareas
        elif user_role == 'security':
            return request.method in permissions.SAFE_METHODS  # Solo lectura

        return False

    def has_object_permission(self, request, view, obj):
        user_role = getattr(request.user, 'role', None)

        # Admin tiene acceso total
        if user_role == 'admin':
            return True

        # Residentes solo acceden a sus propias solicitudes
        if isinstance(obj, SolicitudMantenimiento):
            return obj.solicitante == request.user

        # Mantenimiento solo accede a tareas asignadas
        if isinstance(obj, TareaMantenimiento):
            return obj.asignado_a == request.user

        return True
```

### Lógica de Filtrado por Rol

#### ViewSet de Solicitudes
```python
def get_queryset(self):
    user = self.request.user
    user_role = getattr(user, 'role', None)

    if user_role == 'admin':
        queryset = SolicitudMantenimiento.objects.all()
    elif user_role == 'maintenance':
        queryset = SolicitudMantenimiento.objects.all()  # Para asignar
    else:  # resident, security
        queryset = SolicitudMantenimiento.objects.filter(solicitante=user)

    # Aplicar filtros adicionales
    return queryset.order_by('-fecha_solicitud')
```

#### ViewSet de Tareas
```python
def get_queryset(self):
    user = self.request.user
    user_role = getattr(user, 'role', None)

    if user_role == 'admin':
        queryset = TareaMantenimiento.objects.all()
    elif user_role == 'maintenance':
        queryset = TareaMantenimiento.objects.filter(asignado_a=user)
    else:  # resident, security
        queryset = TareaMantenimiento.objects.filter(
            solicitud__solicitante=user
        )

    # Aplicar filtros adicionales
    return queryset.order_by('-fecha_asignacion')
```

## Validaciones de Permisos Específicas

### Asignación de Tareas
```python
@action(detail=True, methods=['post'])
def asignar_tarea(self, request, pk=None):
    # Solo admin y maintenance pueden asignar
    if not hasattr(request.user, 'role') or \
       request.user.role not in ['admin', 'maintenance']:
        return Response(
            {'error': 'No tienes permisos para asignar tareas'},
            status=status.HTTP_403_FORBIDDEN
        )
    # ... resto de la lógica
```

### Actualización de Estados
```python
@action(detail=True, methods=['post'])
def actualizar_estado(self, request, pk=None):
    tarea = self.get_object()

    # Solo el asignado o admin pueden actualizar
    if request.user != tarea.asignado_a and \
       (not hasattr(request.user, 'role') or request.user.role != 'admin'):
        return Response(
            {'error': 'No tienes permisos para actualizar esta tarea'},
            status=status.HTTP_403_FORBIDDEN
        )
    # ... resto de la lógica
```

## Casos de Uso por Rol

### Administrador
**Responsabilidades:**
- Supervisar todas las solicitudes y tareas
- Asignar tareas a personal de mantenimiento
- Gestionar estados críticos
- Generar reportes (futuro)

**Flujo típico:**
1. Revisa solicitudes pendientes
2. Asigna tareas según prioridad y disponibilidad
3. Monitorea progreso
4. Interviene en casos críticos

### Residente
**Responsabilidades:**
- Reportar problemas de mantenimiento
- Seguir estado de sus solicitudes
- Proporcionar información adicional si es requerido

**Flujo típico:**
1. Identifica problema
2. Crea solicitud con detalles
3. Monitorea estado
4. Confirma resolución

### Personal de Mantenimiento
**Responsabilidades:**
- Revisar tareas asignadas
- Actualizar estados de progreso
- Registrar notas técnicas
- Completar trabajos asignados

**Flujo típico:**
1. Revisa tareas asignadas
2. Actualiza estado a "en_progreso"
3. Registra trabajo realizado
4. Marca como completada

### Seguridad
**Responsabilidades:**
- Monitorear actividades de mantenimiento
- Reportar situaciones de riesgo
- Verificar acceso a áreas comunes

**Flujo típico:**
1. Revisa solicitudes activas
2. Monitorea progreso
3. Reporta incidentes

## Seguridad Adicional

### Validaciones de Datos
- Verificación de existencia de usuarios antes de asignación
- Validación de estados permitidos
- Control de cambios de estado válidos

### Auditoría
- Todos los cambios se registran con timestamps
- Historial de notas por usuario
- Trazabilidad completa de asignaciones

## Extensibilidad

### Nuevos Roles Futuros
- `supervisor`: Supervisor de mantenimiento
- `contractor`: Contratistas externos
- `manager`: Gerente de condominio

### Permisos Granulares
- Permisos específicos por tipo de mantenimiento
- Restricciones por horario
- Límites de presupuesto por rol

## Testing de Permisos

### Casos de Prueba
- Acceso denegado para roles incorrectos
- Filtrado correcto de datos por rol
- Validación de asignaciones permitidas
- Control de actualizaciones de estado

### Scripts de Testing
Ver carpeta `tests/mantenimiento/` para casos de prueba específicos por rol.