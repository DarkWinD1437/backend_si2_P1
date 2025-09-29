"""
Tests for analytics serializers
"""
from django.test import TestCase
from rest_framework import serializers
from backend.apps.analytics.tests.test_base import AnalyticsTestBase
from backend.apps.analytics.serializers import (
    ReporteFinancieroCreateSerializer,
    ReporteFinancieroReadSerializer,
    ReporteSeguridadCreateSerializer,
    ReporteSeguridadReadSerializer,
    ReporteUsoAreasCreateSerializer,
    ReporteUsoAreasReadSerializer,
    PrediccionMorosidadCreateSerializer,
    PrediccionMorosidadReadSerializer
)


class ReporteFinancieroSerializerTest(AnalyticsTestBase):

    def test_create_serializer_valid_data(self):
        """Test create serializer with valid data"""
        data = {
            "titulo": "Test Financial Report",
            "descripcion": "Test description",
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

        serializer = ReporteFinancieroCreateSerializer(
            data=data,
            context={'request': self.get_request_with_user(self.user_admin)}
        )

        self.assertTrue(serializer.is_valid())
        reporte = serializer.save()
        self.assertEqual(reporte.titulo, "Test Financial Report")
        self.assertEqual(reporte.generado_por, self.user_admin)

    def test_create_serializer_invalid_tipo(self):
        """Test create serializer with invalid tipo"""
        data = {
            "titulo": "Test Report",
            "tipo": "invalid_type",
            "periodo": "mensual",
            "formato": "pdf",
            "fecha_inicio": "2024-01-01",
            "fecha_fin": "2024-01-31"
        }

        serializer = ReporteFinancieroCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('tipo', serializer.errors)

    def test_create_serializer_invalid_fechas(self):
        """Test create serializer with invalid dates"""
        data = {
            "titulo": "Test Report",
            "tipo": "ingresos",
            "periodo": "mensual",
            "formato": "pdf",
            "fecha_inicio": "2024-01-31",
            "fecha_fin": "2024-01-01"  # End before start
        }

        serializer = ReporteFinancieroCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('fecha_fin', serializer.errors)

    def test_read_serializer_includes_user_info(self):
        """Test read serializer includes user info"""
        reporte = self.create_test_financial_report()

        serializer = ReporteFinancieroReadSerializer(reporte)
        data = serializer.data

        self.assertIn('generado_por_info', data)
        self.assertEqual(data['generado_por_info']['username'], 'admin_test')
        self.assertEqual(data['generado_por_info']['role'], 'admin')

    def test_read_serializer_includes_all_fields(self):
        """Test read serializer includes all necessary fields"""
        reporte = self.create_test_financial_report(
            descripcion="Test description",
            filtros_aplicados={"categoria": "todas"}
        )

        serializer = ReporteFinancieroReadSerializer(reporte)
        data = serializer.data

        expected_fields = [
            'id', 'titulo', 'descripcion', 'tipo', 'periodo', 'formato',
            'fecha_inicio', 'fecha_fin', 'fecha_generacion', 'generado_por',
            'generado_por_info', 'datos', 'total_registros', 'filtros_aplicados'
        ]

        for field in expected_fields:
            self.assertIn(field, data)


class ReporteSeguridadSerializerTest(AnalyticsTestBase):

    def test_create_serializer_valid_data(self):
        """Test security report create serializer"""
        data = {
            "titulo": "Test Security Report",
            "descripcion": "Test security description",
            "tipo": "incidentes",
            "periodo": "semanal",
            "fecha_inicio": "2024-01-01T00:00:00Z",
            "fecha_fin": "2024-01-07T23:59:59Z",
            "filtros_aplicados": {
                "nivel_critico": True
            }
        }

        serializer = ReporteSeguridadCreateSerializer(
            data=data,
            context={'request': self.get_request_with_user(self.user_admin)}
        )

        self.assertTrue(serializer.is_valid())
        reporte = serializer.save()
        self.assertEqual(reporte.titulo, "Test Security Report")

    def test_read_serializer_includes_event_counts(self):
        """Test security report read serializer includes event counts"""
        reporte = self.create_test_security_report(
            total_eventos=15,
            eventos_criticos=3,
            alertas_generadas=12
        )

        serializer = ReporteSeguridadReadSerializer(reporte)
        data = serializer.data

        self.assertEqual(data['total_eventos'], 15)
        self.assertEqual(data['eventos_criticos'], 3)
        self.assertEqual(data['alertas_generadas'], 12)


class ReporteUsoAreasSerializerTest(AnalyticsTestBase):

    def test_create_serializer_valid_data(self):
        """Test area usage report create serializer"""
        data = {
            "titulo": "Test Area Usage Report",
            "descripcion": "Test area description",
            "area": "piscina",
            "periodo": "mensual",
            "metrica_principal": "ocupacion",
            "fecha_inicio": "2024-01-01",
            "fecha_fin": "2024-01-31",
            "filtros_aplicados": {
                "dias_semana": ["sabado", "domingo"]
            }
        }

        serializer = ReporteUsoAreasCreateSerializer(
            data=data,
            context={'request': self.get_request_with_user(self.user_admin)}
        )

        self.assertTrue(serializer.is_valid())
        reporte = serializer.save()
        self.assertEqual(reporte.area, "piscina")

    def test_read_serializer_includes_usage_metrics(self):
        """Test area usage report read serializer includes metrics"""
        reporte = self.create_test_area_usage_report(
            total_reservas=245,
            horas_ocupacion=1250.5,
            tasa_ocupacion_promedio=68.5
        )

        serializer = ReporteUsoAreasReadSerializer(reporte)
        data = serializer.data

        self.assertEqual(data['total_reservas'], 245)
        self.assertEqual(data['horas_ocupacion'], 1250.5)
        self.assertEqual(data['tasa_ocupacion_promedio'], 68.5)


class PrediccionMorosidadSerializerTest(AnalyticsTestBase):

    def test_create_serializer_valid_data(self):
        """Test prediction create serializer"""
        data = {
            "titulo": "Test Prediction",
            "descripcion": "Test prediction description",
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

        serializer = PrediccionMorosidadCreateSerializer(
            data=data,
            context={'request': self.get_request_with_user(self.user_admin)}
        )

        self.assertTrue(serializer.is_valid())
        prediccion = serializer.save()
        self.assertEqual(prediccion.modelo_usado, "random_forest")

    def test_read_serializer_includes_prediction_results(self):
        """Test prediction read serializer includes results"""
        resultados = {
            'predicciones_por_residente': [
                {'residente_id': 1, 'riesgo_morosidad': 'bajo', 'probabilidad': 0.15}
            ],
            'estadisticas_generales': {
                'riesgo_bajo': 30, 'riesgo_medio': 12, 'riesgo_alto': 8
            }
        }

        prediccion = self.create_test_prediction(
            resultados=resultados,
            metricas_evaluacion={
                'accuracy': 0.852, 'precision': 0.82
            }
        )

        serializer = PrediccionMorosidadReadSerializer(prediccion)
        data = serializer.data

        self.assertIn('resultados', data)
        self.assertIn('metricas_evaluacion', data)
        self.assertEqual(data['precision_modelo'], 85.2)
        self.assertEqual(data['riesgo_porcentaje'], 40.0)

    def test_serializer_invalid_modelo(self):
        """Test serializer with invalid model"""
        data = {
            "titulo": "Test Prediction",
            "modelo_usado": "invalid_model",
            "periodo_predicho": "Próximos 3 meses"
        }

        serializer = PrediccionMorosidadCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('modelo_usado', serializer.errors)