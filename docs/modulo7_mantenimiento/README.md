# Módulo de Gestión de Mantenimiento

## Descripción
El módulo de Gestión de Mantenimiento permite a los residentes del condominio reportar problemas de mantenimiento, asignar tareas a personal de mantenimiento y hacer seguimiento del estado de las reparaciones.

## Funcionalidades Implementadas

### 1. Registrar Solicitud de Mantenimiento
- **Endpoint**: `POST /api/maintenance/solicitudes/`
- **Permisos**: Residentes autenticados
- **Campos requeridos**:
  - `descripcion`: Descripción del problema
  - `ubicacion`: Ubicación del problema
  - `prioridad`: baja/media/alta/urgente

### 2. Asignar Tarea de Mantenimiento
- **Endpoint**: `POST /api/maintenance/solicitudes/{id}/asignar_tarea/`
- **Permisos**: Administradores y personal de mantenimiento
- **Campos requeridos**:
  - `asignado_a_id`: ID del usuario asignado
  - `descripcion_tarea`: Descripción detallada de la tarea
  - `notas`: Notas adicionales (opcional)

### 3. Seguimiento de Estado de Mantenimiento
- **Endpoint**: `POST /api/maintenance/tareas/{id}/actualizar_estado/`
- **Permisos**: Usuario asignado o administradores
- **Campos requeridos**:
  - `estado`: pendiente/asignada/en_progreso/completada/cancelada
  - `notas`: Notas sobre el progreso (opcional)

## Estados del Sistema

### Estados de Solicitud
- `pendiente`: Solicitud creada, esperando asignación
- `asignada`: Tarea asignada a personal de mantenimiento
- `en_progreso`: Trabajo en curso
- `completada`: Trabajo finalizado
- `cancelada`: Solicitud cancelada

### Estados de Tarea
- `pendiente`: Tarea creada pero no iniciada
- `asignada`: Tarea asignada a usuario
- `en_progreso`: Trabajo iniciado
- `completada`: Trabajo finalizado
- `cancelada`: Tarea cancelada

## Permisos por Rol

### Administradores
- Acceso completo a todas las solicitudes y tareas
- Pueden asignar tareas
- Pueden actualizar cualquier estado

### Residentes
- Pueden crear solicitudes de mantenimiento
- Pueden ver solo sus propias solicitudes y tareas relacionadas

### Personal de Mantenimiento
- Pueden ver todas las solicitudes (para asignación)
- Pueden ver tareas asignadas a ellos
- Pueden actualizar estados de sus tareas asignadas

### Seguridad
- Solo lectura de solicitudes y tareas

## Endpoints Disponibles

### Solicitudes de Mantenimiento
- `GET /api/maintenance/solicitudes/` - Listar solicitudes (con filtros)
- `POST /api/maintenance/solicitudes/` - Crear solicitud
- `GET /api/maintenance/solicitudes/{id}/` - Detalle solicitud
- `PUT /api/maintenance/solicitudes/{id}/` - Actualizar solicitud
- `PATCH /api/maintenance/solicitudes/{id}/` - Actualizar parcial
- `DELETE /api/maintenance/solicitudes/{id}/` - Eliminar solicitud
- `POST /api/maintenance/solicitudes/{id}/asignar_tarea/` - Asignar tarea

### Tareas de Mantenimiento
- `GET /api/maintenance/tareas/` - Listar tareas (con filtros)
- `GET /api/maintenance/tareas/{id}/` - Detalle tarea
- `PUT /api/maintenance/tareas/{id}/` - Actualizar tarea
- `PATCH /api/maintenance/tareas/{id}/` - Actualizar parcial
- `DELETE /api/maintenance/tareas/{id}/` - Eliminar tarea
- `POST /api/maintenance/tareas/{id}/actualizar_estado/` - Actualizar estado

## Filtros Disponibles

### Solicitudes
- `?estado=pendiente` - Filtrar por estado
- `?prioridad=alta` - Filtrar por prioridad

### Tareas
- `?estado=en_progreso` - Filtrar por estado
- `?asignado_a=1` - Filtrar por usuario asignado

## Documentación API
La documentación completa de la API está disponible en:
- **Swagger UI**: `/api/schema/swagger-ui/`
- **ReDoc**: `/api/schema/redoc/`
- **OpenAPI Schema**: `/api/schema/`

## Testing
Para ejecutar las pruebas del módulo:
```bash
cd Backend_Django/tests/modulo5_maintenance
python test_maintenance_completo.py
```

El script de pruebas valida todas las funcionalidades principales del módulo.

## Modelos de Datos

### SolicitudMantenimiento
- `id`: ID único
- `solicitante`: Usuario que creó la solicitud
- `descripcion`: Descripción del problema
- `ubicacion`: Ubicación del problema
- `prioridad`: Prioridad (baja/media/alta/urgente)
- `estado`: Estado actual
- `fecha_solicitud`: Fecha de creación
- `fecha_actualizacion`: Última actualización

### TareaMantenimiento
- `id`: ID único
- `solicitud`: Solicitud relacionada
- `asignado_a`: Usuario asignado
- `descripcion_tarea`: Descripción detallada
- `estado`: Estado actual
- `fecha_asignacion`: Fecha de asignación
- `fecha_completado`: Fecha de completación (opcional)
- `notas`: Notas adicionales

## Próximas Mejores
- Notificaciones automáticas por email/SMS
- Sistema de prioridades basado en IA
- Reportes de mantenimiento
- Integración con calendario
- Fotos adjuntas a solicitudes