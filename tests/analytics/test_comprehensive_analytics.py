"""
Tests exhaustivos para el módulo de Analytics
Tests para todos los endpoints y funcionalidades del módulo de reportes y analítica
"""

import json
from datetime import datetime, timedelta
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import patch, MagicMock

from backend.apps.analytics.models import (
    ReporteFinanciero,
    ReporteSeguridad,
    ReporteUsoAreas,
    PrediccionMorosidad
)
from backend.apps.analytics.serializers import (
    ReporteFinancieroSerializer,
    ReporteSeguridadSerializer,
    ReporteUsoAreasSerializer,
    PrediccionMorosidadSerializer
)

User = get_user_model()


class AnalyticsModelsTestCase(TestCase):
    """Tests para modelos de Analytics"""

    def setUp(self):
        """Configurar datos de prueba"""
        self.user = User.objects.create_user(
            username='testadmin',
            email='admin@test.com',
            password='testpass123',
            role='admin'
        )

    def test_reporte_financiero_creation(self):
        """Test creación de reporte financiero"""
        reporte = ReporteFinanciero.objects.create(
            titulo='Reporte de Ingresos',
            descripcion='Análisis de ingresos mensuales',
            tipo='ingresos',
            periodo='mensual',
            formato='json',
            fecha_inicio=datetime.now().date(),
            fecha_fin=datetime.now().date(),
            generado_por=self.user,
            datos={'total': 1000},
            total_registros=10
        )

        self.assertEqual(reporte.titulo, 'Reporte de Ingresos')
        self.assertEqual(reporte.tipo, 'ingresos')
        self.assertEqual(reporte.generado_por, self.user)
        self.assertEqual(reporte.total_registros, 10)

    def test_reporte_seguridad_creation(self):
        """Test creación de reporte de seguridad"""
        reporte = ReporteSeguridad.objects.create(
            titulo='Reporte de Accesos',
            descripcion='Análisis de accesos al sistema',
            tipo='accesos',
            periodo='diario',
            fecha_inicio=datetime.now().date(),
            fecha_fin=datetime.now().date(),
            generado_por=self.user,
            datos={'total_accesos': 150},
            total_eventos=150,
            eventos_criticos=5,
            alertas_generadas=2
        )

        self.assertEqual(reporte.titulo, 'Reporte de Accesos')
        self.assertEqual(reporte.tipo, 'accesos')
        self.assertEqual(reporte.total_eventos, 150)
        self.assertEqual(reporte.eventos_criticos, 5)

    def test_reporte_uso_areas_creation(self):
        """Test creación de reporte de uso de áreas"""
        reporte = ReporteUsoAreas.objects.create(
            titulo='Uso del Gimnasio',
            descripcion='Análisis de ocupación del gimnasio',
            area='gimnasio',
            periodo='semanal',
            metrica_principal='ocupacion',
            fecha_inicio=datetime.now().date(),
            fecha_fin=datetime.now().date(),
            generado_por=self.user,
            datos={'tasa_ocupacion': 75.5},
            total_reservas=50,
            horas_ocupacion=125.5,
            tasa_ocupacion_promedio=75.5
        )

        self.assertEqual(reporte.area, 'gimnasio')
        self.assertEqual(reporte.metrica_principal, 'ocupacion')
        self.assertEqual(reporte.total_reservas, 50)

    def test_prediccion_morosidad_creation(self):
        """Test creación de predicción de morosidad"""
        prediccion = PrediccionMorosidad.objects.create(
            titulo='Predicción de Morosidad',
            descripcion='Análisis predictivo de riesgo de morosidad',
            modelo_usado='random_forest',
            periodo_predicho='3_meses',
            generado_por=self.user,
            datos_entrada={'residentes': 50},
            resultados={'riesgo_alto': 8},
            total_residentes_analizados=50,
            residentes_riesgo_alto=8,
            residentes_riesgo_medio=12,
            precision_modelo=85.2,
            nivel_confianza='alto'
        )

        self.assertEqual(prediccion.modelo_usado, 'random_forest')
        self.assertEqual(prediccion.total_residentes_analizados, 50)
        self.assertEqual(prediccion.residentes_riesgo_alto, 8)
        self.assertEqual(prediccion.precision_modelo, 85.2)


class AnalyticsSerializersTestCase(TestCase):
    """Tests para serializers de Analytics"""

    def setUp(self):
        """Configurar datos de prueba"""
        self.user = User.objects.create_user(
            username='testadmin',
            email='admin@test.com',
            password='testpass123',
            role='admin'
        )

    def test_reporte_financiero_serializer(self):
        """Test serialización de reporte financiero"""
        reporte = ReporteFinanciero.objects.create(
            titulo='Test Report',
            tipo='ingresos',
            periodo='mensual',
            formato='json',
            fecha_inicio=datetime.now().date(),
            fecha_fin=datetime.now().date(),
            generado_por=self.user,
            datos={'test': 'data'},
            total_registros=5
        )

        serializer = ReporteFinancieroSerializer(reporte)
        data = serializer.data

        self.assertEqual(data['titulo'], 'Test Report')
        self.assertEqual(data['tipo'], 'ingresos')
        self.assertIn('generado_por', data)
        self.assertIn('fecha_generacion', data)

    def test_reporte_seguridad_serializer(self):
        """Test serialización de reporte de seguridad"""
        reporte = ReporteSeguridad.objects.create(
            titulo='Security Report',
            tipo='accesos',
            periodo='diario',
            fecha_inicio=datetime.now().date(),
            fecha_fin=datetime.now().date(),
            generado_por=self.user,
            datos={'test': 'data'},
            total_eventos=100,
            eventos_criticos=10,
            alertas_generadas=5
        )

        serializer = ReporteSeguridadSerializer(reporte)
        data = serializer.data

        self.assertEqual(data['titulo'], 'Security Report')
        self.assertEqual(data['total_eventos'], 100)
        self.assertEqual(data['eventos_criticos'], 10)

    def test_reporte_uso_areas_serializer(self):
        """Test serialización de reporte de uso de áreas"""
        reporte = ReporteUsoAreas.objects.create(
            titulo='Area Usage Report',
            area='gimnasio',
            periodo='semanal',
            metrica_principal='ocupacion',
            fecha_inicio=datetime.now().date(),
            fecha_fin=datetime.now().date(),
            generado_por=self.user,
            datos={'test': 'data'},
            total_reservas=25,
            horas_ocupacion=50.5,
            tasa_ocupacion_promedio=65.0
        )

        serializer = ReporteUsoAreasSerializer(reporte)
        data = serializer.data

        self.assertEqual(data['area'], 'gimnasio')
        self.assertEqual(data['total_reservas'], 25)
        self.assertEqual(data['tasa_ocupacion_promedio'], 65.0)

    def test_prediccion_morosidad_serializer(self):
        """Test serialización de predicción de morosidad"""
        prediccion = PrediccionMorosidad.objects.create(
            titulo='Morosidad Prediction',
            modelo_usado='xgboost',
            periodo_predicho='6_meses',
            generado_por=self.user,
            datos_entrada={'test': 'input'},
            resultados={'test': 'output'},
            total_residentes_analizados=40,
            residentes_riesgo_alto=6,
            residentes_riesgo_medio=8,
            precision_modelo=87.1,
            nivel_confianza='alto'
        )

        serializer = PrediccionMorosidadSerializer(prediccion)
        data = serializer.data

        self.assertEqual(data['modelo_usado'], 'xgboost')
        self.assertEqual(data['total_residentes_analizados'], 40)
        self.assertEqual(data['precision_modelo'], 87.1)


class AnalyticsAPITestCase(APITestCase):
    """Tests exhaustivos para APIs de Analytics"""

    def setUp(self):
        """Configurar datos de prueba"""
        # Crear usuarios con diferentes roles
        self.admin_user = User.objects.create_user(
            username='admin',
            email='admin@test.com',
            password='admin123',
            role='admin'
        )

        self.security_user = User.objects.create_user(
            username='security',
            email='security@test.com',
            password='security123',
            role='security'
        )

        self.maintenance_user = User.objects.create_user(
            username='maintenance',
            email='maintenance@test.com',
            password='maintenance123',
            role='maintenance'
        )

        self.resident_user = User.objects.create_user(
            username='resident',
            email='resident@test.com',
            password='resident123',
            role='resident'
        )

        # Crear cliente API
        self.client = APIClient()

        # URLs base
        self.reportes_financieros_url = reverse('analytics:reporte-financiero-list')
        self.reportes_seguridad_url = reverse('analytics:reporte-seguridad-list')
        self.reportes_uso_areas_url = reverse('analytics:reporte-uso-areas-list')
        self.predicciones_morosidad_url = reverse('analytics:prediccion-morosidad-list')

    # ==================== REPORTES FINANCIEROS ====================

    def test_reporte_financiero_list_unauthenticated(self):
        """Test acceso no autorizado a lista de reportes financieros"""
        response = self.client.get(self.reportes_financieros_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_reporte_financiero_list_admin(self):
        """Test lista de reportes financieros como admin"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.reportes_financieros_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_reporte_financiero_list_resident_denied(self):
        """Test acceso denegado para residente"""
        self.client.force_authenticate(user=self.resident_user)
        response = self.client.get(self.reportes_financieros_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_reporte_financiero_create_admin(self):
        """Test creación de reporte financiero como admin"""
        self.client.force_authenticate(user=self.admin_user)

        data = {
            'titulo': 'Reporte de Prueba',
            'descripcion': 'Descripción de prueba',
            'tipo': 'ingresos',
            'periodo': 'mensual',
            'formato': 'json',
            'fecha_inicio': '2024-01-01',
            'fecha_fin': '2024-01-31'
        }

        response = self.client.post(self.reportes_financieros_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['titulo'], 'Reporte de Prueba')
        self.assertEqual(response.data['generado_por']['username'], 'admin')

    def test_reporte_financiero_create_security_denied(self):
        """Test creación denegada para usuario de seguridad"""
        self.client.force_authenticate(user=self.security_user)

        data = {
            'titulo': 'Reporte de Prueba',
            'tipo': 'ingresos',
            'periodo': 'mensual',
            'formato': 'json',
            'fecha_inicio': '2024-01-01',
            'fecha_fin': '2024-01-31'
        }

        response = self.client.post(self.reportes_financieros_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_reporte_financiero_detail_admin(self):
        """Test detalle de reporte financiero como admin"""
        # Crear reporte primero
        reporte = ReporteFinanciero.objects.create(
            titulo='Test Report',
            tipo='ingresos',
            periodo='mensual',
            formato='json',
            fecha_inicio=datetime.now().date(),
            fecha_fin=datetime.now().date(),
            generado_por=self.admin_user,
            datos={'test': 'data'},
            total_registros=5
        )

        self.client.force_authenticate(user=self.admin_user)
        url = reverse('analytics:reporte-financiero-detail', kwargs={'pk': reporte.pk})
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['titulo'], 'Test Report')

    def test_reporte_financiero_update_admin(self):
        """Test actualización de reporte financiero como admin"""
        reporte = ReporteFinanciero.objects.create(
            titulo='Test Report',
            tipo='ingresos',
            periodo='mensual',
            formato='json',
            fecha_inicio=datetime.now().date(),
            fecha_fin=datetime.now().date(),
            generado_por=self.admin_user,
            datos={'test': 'data'},
            total_registros=5
        )

        self.client.force_authenticate(user=self.admin_user)
        url = reverse('analytics:reporte-financiero-detail', kwargs={'pk': reporte.pk})

        data = {'titulo': 'Updated Report'}
        response = self.client.patch(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['titulo'], 'Updated Report')

    def test_reporte_financiero_delete_admin(self):
        """Test eliminación de reporte financiero como admin"""
        reporte = ReporteFinanciero.objects.create(
            titulo='Test Report',
            tipo='ingresos',
            periodo='mensual',
            formato='json',
            fecha_inicio=datetime.now().date(),
            fecha_fin=datetime.now().date(),
            generado_por=self.admin_user,
            datos={'test': 'data'},
            total_registros=5
        )

        self.client.force_authenticate(user=self.admin_user)
        url = reverse('analytics:reporte-financiero-detail', kwargs={'pk': reporte.pk})
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(ReporteFinanciero.objects.filter(pk=reporte.pk).exists())

    @patch('backend.apps.analytics.views.ReporteFinancieroViewSet._generar_datos_financieros')
    def test_generar_reporte_financiero_ingresos(self, mock_generar):
        """Test generación de reporte financiero de ingresos"""
        mock_generar.return_value = {
            'total_ingresos': 15000.00,
            'total_registros': 150
        }

        self.client.force_authenticate(user=self.admin_user)

        data = {
            'titulo': 'Reporte de Ingresos',
            'tipo': 'ingresos',
            'periodo': 'mensual',
            'formato': 'json',
            'fecha_inicio': '2024-01-01',
            'fecha_fin': '2024-01-31'
        }

        url = reverse('analytics:reporte-financiero-generar-reporte')
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['tipo'], 'ingresos')
        self.assertEqual(response.data['total_registros'], 150)

    @patch('backend.apps.analytics.views.ReporteFinancieroViewSet._generar_datos_financieros')
    def test_generar_reporte_financiero_egresos(self, mock_generar):
        """Test generación de reporte financiero de egresos"""
        mock_generar.return_value = {
            'total_egresos': 8500.00,
            'total_registros': 89
        }

        self.client.force_authenticate(user=self.admin_user)

        data = {
            'titulo': 'Reporte de Egresos',
            'tipo': 'egresos',
            'periodo': 'mensual',
            'formato': 'json',
            'fecha_inicio': '2024-01-01',
            'fecha_fin': '2024-01-31'
        }

        url = reverse('analytics:reporte-financiero-generar-reporte')
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['tipo'], 'egresos')

    @patch('backend.apps.analytics.views.ReporteFinancieroViewSet._generar_datos_financieros')
    def test_generar_reporte_financiero_balance(self, mock_generar):
        """Test generación de reporte financiero de balance"""
        mock_generar.return_value = {
            'balance_neto': 6500.00,
            'total_registros': 239
        }

        self.client.force_authenticate(user=self.admin_user)

        data = {
            'titulo': 'Balance General',
            'tipo': 'balance',
            'periodo': 'mensual',
            'formato': 'json',
            'fecha_inicio': '2024-01-01',
            'fecha_fin': '2024-01-31'
        }

        url = reverse('analytics:reporte-financiero-generar-reporte')
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['tipo'], 'balance')

    @patch('backend.apps.analytics.views.ReporteFinancieroViewSet._generar_datos_financieros')
    def test_generar_reporte_financiero_morosidad(self, mock_generar):
        """Test generación de reporte financiero de morosidad"""
        mock_generar.return_value = {
            'porcentaje_morosos': 16.0,
            'total_registros': 50
        }

        self.client.force_authenticate(user=self.admin_user)

        data = {
            'titulo': 'Análisis de Morosidad',
            'tipo': 'morosidad',
            'periodo': 'mensual',
            'formato': 'json',
            'fecha_inicio': '2024-01-01',
            'fecha_fin': '2024-01-31'
        }

        url = reverse('analytics:reporte-financiero-generar-reporte')
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['tipo'], 'morosidad')

    def test_generar_reporte_financiero_security_denied(self):
        """Test generación denegada para usuario de seguridad"""
        self.client.force_authenticate(user=self.security_user)

        data = {
            'titulo': 'Reporte de Prueba',
            'tipo': 'ingresos',
            'periodo': 'mensual',
            'formato': 'json',
            'fecha_inicio': '2024-01-01',
            'fecha_fin': '2024-01-31'
        }

        url = reverse('analytics:reporte-financiero-generar-reporte')
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ==================== REPORTES DE SEGURIDAD ====================

    def test_reporte_seguridad_list_admin(self):
        """Test lista de reportes de seguridad como admin"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.reportes_seguridad_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_reporte_seguridad_list_security_allowed(self):
        """Test lista de reportes de seguridad como usuario de seguridad"""
        self.client.force_authenticate(user=self.security_user)
        response = self.client.get(self.reportes_seguridad_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_reporte_seguridad_create_security(self):
        """Test creación de reporte de seguridad como usuario de seguridad"""
        self.client.force_authenticate(user=self.security_user)

        data = {
            'titulo': 'Reporte de Seguridad',
            'tipo': 'accesos',
            'periodo': 'diario',
            'fecha_inicio': '2024-01-01',
            'fecha_fin': '2024-01-31'
        }

        response = self.client.post(self.reportes_seguridad_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @patch('backend.apps.analytics.views.ReporteSeguridadViewSet._generar_datos_seguridad')
    def test_generar_reporte_seguridad_accesos(self, mock_generar):
        """Test generación de reporte de seguridad de accesos"""
        mock_generar.return_value = {
            'total_accesos': 1250,
            'total_eventos': 1250,
            'eventos_criticos': 50,
            'alertas_generadas': 5
        }

        self.client.force_authenticate(user=self.security_user)

        data = {
            'titulo': 'Reporte de Accesos',
            'tipo': 'accesos',
            'periodo': 'diario',
            'fecha_inicio': '2024-01-01',
            'fecha_fin': '2024-01-31'
        }

        url = reverse('analytics:reporte-seguridad-generar-reporte')
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['tipo'], 'accesos')
        self.assertEqual(response.data['total_eventos'], 1250)

    @patch('backend.apps.analytics.views.ReporteSeguridadViewSet._generar_datos_seguridad')
    def test_generar_reporte_seguridad_incidentes(self, mock_generar):
        """Test generación de reporte de seguridad de incidentes"""
        mock_generar.return_value = {
            'total_incidentes': 12,
            'total_eventos': 12,
            'eventos_criticos': 3,
            'alertas_generadas': 12
        }

        self.client.force_authenticate(user=self.admin_user)

        data = {
            'titulo': 'Reporte de Incidentes',
            'tipo': 'incidentes',
            'periodo': 'semanal',
            'fecha_inicio': '2024-01-01',
            'fecha_fin': '2024-01-31'
        }

        url = reverse('analytics:reporte-seguridad-generar-reporte')
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['tipo'], 'incidentes')

    # ==================== REPORTES DE USO DE ÁREAS ====================

    def test_reporte_uso_areas_list_admin(self):
        """Test lista de reportes de uso de áreas como admin"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.reportes_uso_areas_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_reporte_uso_areas_create_admin(self):
        """Test creación de reporte de uso de áreas como admin"""
        self.client.force_authenticate(user=self.admin_user)

        data = {
            'titulo': 'Uso del Gimnasio',
            'area': 'gimnasio',
            'periodo': 'semanal',
            'metrica_principal': 'ocupacion',
            'fecha_inicio': '2024-01-01',
            'fecha_fin': '2024-01-31'
        }

        response = self.client.post(self.reportes_uso_areas_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @patch('backend.apps.analytics.views.ReporteUsoAreasViewSet._generar_datos_uso_areas')
    def test_generar_reporte_uso_areas_ocupacion(self, mock_generar):
        """Test generación de reporte de uso de áreas - ocupación"""
        mock_generar.return_value = {
            'tasa_ocupacion_promedio': 68.5,
            'total_reservas': 245,
            'horas_ocupacion': 1250.5,
            'tasa_ocupacion_promedio': 68.5
        }

        self.client.force_authenticate(user=self.admin_user)

        data = {
            'titulo': 'Ocupación del Gimnasio',
            'area': 'gimnasio',
            'periodo': 'semanal',
            'metrica_principal': 'ocupacion',
            'fecha_inicio': '2024-01-01',
            'fecha_fin': '2024-01-31'
        }

        url = reverse('analytics:reporte-uso-areas-generar-reporte')
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['area'], 'gimnasio')
        self.assertEqual(response.data['metrica_principal'], 'ocupacion')

    @patch('backend.apps.analytics.views.ReporteUsoAreasViewSet._generar_datos_uso_areas')
    def test_generar_reporte_uso_areas_reservas(self, mock_generar):
        """Test generación de reporte de uso de áreas - reservas"""
        mock_generar.return_value = {
            'total_reservas': 245,
            'horas_ocupacion': 1250.5,
            'tasa_ocupacion_promedio': 68.5
        }

        self.client.force_authenticate(user=self.admin_user)

        data = {
            'titulo': 'Reservas de Piscina',
            'area': 'piscina',
            'periodo': 'mensual',
            'metrica_principal': 'reservas',
            'fecha_inicio': '2024-01-01',
            'fecha_fin': '2024-01-31'
        }

        url = reverse('analytics:reporte-uso-areas-generar-reporte')
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['area'], 'piscina')
        self.assertEqual(response.data['metrica_principal'], 'reservas')

    def test_generar_reporte_uso_areas_maintenance_denied(self):
        """Test generación denegada para usuario de mantenimiento"""
        self.client.force_authenticate(user=self.maintenance_user)

        data = {
            'titulo': 'Reporte de Prueba',
            'area': 'gimnasio',
            'periodo': 'semanal',
            'metrica_principal': 'ocupacion',
            'fecha_inicio': '2024-01-01',
            'fecha_fin': '2024-01-31'
        }

        url = reverse('analytics:reporte-uso-areas-generar-reporte')
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ==================== PREDICCIONES DE MOROSIDAD ====================

    def test_prediccion_morosidad_list_admin(self):
        """Test lista de predicciones de morosidad como admin"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.predicciones_morosidad_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_prediccion_morosidad_create_admin(self):
        """Test creación de predicción de morosidad como admin"""
        self.client.force_authenticate(user=self.admin_user)

        data = {
            'titulo': 'Predicción de Morosidad',
            'modelo_usado': 'random_forest',
            'periodo_predicho': '3_meses'
        }

        response = self.client.post(self.predicciones_morosidad_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    @patch('backend.apps.analytics.views.PrediccionMorosidadViewSet._generar_prediccion_ia')
    def test_generar_prediccion_morosidad_random_forest(self, mock_generar):
        """Test generación de predicción de morosidad con Random Forest"""
        mock_generar.return_value = {
            'resultados': {'test': 'data'},
            'total_residentes_analizados': 50,
            'residentes_riesgo_alto': 8,
            'residentes_riesgo_medio': 12,
            'precision_modelo': 85.2,
            'nivel_confianza': 'alto',
            'metricas_evaluacion': {'accuracy': 0.85}
        }

        self.client.force_authenticate(user=self.admin_user)

        data = {
            'titulo': 'Predicción con Random Forest',
            'modelo_usado': 'random_forest',
            'periodo_predicho': '3_meses'
        }

        url = reverse('analytics:prediccion-morosidad-generar-prediccion')
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['modelo_usado'], 'random_forest')
        self.assertEqual(response.data['precision_modelo'], 85.2)

    @patch('backend.apps.analytics.views.PrediccionMorosidadViewSet._generar_prediccion_ia')
    def test_generar_prediccion_morosidad_xgboost(self, mock_generar):
        """Test generación de predicción de morosidad con XGBoost"""
        mock_generar.return_value = {
            'resultados': {'test': 'data'},
            'total_residentes_analizados': 50,
            'residentes_riesgo_alto': 6,
            'residentes_riesgo_medio': 10,
            'precision_modelo': 87.1,
            'nivel_confianza': 'alto',
            'metricas_evaluacion': {'accuracy': 0.87}
        }

        self.client.force_authenticate(user=self.admin_user)

        data = {
            'titulo': 'Predicción con XGBoost',
            'modelo_usado': 'xgboost',
            'periodo_predicho': '6_meses'
        }

        url = reverse('analytics:prediccion-morosidad-generar-prediccion')
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['modelo_usado'], 'xgboost')
        self.assertEqual(response.data['nivel_confianza'], 'alto')

    @patch('backend.apps.analytics.views.PrediccionMorosidadViewSet._generar_prediccion_ia')
    def test_generar_prediccion_morosidad_ensemble(self, mock_generar):
        """Test generación de predicción de morosidad con Ensemble"""
        mock_generar.return_value = {
            'resultados': {'test': 'data'},
            'total_residentes_analizados': 50,
            'residentes_riesgo_alto': 5,
            'residentes_riesgo_medio': 8,
            'precision_modelo': 89.4,
            'nivel_confianza': 'alto',
            'metricas_evaluacion': {'accuracy': 0.89}
        }

        self.client.force_authenticate(user=self.admin_user)

        data = {
            'titulo': 'Predicción con Ensemble',
            'modelo_usado': 'ensemble',
            'periodo_predicho': '12_meses'
        }

        url = reverse('analytics:prediccion-morosidad-generar-prediccion')
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['modelo_usado'], 'ensemble')
        self.assertEqual(response.data['precision_modelo'], 89.4)

    def test_generar_prediccion_morosidad_security_denied(self):
        """Test generación denegada para usuario de seguridad"""
        self.client.force_authenticate(user=self.security_user)

        data = {
            'titulo': 'Predicción de Prueba',
            'modelo_usado': 'random_forest',
            'periodo_predicho': '3_meses'
        }

        url = reverse('analytics:prediccion-morosidad-generar-prediccion')
        response = self.client.post(url, data, format='json')

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    # ==================== TESTS DE FILTROS Y BÚSQUEDA ====================

    def test_reporte_financiero_filter_by_tipo(self):
        """Test filtrado de reportes financieros por tipo"""
        # Crear reportes de diferentes tipos
        ReporteFinanciero.objects.create(
            titulo='Ingresos Report', tipo='ingresos', periodo='mensual', formato='json',
            fecha_inicio=datetime.now().date(), fecha_fin=datetime.now().date(),
            generado_por=self.admin_user, datos={}, total_registros=10
        )
        ReporteFinanciero.objects.create(
            titulo='Egresos Report', tipo='egresos', periodo='mensual', formato='json',
            fecha_inicio=datetime.now().date(), fecha_fin=datetime.now().date(),
            generado_por=self.admin_user, datos={}, total_registros=5
        )

        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(f'{self.reportes_financieros_url}?tipo=ingresos')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['tipo'], 'ingresos')

    def test_reporte_seguridad_filter_by_tipo(self):
        """Test filtrado de reportes de seguridad por tipo"""
        ReporteSeguridad.objects.create(
            titulo='Accesos Report', tipo='accesos', periodo='diario',
            fecha_inicio=datetime.now().date(), fecha_fin=datetime.now().date(),
            generado_por=self.admin_user, datos={}, total_eventos=100,
            eventos_criticos=5, alertas_generadas=2
        )

        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(f'{self.reportes_seguridad_url}?tipo=accesos')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['tipo'], 'accesos')

    def test_reporte_uso_areas_filter_by_area(self):
        """Test filtrado de reportes de uso de áreas por área"""
        ReporteUsoAreas.objects.create(
            titulo='Gimnasio Report', area='gimnasio', periodo='semanal',
            metrica_principal='ocupacion', fecha_inicio=datetime.now().date(),
            fecha_fin=datetime.now().date(), generado_por=self.admin_user,
            datos={}, total_reservas=25, horas_ocupacion=50.5, tasa_ocupacion_promedio=65.0
        )

        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(f'{self.reportes_uso_areas_url}?area=gimnasio')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['area'], 'gimnasio')

    def test_prediccion_morosidad_filter_by_modelo(self):
        """Test filtrado de predicciones por modelo"""
        PrediccionMorosidad.objects.create(
            titulo='RF Prediction', modelo_usado='random_forest', periodo_predicho='3_meses',
            generado_por=self.admin_user, datos_entrada={}, resultados={},
            total_residentes_analizados=50, residentes_riesgo_alto=8,
            residentes_riesgo_medio=12, precision_modelo=85.2, nivel_confianza='alto'
        )

        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(f'{self.predicciones_morosidad_url}?modelo=random_forest')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['modelo_usado'], 'random_forest')

    # ==================== TESTS DE VALIDACIÓN ====================

    def test_reporte_financiero_invalid_dates(self):
        """Test validación de fechas inválidas en reporte financiero"""
        self.client.force_authenticate(user=self.admin_user)

        data = {
            'titulo': 'Invalid Dates Report',
            'tipo': 'ingresos',
            'periodo': 'mensual',
            'formato': 'json',
            'fecha_inicio': '2024-01-31',  # Fecha fin antes que fecha inicio
            'fecha_fin': '2024-01-01'
        }

        response = self.client.post(self.reportes_financieros_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reporte_seguridad_invalid_tipo(self):
        """Test validación de tipo inválido en reporte de seguridad"""
        self.client.force_authenticate(user=self.security_user)

        data = {
            'titulo': 'Invalid Type Report',
            'tipo': 'invalid_type',
            'periodo': 'diario',
            'fecha_inicio': '2024-01-01',
            'fecha_fin': '2024-01-31'
        }

        response = self.client.post(self.reportes_seguridad_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reporte_uso_areas_invalid_area(self):
        """Test validación de área inválida en reporte de uso de áreas"""
        self.client.force_authenticate(user=self.admin_user)

        data = {
            'titulo': 'Invalid Area Report',
            'area': 'invalid_area',
            'periodo': 'semanal',
            'metrica_principal': 'ocupacion',
            'fecha_inicio': '2024-01-01',
            'fecha_fin': '2024-01-31'
        }

        response = self.client.post(self.reportes_uso_areas_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_prediccion_morosidad_invalid_modelo(self):
        """Test validación de modelo inválido en predicción de morosidad"""
        self.client.force_authenticate(user=self.admin_user)

        data = {
            'titulo': 'Invalid Model Prediction',
            'modelo_usado': 'invalid_model',
            'periodo_predicho': '3_meses'
        }

        response = self.client.post(self.predicciones_morosidad_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    # ==================== TESTS DE ORDENAMIENTO ====================

    def test_reporte_financiero_ordering(self):
        """Test ordenamiento de reportes financieros por fecha de generación"""
        # Crear reportes en orden inverso
        old_report = ReporteFinanciero.objects.create(
            titulo='Old Report', tipo='ingresos', periodo='mensual', formato='json',
            fecha_inicio=datetime.now().date() - timedelta(days=10),
            fecha_fin=datetime.now().date() - timedelta(days=5),
            generado_por=self.admin_user, datos={}, total_registros=10
        )

        new_report = ReporteFinanciero.objects.create(
            titulo='New Report', tipo='ingresos', periodo='mensual', formato='json',
            fecha_inicio=datetime.now().date(), fecha_fin=datetime.now().date(),
            generado_por=self.admin_user, datos={}, total_registros=5
        )

        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(self.reportes_financieros_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # El primer resultado debería ser el más reciente
        self.assertEqual(response.data[0]['titulo'], 'New Report')
        self.assertEqual(response.data[1]['titulo'], 'Old Report')

    # ==================== TESTS DE CONTEO Y PAGINACIÓN ====================

    def test_reporte_financiero_pagination(self):
        """Test paginación de reportes financieros"""
        # Crear múltiples reportes
        for i in range(25):  # Más que el límite de página típico
            ReporteFinanciero.objects.create(
                titulo=f'Report {i}', tipo='ingresos', periodo='mensual', formato='json',
                fecha_inicio=datetime.now().date(), fecha_fin=datetime.now().date(),
                generado_por=self.admin_user, datos={}, total_registros=10
            )

        self.client.force_authenticate(user=self.admin_user)
        response = self.client.get(f'{self.reportes_financieros_url}?page=1')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verificar que hay resultados (dependiendo de la configuración de paginación)
        self.assertGreater(len(response.data), 0)

    # ==================== TESTS DE INTEGRACIÓN ====================

    def test_full_workflow_reporte_financiero(self):
        """Test workflow completo: crear, leer, actualizar, eliminar reporte financiero"""
        self.client.force_authenticate(user=self.admin_user)

        # 1. Crear reporte
        create_data = {
            'titulo': 'Workflow Test Report',
            'descripcion': 'Prueba de workflow completo',
            'tipo': 'ingresos',
            'periodo': 'mensual',
            'formato': 'json',
            'fecha_inicio': '2024-01-01',
            'fecha_fin': '2024-01-31'
        }

        create_response = self.client.post(self.reportes_financieros_url, create_data, format='json')
        self.assertEqual(create_response.status_code, status.HTTP_201_CREATED)

        report_id = create_response.data['id']

        # 2. Leer reporte
        detail_url = reverse('analytics:reporte-financiero-detail', kwargs={'pk': report_id})
        read_response = self.client.get(detail_url)
        self.assertEqual(read_response.status_code, status.HTTP_200_OK)
        self.assertEqual(read_response.data['titulo'], 'Workflow Test Report')

        # 3. Actualizar reporte
        update_data = {'titulo': 'Updated Workflow Test Report'}
        update_response = self.client.patch(detail_url, update_data, format='json')
        self.assertEqual(update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(update_response.data['titulo'], 'Updated Workflow Test Report')

        # 4. Eliminar reporte
        delete_response = self.client.delete(detail_url)
        self.assertEqual(delete_response.status_code, status.HTTP_204_NO_CONTENT)

        # 5. Verificar eliminación
        verify_response = self.client.get(detail_url)
        self.assertEqual(verify_response.status_code, status.HTTP_404_NOT_FOUND)

    def test_cross_module_integration(self):
        """Test integración entre diferentes módulos de analytics"""
        self.client.force_authenticate(user=self.admin_user)

        # Crear un reporte financiero
        fin_data = {
            'titulo': 'Integration Test - Financial',
            'tipo': 'balance',
            'periodo': 'mensual',
            'formato': 'json',
            'fecha_inicio': '2024-01-01',
            'fecha_fin': '2024-01-31'
        }
        fin_response = self.client.post(self.reportes_financieros_url, fin_data, format='json')
        self.assertEqual(fin_response.status_code, status.HTTP_201_CREATED)

        # Crear un reporte de seguridad
        sec_data = {
            'titulo': 'Integration Test - Security',
            'tipo': 'alertas',
            'periodo': 'diario',
            'fecha_inicio': '2024-01-01',
            'fecha_fin': '2024-01-31'
        }
        sec_response = self.client.post(self.reportes_seguridad_url, sec_data, format='json')
        self.assertEqual(sec_response.status_code, status.HTTP_201_CREATED)

        # Crear un reporte de uso de áreas
        area_data = {
            'titulo': 'Integration Test - Area Usage',
            'area': 'gimnasio',
            'periodo': 'semanal',
            'metrica_principal': 'reservas',
            'fecha_inicio': '2024-01-01',
            'fecha_fin': '2024-01-31'
        }
        area_response = self.client.post(self.reportes_uso_areas_url, area_data, format='json')
        self.assertEqual(area_response.status_code, status.HTTP_201_CREATED)

        # Crear una predicción de morosidad
        pred_data = {
            'titulo': 'Integration Test - Prediction',
            'modelo_usado': 'xgboost',
            'periodo_predicho': '6_meses'
        }
        pred_response = self.client.post(self.predicciones_morosidad_url, pred_data, format='json')
        self.assertEqual(pred_response.status_code, status.HTTP_201_CREATED)

        # Verificar que todos los módulos funcionan juntos
        self.assertEqual(fin_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(sec_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(area_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(pred_response.status_code, status.HTTP_201_CREATED)

    # ==================== TESTS DE PERFORMANCE ====================

    def test_bulk_create_reportes_financieros(self):
        """Test creación masiva de reportes financieros"""
        self.client.force_authenticate(user=self.admin_user)

        # Crear múltiples reportes en lote
        reports_data = []
        for i in range(10):
            reports_data.append({
                'titulo': f'Bulk Report {i}',
                'tipo': 'ingresos',
                'periodo': 'mensual',
                'formato': 'json',
                'fecha_inicio': '2024-01-01',
                'fecha_fin': '2024-01-31'
            })

        # Crear reportes uno por uno (simulando carga masiva)
        created_reports = []
        for data in reports_data:
            response = self.client.post(self.reportes_financieros_url, data, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            created_reports.append(response.data)

        # Verificar que se crearon todos
        self.assertEqual(len(created_reports), 10)

        # Verificar lista completa
        list_response = self.client.get(self.reportes_financieros_url)
        self.assertEqual(list_response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(list_response.data), 10)

    # ==================== TESTS DE ERROR HANDLING ====================

    def test_malformed_json_handling(self):
        """Test manejo de JSON malformado"""
        self.client.force_authenticate(user=self.admin_user)

        # Enviar JSON malformado
        response = self.client.post(
            self.reportes_financieros_url,
            '{"titulo": "Test", "tipo": "ingresos", invalid}',  # JSON malformado
            content_type='application/json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_missing_required_fields(self):
        """Test validación de campos requeridos faltantes"""
        self.client.force_authenticate(user=self.admin_user)

        # Enviar datos sin campos requeridos
        incomplete_data = {
            'titulo': 'Incomplete Report'
            # Faltan tipo, periodo, formato, fechas
        }

        response = self.client.post(self.reportes_financieros_url, incomplete_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_invalid_url_patterns(self):
        """Test URLs inválidas"""
        self.client.force_authenticate(user=self.admin_user)

        # Intentar acceder a un ID que no existe
        invalid_url = reverse('analytics:reporte-financiero-detail', kwargs={'pk': 99999})
        response = self.client.get(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    # ==================== TESTS DE CONCURRENCIA ====================

    def test_concurrent_access_simulation(self):
        """Test simulación de acceso concurrente"""
        import threading
        import time

        results = []
        errors = []

        def create_report(thread_id):
            try:
                client = APIClient()
                client.force_authenticate(user=self.admin_user)

                data = {
                    'titulo': f'Concurrent Report {thread_id}',
                    'tipo': 'ingresos',
                    'periodo': 'mensual',
                    'formato': 'json',
                    'fecha_inicio': '2024-01-01',
                    'fecha_fin': '2024-01-31'
                }

                response = client.post(self.reportes_financieros_url, data, format='json')
                results.append((thread_id, response.status_code))

            except Exception as e:
                errors.append((thread_id, str(e)))

        # Simular 5 usuarios creando reportes concurrentemente
        threads = []
        for i in range(5):
            thread = threading.Thread(target=create_report, args=(i,))
            threads.append(thread)
            thread.start()

        # Esperar a que terminen todos los threads
        for thread in threads:
            thread.join()

        # Verificar resultados
        self.assertEqual(len(results), 5)
        for thread_id, status_code in results:
            self.assertEqual(status_code, status.HTTP_201_CREATED)

        self.assertEqual(len(errors), 0)  # No debería haber errores