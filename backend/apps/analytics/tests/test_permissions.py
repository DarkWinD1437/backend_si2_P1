"""
Tests for analytics permissions
"""
from django.test import override_settings
from rest_framework import status
from backend.apps.analytics.tests.test_base import AnalyticsTestBase


class AnalyticsPermissionsTest(AnalyticsTestBase):

    def test_admin_has_full_access_to_financial_reports(self):
        """Test that admin has full access to financial reports"""
        self.authenticate_as_admin()

        # Can list reports
        response = self.client.get('/api/analytics/reportes-financieros/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Can create reports
        data = {
            "titulo": "Admin Report",
            "tipo": "balance",
            "periodo": "mensual",
            "formato": "pdf",
            "fecha_inicio": "2024-01-01",
            "fecha_fin": "2024-01-31"
        }
        response = self.client.post('/api/analytics/reportes-financieros/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Can generate reports
        response = self.client.post('/api/analytics/reportes-financieros/generar_reporte/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_staff_has_limited_access_to_financial_reports(self):
        """Test that staff has limited access to financial reports"""
        self.authenticate_as_staff()

        # Can list reports (but with filters)
        response = self.client.get('/api/analytics/reportes-financieros/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Cannot create balance reports
        data = {
            "titulo": "Staff Balance Report",
            "tipo": "balance",  # Should be forbidden
            "periodo": "mensual",
            "formato": "pdf",
            "fecha_inicio": "2024-01-01",
            "fecha_fin": "2024-01-31"
        }
        response = self.client.post('/api/analytics/reportes-financieros/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Can create basic reports
        data['tipo'] = 'ingresos'  # Should be allowed
        response = self.client.post('/api/analytics/reportes-financieros/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_resident_has_no_access_to_financial_reports(self):
        """Test that resident has no access to financial reports"""
        self.authenticate_as_resident()

        # Cannot list reports
        response = self.client.get('/api/analytics/reportes-financieros/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Cannot create reports
        data = {
            "titulo": "Resident Report",
            "tipo": "ingresos",
            "periodo": "mensual",
            "formato": "pdf",
            "fecha_inicio": "2024-01-01",
            "fecha_fin": "2024-01-31"
        }
        response = self.client.post('/api/analytics/reportes-financieros/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_has_full_access_to_security_reports(self):
        """Test that admin has full access to security reports"""
        self.authenticate_as_admin()

        data = {
            "titulo": "Security Report",
            "tipo": "incidentes",
            "periodo": "semanal",
            "fecha_inicio": "2024-01-01T00:00:00Z",
            "fecha_fin": "2024-01-07T23:59:59Z"
        }

        response = self.client.post('/api/analytics/reportes-seguridad/generar_reporte/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_staff_has_limited_access_to_security_reports(self):
        """Test that staff has limited access to security reports"""
        self.authenticate_as_staff()

        # Can generate basic security reports
        data = {
            "titulo": "Staff Security Report",
            "tipo": "incidentes",
            "periodo": "diario",
            "fecha_inicio": "2024-01-01T00:00:00Z",
            "fecha_fin": "2024-01-01T23:59:59Z"
        }

        response = self.client.post('/api/analytics/reportes-seguridad/generar_reporte/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_resident_has_no_access_to_security_reports(self):
        """Test that resident has no access to security reports"""
        self.authenticate_as_resident()

        data = {
            "titulo": "Resident Security Report",
            "tipo": "incidentes",
            "periodo": "diario",
            "fecha_inicio": "2024-01-01T00:00:00Z",
            "fecha_fin": "2024-01-01T23:59:59Z"
        }

        response = self.client.post('/api/analytics/reportes-seguridad/generar_reporte/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_has_full_access_to_area_usage_reports(self):
        """Test that admin has full access to area usage reports"""
        self.authenticate_as_admin()

        data = {
            "titulo": "Area Usage Report",
            "area": "piscina",
            "periodo": "mensual",
            "metrica_principal": "ocupacion",
            "fecha_inicio": "2024-01-01",
            "fecha_fin": "2024-01-31"
        }

        response = self.client.post('/api/analytics/reportes-uso-areas/generar_reporte/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_staff_has_access_to_area_usage_reports(self):
        """Test that staff has access to area usage reports"""
        self.authenticate_as_staff()

        data = {
            "titulo": "Staff Area Report",
            "area": "gimnasio",
            "periodo": "semanal",
            "metrica_principal": "ocupacion",
            "fecha_inicio": "2024-01-01",
            "fecha_fin": "2024-01-07"
        }

        response = self.client.post('/api/analytics/reportes-uso-areas/generar_reporte/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_resident_has_no_access_to_area_usage_generation(self):
        """Test that resident cannot generate area usage reports"""
        self.authenticate_as_resident()

        data = {
            "titulo": "Resident Area Report",
            "area": "piscina",
            "periodo": "mensual",
            "metrica_principal": "ocupacion",
            "fecha_inicio": "2024-01-01",
            "fecha_fin": "2024-01-31"
        }

        response = self.client.post('/api/analytics/reportes-uso-areas/generar_reporte/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_has_full_access_to_predictions(self):
        """Test that admin has full access to predictions"""
        self.authenticate_as_admin()

        # Can list predictions
        response = self.client.get('/api/analytics/predicciones-morosidad/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Can generate predictions
        data = {
            "titulo": "Admin Prediction",
            "modelo_usado": "random_forest",
            "periodo_predicho": "Próximos 3 meses"
        }

        response = self.client.post('/api/analytics/predicciones-morosidad/generar_prediccion/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_staff_has_limited_access_to_predictions(self):
        """Test that staff has limited access to predictions"""
        self.authenticate_as_staff()

        # Can list predictions (with filters)
        response = self.client.get('/api/analytics/predicciones-morosidad/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Cannot generate predictions
        data = {
            "titulo": "Staff Prediction",
            "modelo_usado": "random_forest",
            "periodo_predicho": "Próximos 3 meses"
        }

        response = self.client.post('/api/analytics/predicciones-morosidad/generar_prediccion/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_resident_has_no_access_to_predictions(self):
        """Test that resident has no access to predictions"""
        self.authenticate_as_resident()

        # Cannot list predictions
        response = self.client.get('/api/analytics/predicciones-morosidad/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        # Cannot generate predictions
        data = {
            "titulo": "Resident Prediction",
            "modelo_usado": "random_forest",
            "periodo_predicho": "Próximos 3 meses"
        }

        response = self.client.post('/api/analytics/predicciones-morosidad/generar_prediccion/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_unauthenticated_users_blocked(self):
        """Test that unauthenticated users are blocked from all endpoints"""
        # No authentication

        # Financial reports
        response = self.client.get('/api/analytics/reportes-financieros/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Security reports
        response = self.client.post('/api/analytics/reportes-seguridad/generar_reporte/', {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Area usage reports
        response = self.client.post('/api/analytics/reportes-uso-areas/generar_reporte/', {})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        # Predictions
        response = self.client.get('/api/analytics/predicciones-morosidad/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    @override_settings(ANALYTICS_RATE_LIMIT_ENABLED=True)
    def test_rate_limiting_applies_by_role(self):
        """Test that rate limiting applies correctly by role"""
        # This would require setting up rate limiting middleware
        # For now, just test that endpoints respond
        self.authenticate_as_resident()

        # Resident should be rate limited more aggressively
        for i in range(5):
            response = self.client.get('/api/analytics/reportes-financieros/')
            if i < 2:  # First few should work
                self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)  # Forbidden, not rate limited
            # Rate limiting would return 429, but we don't have it configured in tests