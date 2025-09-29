"""
Tests for analytics views/endpoints
"""
from django.urls import reverse
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch, MagicMock
from backend.apps.analytics.tests.test_base import AnalyticsTestBase


class ReporteFinancieroAPITest(AnalyticsTestBase):

    def test_list_reportes_financieros_admin(self):
        """Test list financial reports as admin"""
        self.authenticate_as_admin()

        # Create some test reports
        self.create_test_financial_report(titulo="Report 1")
        self.create_test_financial_report(titulo="Report 2")

        response = self.client.get('/api/analytics/reportes-financieros/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_list_reportes_financieros_staff_limited(self):
        """Test list financial reports as staff with limitations"""
        self.authenticate_as_staff()

        # Create recent report (should be visible)
        recent_report = self.create_test_financial_report(
            titulo="Recent Report",
            fecha_generacion=timezone.now()
        )

        # Create old report (should not be visible to staff)
        old_date = timezone.now() - timedelta(days=200)
        old_report = self.create_test_financial_report(
            titulo="Old Report",
            fecha_generacion=old_date
        )

        response = self.client.get('/api/analytics/reportes-financieros/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Staff should only see recent reports
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['titulo'], "Recent Report")

    def test_list_reportes_financieros_resident_forbidden(self):
        """Test list financial reports as resident (should be forbidden)"""
        self.authenticate_as_resident()

        response = self.client.get('/api/analytics/reportes-financieros/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_reporte_financiero_admin(self):
        """Test create financial report as admin"""
        self.authenticate_as_admin()

        data = {
            "titulo": "Nuevo Report",
            "descripcion": "Descripción del reporte",
            "tipo": "ingresos",
            "periodo": "mensual",
            "formato": "pdf",
            "fecha_inicio": "2024-01-01",
            "fecha_fin": "2024-01-31",
            "filtros_aplicados": {
                "categoria": "todas",
                "incluir_multas": True
            }
        }

        response = self.client.post(
            '/api/analytics/reportes-financieros/',
            data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['titulo'], "Nuevo Report")
        self.assertEqual(response.data['generado_por'], self.user_admin.id)

    def test_create_reporte_financiero_staff_limited(self):
        """Test create financial report as staff with limitations"""
        self.authenticate_as_staff()

        # Try to create balance report (should be forbidden for staff)
        data = {
            "titulo": "Balance Report",
            "tipo": "balance",  # This should be restricted for staff
            "periodo": "mensual",
            "formato": "pdf",
            "fecha_inicio": "2024-01-01",
            "fecha_fin": "2024-01-31"
        }

        response = self.client.post(
            '/api/analytics/reportes-financieros/',
            data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_create_reporte_financiero_resident_forbidden(self):
        """Test create financial report as resident (should be forbidden)"""
        self.authenticate_as_resident()

        data = {
            "titulo": "Resident Report",
            "tipo": "ingresos",
            "periodo": "mensual",
            "formato": "pdf",
            "fecha_inicio": "2024-01-01",
            "fecha_fin": "2024-01-31"
        }

        response = self.client.post(
            '/api/analytics/reportes-financieros/',
            data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    @patch('analytics.views.generar_reporte_financiero')
    def test_generar_reporte_financiero_admin(self, mock_generar):
        """Test generate financial report as admin"""
        self.authenticate_as_admin()

        # Mock the report generation function
        mock_generar.return_value = {
            'total_ingresos': 15000.00,
            'ingresos_por_mes': {'2024-01': 15000.00},
            'fuentes_ingreso': {'cuotas': 12000.00, 'multas': 3000.00},
            'total_registros': 150
        }

        data = {
            "titulo": "Reporte Generado",
            "descripcion": "Reporte generado automáticamente",
            "tipo": "ingresos",
            "periodo": "mensual",
            "formato": "json",
            "fecha_inicio": "2024-01-01",
            "fecha_fin": "2024-01-31",
            "filtros_aplicados": {
                "fuente": "cuotas_mantenimiento"
            }
        }

        response = self.client.post(
            '/api/analytics/reportes-financieros/generar_reporte/',
            data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('datos', response.data)
        self.assertEqual(response.data['datos']['total_ingresos'], 15000.00)
        mock_generar.assert_called_once()

    def test_generar_reporte_financiero_invalid_dates(self):
        """Test generate financial report with invalid dates"""
        self.authenticate_as_admin()

        data = {
            "titulo": "Invalid Date Report",
            "tipo": "ingresos",
            "periodo": "mensual",
            "formato": "pdf",
            "fecha_inicio": "2024-01-31",
            "fecha_fin": "2024-01-01"  # End before start
        }

        response = self.client.post(
            '/api/analytics/reportes-financieros/generar_reporte/',
            data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('fecha_fin', response.data)


class ReporteSeguridadAPITest(AnalyticsTestBase):

    @patch('analytics.views.generar_reporte_seguridad')
    def test_generar_reporte_seguridad_admin(self, mock_generar):
        """Test generate security report as admin"""
        self.authenticate_as_admin()

        mock_generar.return_value = {
            'total_incidentes': 12,
            'incidentes_por_tipo': {'intento_fuerza': 3, 'codigo_incorrecto': 8, 'sospechoso': 1},
            'incidentes_resueltos': 11,
            'tiempo_respuesta_promedio': '5.2 minutos'
        }

        data = {
            "titulo": "Seguridad Enero",
            "descripcion": "Análisis de incidentes",
            "tipo": "incidentes",
            "periodo": "mensual",
            "fecha_inicio": "2024-01-01T00:00:00Z",
            "fecha_fin": "2024-01-31T23:59:59Z",
            "filtros_aplicados": {
                "nivel_critico": True
            }
        }

        response = self.client.post(
            '/api/analytics/reportes-seguridad/generar_reporte/',
            data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('datos', response.data)
        self.assertEqual(response.data['datos']['total_incidentes'], 12)

    def test_generar_reporte_seguridad_staff(self):
        """Test generate security report as staff"""
        self.authenticate_as_staff()

        data = {
            "titulo": "Seguridad Staff",
            "tipo": "incidentes",
            "periodo": "diario",
            "fecha_inicio": "2024-01-01T00:00:00Z",
            "fecha_fin": "2024-01-01T23:59:59Z"
        }

        response = self.client.post(
            '/api/analytics/reportes-seguridad/generar_reporte/',
            data,
            format='json'
        )

        # Staff should be able to generate basic security reports
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


class ReporteUsoAreasAPITest(AnalyticsTestBase):

    @patch('analytics.views.generar_reporte_uso_areas')
    def test_generar_reporte_uso_areas_admin(self, mock_generar):
        """Test generate area usage report as admin"""
        self.authenticate_as_admin()

        mock_generar.return_value = {
            'tasa_ocupacion_promedio': 68.5,
            'ocupacion_por_dia': {'lunes': 75.0, 'martes': 70.0},
            'ocupacion_por_hora': {'08:00': 30.0, '12:00': 70.0}
        }

        data = {
            "titulo": "Ocupación Piscina",
            "descripcion": "Análisis de uso de piscina",
            "area": "piscina",
            "periodo": "mensual",
            "metrica_principal": "ocupacion",
            "fecha_inicio": "2024-01-01",
            "fecha_fin": "2024-01-31",
            "filtros_aplicados": {
                "dias_semana": ["sabado", "domingo"]
            }
        }

        response = self.client.post(
            '/api/analytics/reportes-uso-areas/generar_reporte/',
            data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('datos', response.data)
        self.assertEqual(response.data['datos']['tasa_ocupacion_promedio'], 68.5)

    def test_generar_reporte_uso_areas_resident_forbidden(self):
        """Test generate area usage report as resident (should be forbidden)"""
        self.authenticate_as_resident()

        data = {
            "titulo": "Uso Areas Resident",
            "area": "piscina",
            "periodo": "mensual",
            "metrica_principal": "ocupacion",
            "fecha_inicio": "2024-01-01",
            "fecha_fin": "2024-01-31"
        }

        response = self.client.post(
            '/api/analytics/reportes-uso-areas/generar_reporte/',
            data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class PrediccionMorosidadAPITest(AnalyticsTestBase):

    @patch('analytics.views.generar_prediccion_morosidad')
    def test_generar_prediccion_morosidad_admin(self, mock_generar):
        """Test generate morosidad prediction as admin"""
        self.authenticate_as_admin()

        mock_generar.return_value = {
            'predicciones_por_residente': [
                {'residente_id': 1, 'riesgo_morosidad': 'bajo', 'probabilidad': 0.15},
                {'residente_id': 2, 'riesgo_morosidad': 'medio', 'probabilidad': 0.65}
            ],
            'estadisticas_generales': {
                'riesgo_bajo': 30, 'riesgo_medio': 12, 'riesgo_alto': 8,
                'precision_modelo': 85.2
            },
            'factores_riesgo_identificados': [
                'Historial de pagos atrasados',
                'Cambios en ingresos declarados'
            ]
        }

        data = {
            "titulo": "Predicción Morosidad Q1",
            "descripcion": "Análisis predictivo de riesgo",
            "modelo_usado": "random_forest",
            "periodo_predicho": "Próximos 3 meses",
            "datos_entrada": {
                "variables_historicas": True,
                "incluir_demografia": True,
                "periodo_analisis": "12_meses"
            },
            "parametros_modelo": {
                "n_estimators": 100,
                "max_depth": 10,
                "random_state": 42
            }
        }

        response = self.client.post(
            '/api/analytics/predicciones-morosidad/generar_prediccion/',
            data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('resultados', response.data)
        self.assertIn('predicciones_por_residente', response.data['resultados'])

    def test_generar_prediccion_morosidad_staff_forbidden(self):
        """Test generate morosidad prediction as staff (should be forbidden)"""
        self.authenticate_as_staff()

        data = {
            "titulo": "Predicción Staff",
            "modelo_usado": "random_forest",
            "periodo_predicho": "Próximos 3 meses"
        }

        response = self.client.post(
            '/api/analytics/predicciones-morosidad/generar_prediccion/',
            data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_predicciones_admin(self):
        """Test list predictions as admin"""
        self.authenticate_as_admin()

        # Create test predictions
        self.create_test_prediction(titulo="Prediction 1")
        self.create_test_prediction(titulo="Prediction 2")

        response = self.client.get('/api/analytics/predicciones-morosidad/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_list_predicciones_staff_limited(self):
        """Test list predictions as staff with limitations"""
        self.authenticate_as_staff()

        # Create prediction with medium risk
        self.create_test_prediction(
            titulo="Medium Risk Prediction",
            resultados={
                'estadisticas_generales': {'riesgo_medio': 15, 'riesgo_alto': 0}
            }
        )

        # Create prediction with high risk (should be filtered for staff)
        self.create_test_prediction(
            titulo="High Risk Prediction",
            resultados={
                'estadisticas_generales': {'riesgo_medio': 5, 'riesgo_alto': 10}
            }
        )

        response = self.client.get('/api/analytics/predicciones-morosidad/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Staff should only see medium risk predictions
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['titulo'], "Medium Risk Prediction")


class AnalyticsPermissionsTest(AnalyticsTestBase):

    def test_unauthenticated_access_forbidden(self):
        """Test that unauthenticated users cannot access endpoints"""
        # Don't authenticate

        response = self.client.get('/api/analytics/reportes-financieros/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        response = self.client.post('/api/analytics/reportes-financieros/', {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_admin_full_access(self):
        """Test that admin has full access to all endpoints"""
        self.authenticate_as_admin()

        # Test financial reports
        response = self.client.get('/api/analytics/reportes-financieros/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Test security reports
        response = self.client.post('/api/analytics/reportes-seguridad/generar_reporte/', {
            "titulo": "Test", "tipo": "incidentes", "periodo": "diario",
            "fecha_inicio": "2024-01-01T00:00:00Z", "fecha_fin": "2024-01-01T23:59:59Z"
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Test area usage reports
        response = self.client.post('/api/analytics/reportes-uso-areas/generar_reporte/', {
            "titulo": "Test", "area": "piscina", "periodo": "mensual",
            "metrica_principal": "ocupacion", "fecha_inicio": "2024-01-01", "fecha_fin": "2024-01-31"
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Test predictions
        response = self.client.post('/api/analytics/predicciones-morosidad/generar_prediccion/', {
            "titulo": "Test", "modelo_usado": "random_forest", "periodo_predicho": "3 meses"
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_staff_restricted_access(self):
        """Test that staff has restricted access"""
        self.authenticate_as_staff()

        # Can access financial reports (with limitations)
        response = self.client.get('/api/analytics/reportes-financieros/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Cannot generate predictions
        response = self.client.post('/api/analytics/predicciones-morosidad/generar_prediccion/', {
            "titulo": "Test", "modelo_usado": "random_forest", "periodo_predicho": "3 meses"
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_resident_limited_access(self):
        """Test that residents have very limited access"""
        self.authenticate_as_resident()

        # Cannot access financial reports
        response = self.client.get('/api/analytics/reportes-financieros/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Cannot generate any reports
        response = self.client.post('/api/analytics/reportes-seguridad/generar_reporte/', {
            "titulo": "Test", "tipo": "incidentes", "periodo": "diario",
            "fecha_inicio": "2024-01-01T00:00:00Z", "fecha_fin": "2024-01-01T23:59:59Z"
        })
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)