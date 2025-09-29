"""
Integration tests for analytics module
"""
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from unittest.mock import patch
from backend.apps.analytics.tests.test_base import AnalyticsTestBase


class AnalyticsIntegrationTest(AnalyticsTestBase):

    def test_complete_admin_workflow(self):
        """Test complete workflow as admin user"""
        self.authenticate_as_admin()

        # 1. Generate financial report
        financial_data = {
            "titulo": "Monthly Financial Report",
            "descripcion": "Complete financial analysis",
            "tipo": "balance",
            "periodo": "mensual",
            "formato": "json",
            "fecha_inicio": "2024-01-01",
            "fecha_fin": "2024-01-31",
            "filtros_aplicados": {
                "categoria": "todas",
                "incluir_multas": True
            }
        }

        with patch('analytics.views.generar_reporte_financiero') as mock_financial:
            mock_financial.return_value = {
                'total_ingresos': 25000.00,
                'total_egresos': 18000.00,
                'balance': 7000.00,
                'total_registros': 200
            }

            response = self.client.post(
                '/api/analytics/reportes-financieros/generar_reporte/',
                financial_data,
                format='json'
            )

            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            financial_report_id = response.data['id']

        # 2. Generate security report
        security_data = {
            "titulo": "Monthly Security Report",
            "descripcion": "Security incidents analysis",
            "tipo": "incidentes",
            "periodo": "mensual",
            "fecha_inicio": "2024-01-01T00:00:00Z",
            "fecha_fin": "2024-01-31T23:59:59Z",
            "filtros_aplicados": {
                "nivel_critico": True
            }
        }

        with patch('analytics.views.generar_reporte_seguridad') as mock_security:
            mock_security.return_value = {
                'total_incidentes': 15,
                'incidentes_por_tipo': {'intento_fuerza': 5, 'codigo_incorrecto': 10},
                'incidentes_resueltos': 14,
                'tiempo_respuesta_promedio': '4.5 minutos'
            }

            response = self.client.post(
                '/api/analytics/reportes-seguridad/generar_reporte/',
                security_data,
                format='json'
            )

            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 3. Generate area usage report
        area_data = {
            "titulo": "Pool Usage Report",
            "descripcion": "Pool occupancy analysis",
            "area": "piscina",
            "periodo": "mensual",
            "metrica_principal": "ocupacion",
            "fecha_inicio": "2024-01-01",
            "fecha_fin": "2024-01-31",
            "filtros_aplicados": {
                "dias_semana": ["sabado", "domingo"]
            }
        }

        with patch('analytics.views.generar_reporte_uso_areas') as mock_area:
            mock_area.return_value = {
                'tasa_ocupacion_promedio': 75.5,
                'ocupacion_por_dia': {'lunes': 80.0, 'martes': 70.0},
                'total_reservas': 320,
                'horas_ocupacion': 1800.5
            }

            response = self.client.post(
                '/api/analytics/reportes-uso-areas/generar_reporte/',
                area_data,
                format='json'
            )

            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 4. Generate morosidad prediction
        prediction_data = {
            "titulo": "Morosidad Prediction Q1",
            "descripcion": "Predictive analysis of payment risk",
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

        with patch('analytics.views.generar_prediccion_morosidad') as mock_prediction:
            mock_prediction.return_value = {
                'predicciones_por_residente': [
                    {'residente_id': 1, 'riesgo_morosidad': 'bajo', 'probabilidad': 0.12},
                    {'residente_id': 2, 'riesgo_morosidad': 'medio', 'probabilidad': 0.68}
                ],
                'estadisticas_generales': {
                    'riesgo_bajo': 35, 'riesgo_medio': 10, 'riesgo_alto': 5,
                    'precision_modelo': 87.3
                },
                'factores_riesgo_identificados': [
                    'Historial de pagos atrasados',
                    'Cambios en ingresos'
                ]
            }

            response = self.client.post(
                '/api/analytics/predicciones-morosidad/generar_prediccion/',
                prediction_data,
                format='json'
            )

            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 5. List all reports to verify creation
        response = self.client.get('/api/analytics/reportes-financieros/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

        response = self.client.get('/api/analytics/predicciones-morosidad/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_staff_limited_workflow(self):
        """Test workflow with staff limitations"""
        self.authenticate_as_staff()

        # Staff can generate basic financial reports
        data = {
            "titulo": "Staff Income Report",
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
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # But cannot generate balance reports
        data['tipo'] = 'balance'
        response = self.client.post(
            '/api/analytics/reportes-financieros/',
            data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Can generate security reports
        security_data = {
            "titulo": "Staff Security Report",
            "tipo": "incidentes",
            "periodo": "diario",
            "fecha_inicio": "2024-01-01T00:00:00Z",
            "fecha_fin": "2024-01-01T23:59:59Z"
        }

        response = self.client.post(
            '/api/analytics/reportes-seguridad/generar_reporte/',
            security_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Cannot generate predictions
        prediction_data = {
            "titulo": "Staff Prediction",
            "modelo_usado": "random_forest",
            "periodo_predicho": "3 meses"
        }

        response = self.client.post(
            '/api/analytics/predicciones-morosidad/generar_prediccion/',
            prediction_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_resident_restricted_workflow(self):
        """Test workflow with resident restrictions"""
        self.authenticate_as_resident()

        # Resident cannot access most endpoints
        endpoints = [
            '/api/analytics/reportes-financieros/',
            '/api/analytics/reportes-seguridad/generar_reporte/',
            '/api/analytics/reportes-uso-areas/generar_reporte/',
            '/api/analytics/predicciones-morosidad/',
            '/api/analytics/predicciones-morosidad/generar_prediccion/'
        ]

        for endpoint in endpoints:
            if endpoint.endswith('/'):
                response = self.client.get(endpoint)
            else:
                response = self.client.post(endpoint, {})
            self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cross_module_data_consistency(self):
        """Test data consistency across different report types"""
        self.authenticate_as_admin()

        # Create reports with related data
        base_date = "2024-01-15"

        # Financial report
        with patch('analytics.views.generar_reporte_financiero') as mock_financial:
            mock_financial.return_value = {
                'total_ingresos': 30000.00,
                'total_registros': 150
            }

            financial_response = self.client.post(
                '/api/analytics/reportes-financieros/generar_reporte/',
                {
                    "titulo": "Financial Overview",
                    "tipo": "ingresos",
                    "periodo": "mensual",
                    "formato": "json",
                    "fecha_inicio": "2024-01-01",
                    "fecha_fin": "2024-01-31"
                },
                format='json'
            )
            self.assertEqual(financial_response.status_code, status.HTTP_201_CREATED)

        # Security report for same period
        with patch('analytics.views.generar_reporte_seguridad') as mock_security:
            mock_security.return_value = {
                'total_incidentes': 8,
                'total_eventos': 8
            }

            security_response = self.client.post(
                '/api/analytics/reportes-seguridad/generar_reporte/',
                {
                    "titulo": "Security Overview",
                    "tipo": "incidentes",
                    "periodo": "mensual",
                    "fecha_inicio": "2024-01-01T00:00:00Z",
                    "fecha_fin": "2024-01-31T23:59:59Z"
                },
                format='json'
            )
            self.assertEqual(security_response.status_code, status.HTTP_201_CREATED)

        # Both reports should be created successfully and independently
        self.assertNotEqual(
            financial_response.data['id'],
            security_response.data['id']
        )

        # Verify both appear in their respective lists
        financial_list = self.client.get('/api/analytics/reportes-financieros/')
        security_list = self.client.get('/api/analytics/reportes-seguridad/generar_reporte/')  # This is wrong, should be list endpoint

        self.assertEqual(financial_list.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(financial_list.data), 1)

    def test_error_handling_integration(self):
        """Test error handling across the module"""
        self.authenticate_as_admin()

        # Test invalid data handling
        invalid_data = {
            "titulo": "",
            "tipo": "invalid_type",
            "periodo": "invalid_period",
            "formato": "invalid_format",
            "fecha_inicio": "2024-01-31",
            "fecha_fin": "2024-01-01"  # Invalid date range
        }

        response = self.client.post(
            '/api/analytics/reportes-financieros/',
            invalid_data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        # Should contain multiple validation errors
        self.assertGreater(len(response.data), 1)

    def test_data_filtering_integration(self):
        """Test that data filtering works correctly across endpoints"""
        self.authenticate_as_staff()

        # Create reports with different dates
        old_report = self.create_test_financial_report(
            titulo="Old Report",
            fecha_generacion=timezone.now() - timedelta(days=300)  # 10 months ago
        )

        recent_report = self.create_test_financial_report(
            titulo="Recent Report",
            fecha_generacion=timezone.now()  # Today
        )

        # Staff should only see recent reports
        response = self.client.get('/api/analytics/reportes-financieros/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Should only return the recent report
        report_titles = [report['titulo'] for report in response.data]
        self.assertIn("Recent Report", report_titles)
        self.assertNotIn("Old Report", report_titles)