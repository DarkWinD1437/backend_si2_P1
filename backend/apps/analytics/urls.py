"""
URLs para el Módulo de Reportes y Analítica
Módulo 8: Reportes y Analítica
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ReporteFinancieroViewSet,
    ReporteSeguridadViewSet,
    ReporteUsoAreasViewSet,
    PrediccionMorosidadViewSet
)

# Router para las APIs
router = DefaultRouter()
router.register(r'reportes-financieros', ReporteFinancieroViewSet, basename='reporte-financiero')
router.register(r'reportes-seguridad', ReporteSeguridadViewSet, basename='reporte-seguridad')
router.register(r'reportes-uso-areas', ReporteUsoAreasViewSet, basename='reporte-uso-areas')
router.register(r'predicciones-morosidad', PrediccionMorosidadViewSet, basename='prediccion-morosidad')

app_name = 'analytics'

urlpatterns = [
    path('', include(router.urls)),
]

"""
Endpoints disponibles:

REPORTES FINANCIEROS:
- GET    /api/analytics/reportes-financieros/                    - Listar reportes financieros
- POST   /api/analytics/reportes-financieros/                    - Crear reporte financiero
- GET    /api/analytics/reportes-financieros/{id}/               - Detalle reporte financiero
- PUT    /api/analytics/reportes-financieros/{id}/               - Actualizar reporte
- PATCH  /api/analytics/reportes-financieros/{id}/               - Actualizar parcial
- DELETE /api/analytics/reportes-financieros/{id}/               - Eliminar reporte
- POST   /api/analytics/reportes-financieros/generar_reporte/    - Generar reporte financiero (T1)

REPORTES DE SEGURIDAD:
- GET    /api/analytics/reportes-seguridad/                      - Listar reportes de seguridad
- POST   /api/analytics/reportes-seguridad/                      - Crear reporte de seguridad
- GET    /api/analytics/reportes-seguridad/{id}/                 - Detalle reporte de seguridad
- PUT    /api/analytics/reportes-seguridad/{id}/                 - Actualizar reporte
- PATCH  /api/analytics/reportes-seguridad/{id}/                 - Actualizar parcial
- DELETE /api/analytics/reportes-seguridad/{id}/                 - Eliminar reporte
- POST   /api/analytics/reportes-seguridad/generar_reporte/      - Generar reporte de seguridad (T2)

REPORTES DE USO DE ÁREAS:
- GET    /api/analytics/reportes-uso-areas/                      - Listar reportes de uso de áreas
- POST   /api/analytics/reportes-uso-areas/                      - Crear reporte de uso de áreas
- GET    /api/analytics/reportes-uso-areas/{id}/                 - Detalle reporte de uso de áreas
- PUT    /api/analytics/reportes-uso-areas/{id}/                 - Actualizar reporte
- PATCH  /api/analytics/reportes-uso-areas/{id}/                 - Actualizar parcial
- DELETE /api/analytics/reportes-uso-areas/{id}/                 - Eliminar reporte
- POST   /api/analytics/reportes-uso-areas/generar_reporte/      - Generar reporte de uso de áreas (T3)

PREDICCIONES DE MOROSIDAD:
- GET    /api/analytics/predicciones-morosidad/                  - Listar predicciones de morosidad
- POST   /api/analytics/predicciones-morosidad/                  - Crear predicción de morosidad
- GET    /api/analytics/predicciones-morosidad/{id}/             - Detalle predicción de morosidad
- PUT    /api/analytics/predicciones-morosidad/{id}/             - Actualizar predicción
- PATCH  /api/analytics/predicciones-morosidad/{id}/             - Actualizar parcial
- DELETE /api/analytics/predicciones-morosidad/{id}/             - Eliminar predicción
- POST   /api/analytics/predicciones-morosidad/generar_prediccion/ - Generar predicción con IA (T4)

TAREAS IMPLEMENTADAS:

T1: Generar Reporte Financiero
   - Endpoint: POST /api/analytics/reportes-financieros/generar_reporte/
   - Tipos: ingresos, egresos, balance, estado_cuenta, morosidad, presupuesto, otros
   - Formatos: json, pdf, excel, csv

T2: Generar Reporte de Seguridad
   - Endpoint: POST /api/analytics/reportes-seguridad/generar_reporte/
   - Tipos: accesos, incidentes, alertas, patrones, auditoria
   - Incluye estadísticas de eventos críticos y alertas

T3: Generar Reporte de Uso de Áreas Comunes
   - Endpoint: POST /api/analytics/reportes-uso-areas/generar_reporte/
   - Áreas: gimnasio, piscina, salon_eventos, estacionamiento, areas_verdes, todas
   - Métricas: ocupacion, reservas, tiempo_promedio, patrones_horarios, comparativo

T4: Generar Predicción de Morosidad con IA
   - Endpoint: POST /api/analytics/predicciones-morosidad/generar_prediccion/
   - Modelos: regresion_logistica, random_forest, xgboost, red_neuronal, ensemble
   - Incluye métricas de evaluación y nivel de confianza

PERMISOS:
- Administradores: Acceso completo a todos los reportes y predicciones
- Staff (mantenimiento, seguridad): Solo lectura de reportes
- Residentes: Sin acceso
"""