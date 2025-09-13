"""
URLs para el Módulo de Gestión Financiera
Módulo 2: Gestión Financiera Básica - T1: Configurar Cuotas y Multas
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConceptoFinancieroViewSet, CargoFinancieroViewSet, EstadisticasFinancierasViewSet

# Router para las APIs
router = DefaultRouter()
router.register(r'conceptos', ConceptoFinancieroViewSet, basename='concepto-financiero')
router.register(r'cargos', CargoFinancieroViewSet, basename='cargo-financiero')
router.register(r'estadisticas', EstadisticasFinancierasViewSet, basename='estadisticas-financieras')

app_name = 'finances'

urlpatterns = [
    path('', include(router.urls)),
]

"""
Endpoints disponibles:

CONCEPTOS FINANCIEROS:
- GET    /api/finances/conceptos/                     - Listar conceptos
- POST   /api/finances/conceptos/                     - Crear concepto (admin)
- GET    /api/finances/conceptos/{id}/                - Detalle concepto
- PUT    /api/finances/conceptos/{id}/                - Actualizar concepto (admin)
- PATCH  /api/finances/conceptos/{id}/                - Actualizar concepto parcial (admin)
- DELETE /api/finances/conceptos/{id}/                - Eliminar concepto (admin)
- GET    /api/finances/conceptos/vigentes/            - Conceptos vigentes
- POST   /api/finances/conceptos/{id}/toggle_estado/  - Activar/desactivar concepto (admin)

CARGOS FINANCIEROS:
- GET    /api/finances/cargos/                        - Listar cargos (filtrado por permisos)
- POST   /api/finances/cargos/                        - Crear cargo (admin)
- GET    /api/finances/cargos/{id}/                   - Detalle cargo
- PUT    /api/finances/cargos/{id}/                   - Actualizar cargo (admin)
- PATCH  /api/finances/cargos/{id}/                   - Actualizar cargo parcial (admin)
- DELETE /api/finances/cargos/{id}/                   - Eliminar cargo (admin)
- GET    /api/finances/cargos/mis_cargos/             - Cargos del usuario actual
- POST   /api/finances/cargos/{id}/pagar/             - Marcar cargo como pagado
- GET    /api/finances/cargos/vencidos/               - Cargos vencidos (admin)
- GET    /api/finances/cargos/resumen/{user_id}/      - Resumen financiero residente
- GET    /api/finances/cargos/estado_cuenta/          - Estado de cuenta completo (T2)

ESTADÍSTICAS:
- GET    /api/finances/estadisticas/                  - Estadísticas generales (admin)

FILTROS DISPONIBLES:
Conceptos:
  ?tipo=cuota_mensual&estado=activo&vigente=true

Cargos:
  ?estado=pendiente&residente=1&concepto=1&vencidos=true

Estado de Cuenta:
  ?residente=user_id  (solo para administradores)
"""