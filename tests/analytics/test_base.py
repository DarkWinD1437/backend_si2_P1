"""
Base classes and utilities for analytics tests
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from django.utils import timezone
from datetime import timedelta
from backend.apps.analytics.models import *


class AnalyticsTestBase(APITestCase):
    """Base class for analytics tests with common setup"""

    def setUp(self):
        """Set up test users and authentication"""
        User = get_user_model()

        # Create test users with different roles
        self.user_admin = User.objects.create_user(
            username='admin_test',
            email='admin@test.com',
            password='password123',
            role='admin',
            first_name='Admin',
            last_name='Test'
        )

        self.user_staff = User.objects.create_user(
            username='staff_test',
            email='staff@test.com',
            password='password123',
            role='staff',
            first_name='Staff',
            last_name='Test'
        )

        self.user_resident = User.objects.create_user(
            username='resident_test',
            email='resident@test.com',
            password='password123',
            role='resident',
            first_name='Resident',
            last_name='Test'
        )

    def authenticate_as_admin(self):
        """Authenticate as admin user"""
        self.client.force_authenticate(user=self.user_admin)

    def authenticate_as_staff(self):
        """Authenticate as staff user"""
        self.client.force_authenticate(user=self.user_staff)

    def authenticate_as_resident(self):
        """Authenticate as resident user"""
        self.client.force_authenticate(user=self.user_resident)

    def get_request_with_user(self, user):
        """Create a mock request with user for serializers"""
        from rest_framework.test import APIRequestFactory
        factory = APIRequestFactory()
        request = factory.get('/')
        request.user = user
        return request

    def create_test_financial_report(self, **kwargs):
        """Helper to create test financial report"""
        defaults = {
            'titulo': 'Test Financial Report',
            'tipo': 'ingresos',
            'periodo': 'mensual',
            'formato': 'pdf',
            'fecha_inicio': '2024-01-01',
            'fecha_fin': '2024-01-31',
            'generado_por': self.user_admin,
            'datos': {},  # Required field
            'filtros_aplicados': {}
        }
        defaults.update(kwargs)
        return ReporteFinanciero.objects.create(**defaults)

    def create_test_security_report(self, **kwargs):
        """Helper to create test security report"""
        defaults = {
            'titulo': 'Test Security Report',
            'tipo': 'incidentes',
            'periodo': 'semanal',
            'fecha_inicio': '2024-01-01T00:00:00Z',
            'fecha_fin': '2024-01-07T23:59:59Z',
            'generado_por': self.user_admin,
            'datos': {},  # Required field
            'filtros_aplicados': {}
        }
        defaults.update(kwargs)
        return ReporteSeguridad.objects.create(**defaults)

    def create_test_area_usage_report(self, **kwargs):
        """Helper to create test area usage report"""
        defaults = {
            'titulo': 'Test Area Usage Report',
            'area': 'piscina',
            'periodo': 'mensual',
            'metrica_principal': 'ocupacion',
            'fecha_inicio': '2024-01-01',
            'fecha_fin': '2024-01-31',
            'generado_por': self.user_admin,
            'datos': {},  # Required field
            'filtros_aplicados': {}
        }
        defaults.update(kwargs)
        return ReporteUsoAreas.objects.create(**defaults)

    def create_test_prediction(self, **kwargs):
        """Helper to create test prediction"""
        defaults = {
            'titulo': 'Test Prediction',
            'modelo_usado': 'random_forest',
            'nivel_confianza': 'alto',
            'fecha_prediccion': timezone.now(),
            'periodo_predicho': 'Próximos 3 meses',
            'generado_por': self.user_admin,
            'total_residentes_analizados': 50,
            'residentes_riesgo_alto': 8,
            'residentes_riesgo_medio': 12,
            'precision_modelo': 85.2,
            'datos_entrada': {},  # Required field
            'resultados': {},  # Required field
            'parametros_modelo': {}
        }
        defaults.update(kwargs)
        return PrediccionMorosidad.objects.create(**defaults)