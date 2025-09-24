"""
URLs para el Módulo de Reservas de Áreas Comunes
Módulo 4: Reservas de Áreas Comunes
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AreaComunViewSet, ReservaViewSet, HorarioDisponibleViewSet

# Router para las APIs
router = DefaultRouter()
router.register(r'areas', AreaComunViewSet, basename='area-comun')
router.register(r'reservas', ReservaViewSet, basename='reserva')
router.register(r'horarios', HorarioDisponibleViewSet, basename='horario-disponible')

app_name = 'reservations'

urlpatterns = [
    path('', include(router.urls)),
]

"""
Endpoints disponibles:

ÁREAS COMUNES:
- GET    /api/reservations/areas/                     - Listar áreas comunes activas
- POST   /api/reservations/areas/                     - Crear área común (admin)
- GET    /api/reservations/areas/{id}/                - Detalle área común
- PUT    /api/reservations/areas/{id}/                - Actualizar área común (admin)
- PATCH  /api/reservations/areas/{id}/                - Actualizar área común parcial (admin)
- DELETE /api/reservations/areas/{id}/                - Eliminar área común (admin)
- GET    /api/reservations/areas/{id}/disponibilidad/ - Consultar disponibilidad (T1)
- POST   /api/reservations/areas/{id}/reservar/       - Reservar área común (T2)

RESERVAS:
- GET    /api/reservations/reservas/                  - Listar reservas (filtrado por permisos)
- POST   /api/reservations/reservas/                  - Crear reserva (no usado, usar /areas/{id}/reservar/)
- GET    /api/reservations/reservas/{id}/             - Detalle reserva
- PUT    /api/reservations/reservas/{id}/             - Actualizar reserva (admin)
- PATCH  /api/reservations/reservas/{id}/             - Actualizar reserva parcial (admin)
- DELETE /api/reservations/reservas/{id}/             - Eliminar reserva (admin)
- POST   /api/reservations/reservas/{id}/confirmar/   - Confirmar reserva con pago (T3)
- POST   /api/reservations/reservas/{id}/cancelar/    - Cancelar reserva (T4)
- GET    /api/reservations/reservas/mis_reservas/     - Reservas del usuario actual
- GET    /api/reservations/reservas/disponibles/      - Áreas disponibles para reserva

HORARIOS DISPONIBLES (solo admin):
- GET    /api/reservations/horarios/                  - Listar horarios disponibles
- POST   /api/reservations/horarios/                  - Crear horario disponible
- GET    /api/reservations/horarios/{id}/             - Detalle horario disponible
- PUT    /api/reservations/horarios/{id}/             - Actualizar horario disponible
- PATCH  /api/reservations/horarios/{id}/             - Actualizar horario disponible parcial
- DELETE /api/reservations/horarios/{id}/             - Eliminar horario disponible

FILTROS DISPONIBLES:

Áreas Comunes:
  ?tipo=gimnasio&capacidad_minima=10

Reservas:
  ?estado=confirmada&fecha_desde=2025-09-01&fecha_hasta=2025-09-30&area_comun=1

Disponibilidad:
  ?fecha=2025-09-25

TAREAS IMPLEMENTADAS:

T1: Consultar Disponibilidad de Área Común
   - Endpoint: GET /api/reservations/areas/{id}/disponibilidad/?fecha=YYYY-MM-DD
   - Retorna slots disponibles con horarios y costos

T2: Reservar Área Común
   - Endpoint: POST /api/reservations/areas/{id}/reservar/
   - Valida permisos, disponibilidad, capacidad y anticipación
   - Crea reserva en estado pendiente o confirmada según configuración

T3: Confirmar Reserva con Pago
   - Endpoint: POST /api/reservations/reservas/{id}/confirmar/
   - Procesa pago y marca reserva como pagada
   - TODO: Integrar completamente con módulo financiero

T4: Cancelar Reserva
   - Endpoint: POST /api/reservations/reservas/{id}/cancelar/
   - Valida permisos y estado de la reserva
   - TODO: Implementar reembolso si ya se pagó

PERMISOS:
- Administradores: Acceso completo a todas las funcionalidades
- Residentes: Pueden ver áreas, hacer reservas, gestionar sus reservas
- Seguridad: Solo lectura de áreas y reservas
"""