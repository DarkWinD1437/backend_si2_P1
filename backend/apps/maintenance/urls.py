"""
URLs para el Módulo de Gestión de Mantenimiento
Módulo: Gestión de Mantenimiento
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SolicitudMantenimientoViewSet, TareaMantenimientoViewSet

# Router para las APIs
router = DefaultRouter()
router.register(r'solicitudes', SolicitudMantenimientoViewSet, basename='solicitud-mantenimiento')
router.register(r'tareas', TareaMantenimientoViewSet, basename='tarea-mantenimiento')

app_name = 'maintenance'

urlpatterns = [
    path('', include(router.urls)),
]

"""
Endpoints disponibles:

SOLICITUDES DE MANTENIMIENTO:
- GET    /api/maintenance/solicitudes/                    - Listar solicitudes (filtrado por permisos)
- POST   /api/maintenance/solicitudes/                    - Crear solicitud de mantenimiento (T1)
- GET    /api/maintenance/solicitudes/{id}/               - Detalle solicitud
- PUT    /api/maintenance/solicitudes/{id}/               - Actualizar solicitud (admin)
- PATCH  /api/maintenance/solicitudes/{id}/               - Actualizar solicitud parcial (admin)
- DELETE /api/maintenance/solicitudes/{id}/               - Eliminar solicitud (admin)

TAREAS DE MANTENIMIENTO:
- GET    /api/maintenance/tareas/                         - Listar tareas (filtrado por permisos)
- POST   /api/maintenance/tareas/                         - Crear tarea (no usado directamente)
- GET    /api/maintenance/tareas/{id}/                    - Detalle tarea
- PUT    /api/maintenance/tareas/{id}/                    - Actualizar tarea (admin/mantenimiento)
- PATCH  /api/maintenance/tareas/{id}/                    - Actualizar tarea parcial (admin/mantenimiento)
- DELETE /api/maintenance/tareas/{id}/                    - Eliminar tarea (admin)
- POST   /api/maintenance/tareas/{id}/asignar/            - Asignar tarea (T2)
- POST   /api/maintenance/tareas/{id}/actualizar_estado/  - Actualizar estado tarea (T3)

TAREAS IMPLEMENTADAS:

T1: Registrar Solicitud de Mantenimiento
   - Endpoint: POST /api/maintenance/solicitudes/
   - Crea solicitud en estado pendiente

T2: Asignar Tarea de Mantenimiento
   - Endpoint: POST /api/maintenance/solicitudes/{id}/asignar_tarea/
   - Asigna tarea a un usuario de mantenimiento

T3: Seguimiento de Estado de Mantenimiento
   - Endpoint: POST /api/maintenance/tareas/{id}/actualizar_estado/
   - Actualiza estado de la tarea y solicitud relacionada

PERMISOS:
- Administradores: Acceso completo
- Residentes: Pueden crear solicitudes y ver sus solicitudes/tareas
- Mantenimiento: Pueden ver asignadas, actualizar estados
- Seguridad: Solo lectura
"""