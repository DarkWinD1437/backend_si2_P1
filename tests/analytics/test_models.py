"""
Tests for analytics models
"""
from django.core.exceptions import ValidationError
from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from backend.apps.analytics.tests.test_base import AnalyticsTestBase
from backend.apps.analytics.models import ReporteFinanciero, ReporteSeguridad, ReporteUsoAreas, PrediccionMorosidad


class ReporteFinancieroModelTest(AnalyticsTestBase):

    def test_crear_reporte_financiero_basico(self):
        """Test basic creation of financial report"""
        reporte = self.create_test_financial_report()

        self.assertEqual(reporte.titulo, 'Test Financial Report')
        self.assertEqual(reporte.tipo, 'ingresos')
        self.assertEqual(reporte.periodo, 'mensual')
        self.assertEqual(reporte.formato, 'pdf')
        self.assertIsNotNone(reporte.fecha_generacion)
        self.assertEqual(reporte.generado_por, self.user_admin)

    def test_reporte_financiero_con_datos(self):
        """Test financial report with data"""
        datos = {
            'total_ingresos': 15000.00,
            'ingresos_por_mes': {'2024-01': 15000.00},
            'fuentes_ingreso': {'cuotas': 12000.00, 'multas': 3000.00}
        }

        reporte = self.create_test_financial_report(
            datos=datos,
            total_registros=150
        )

        self.assertEqual(reporte.datos['total_ingresos'], 15000.00)
        self.assertEqual(reporte.total_registros, 150)

    def test_validaciones_tipo_reporte(self):
        """Test validations for report type"""
        # Valid types should work
        valid_types = ['ingresos', 'egresos', 'balance']
        for tipo in valid_types:
            reporte = self.create_test_financial_report(tipo=tipo)
            self.assertEqual(reporte.tipo, tipo)

        # Invalid type should raise error
        with self.assertRaises(ValidationError):
            reporte = ReporteFinanciero(
                titulo='Invalid',
                tipo='invalid_type',
                periodo='mensual',
                formato='pdf',
                fecha_inicio='2024-01-01',
                fecha_fin='2024-01-31',
                generado_por=self.user_admin
            )
            reporte.full_clean()

    def test_validaciones_periodo_reporte(self):
        """Test validations for report period"""
        valid_periods = ['diario', 'semanal', 'mensual', 'trimestral', 'anual']
        for periodo in valid_periods:
            reporte = self.create_test_financial_report(periodo=periodo)
            self.assertEqual(reporte.periodo, periodo)

        # Invalid period should raise error
        with self.assertRaises(ValidationError):
            reporte = ReporteFinanciero(
                titulo='Invalid',
                tipo='ingresos',
                periodo='invalid_period',
                formato='pdf',
                fecha_inicio='2024-01-01',
                fecha_fin='2024-01-31',
                generado_por=self.user_admin
            )
            reporte.full_clean()

    def test_validaciones_formato_reporte(self):
        """Test validations for report format"""
        valid_formats = ['pdf', 'excel', 'json']
        for formato in valid_formats:
            reporte = self.create_test_financial_report(formato=formato)
            self.assertEqual(reporte.formato, formato)

        # Invalid format should raise error
        with self.assertRaises(ValidationError):
            reporte = ReporteFinanciero(
                titulo='Invalid',
                tipo='ingresos',
                periodo='mensual',
                formato='invalid_format',
                fecha_inicio='2024-01-01',
                fecha_fin='2024-01-31',
                generado_por=self.user_admin
            )
            reporte.full_clean()

    def test_validaciones_fechas_reporte(self):
        """Test validations for report dates"""
        # Valid dates
        reporte = self.create_test_financial_report(
            fecha_inicio='2024-01-01',
            fecha_fin='2024-01-31'
        )
        self.assertEqual(str(reporte.fecha_inicio), '2024-01-01')
        self.assertEqual(str(reporte.fecha_fin), '2024-01-31')

        # Invalid dates (end before start)
        with self.assertRaises(ValidationError):
            reporte = ReporteFinanciero(
                titulo='Invalid',
                tipo='ingresos',
                periodo='mensual',
                formato='pdf',
                fecha_inicio='2024-01-31',
                fecha_fin='2024-01-01',
                generado_por=self.user_admin
            )
            reporte.full_clean()

    def test_relacion_con_usuario(self):
        """Test relationship with user"""
        reporte = self.create_test_financial_report()

        # Test forward relationship
        self.assertEqual(reporte.generado_por, self.user_admin)

        # Test reverse relationship
        reportes_usuario = self.user_admin.reportes_financieros_generados.all()
        self.assertIn(reporte, reportes_usuario)

    def test_propiedad_generado_por_info(self):
        """Test generado_por_info property"""
        reporte = self.create_test_financial_report()

        info = reporte.generado_por_info
        self.assertEqual(info['username'], 'admin_test')
        self.assertEqual(info['email'], 'admin@test.com')
        self.assertEqual(info['role'], 'admin')

    def test_str_method(self):
        """Test string representation"""
        reporte = self.create_test_financial_report()
        expected_str = f"Reporte Financiero: Test Financial Report (ingresos - mensual)"
        self.assertEqual(str(reporte), expected_str)


class ReporteSeguridadModelTest(AnalyticsTestBase):

    def test_crear_reporte_seguridad_basico(self):
        """Test basic creation of security report"""
        reporte = self.create_test_security_report()

        self.assertEqual(reporte.titulo, 'Test Security Report')
        self.assertEqual(reporte.tipo, 'incidentes')
        self.assertEqual(reporte.periodo, 'semanal')
        self.assertIsNotNone(reporte.fecha_generacion)

    def test_reporte_seguridad_con_datos(self):
        """Test security report with data"""
        datos = {
            'total_incidentes': 12,
            'incidentes_por_tipo': {'intento_fuerza': 3, 'codigo_incorrecto': 8, 'sospechoso': 1},
            'incidentes_resueltos': 11,
            'tiempo_respuesta_promedio': '5.2 minutos'
        }

        reporte = self.create_test_security_report(
            datos=datos,
            total_eventos=12,
            eventos_criticos=3,
            alertas_generadas=12
        )

        self.assertEqual(reporte.datos['total_incidentes'], 12)
        self.assertEqual(reporte.total_eventos, 12)
        self.assertEqual(reporte.eventos_criticos, 3)

    def test_validaciones_tipo_seguridad(self):
        """Test validations for security report type"""
        valid_types = ['incidentes', 'accesos', 'alertas', 'estadisticas']
        for tipo in valid_types:
            reporte = self.create_test_security_report(tipo=tipo)
            self.assertEqual(reporte.tipo, tipo)


class ReporteUsoAreasModelTest(AnalyticsTestBase):

    def test_crear_reporte_uso_areas_basico(self):
        """Test basic creation of area usage report"""
        reporte = self.create_test_area_usage_report()

        self.assertEqual(reporte.titulo, 'Test Area Usage Report')
        self.assertEqual(reporte.area, 'piscina')
        self.assertEqual(reporte.periodo, 'mensual')
        self.assertEqual(reporte.metrica_principal, 'ocupacion')

    def test_reporte_uso_areas_con_datos(self):
        """Test area usage report with data"""
        datos = {
            'tasa_ocupacion_promedio': 68.5,
            'ocupacion_por_dia': {'lunes': 75.0, 'martes': 70.0},
            'ocupacion_por_hora': {'08:00': 30.0, '12:00': 70.0}
        }

        reporte = self.create_test_area_usage_report(
            datos=datos,
            total_reservas=245,
            horas_ocupacion=1250.5,
            tasa_ocupacion_promedio=68.5
        )

        self.assertEqual(reporte.datos['tasa_ocupacion_promedio'], 68.5)
        self.assertEqual(reporte.total_reservas, 245)


class PrediccionMorosidadModelTest(AnalyticsTestBase):

    def test_crear_prediccion_basica(self):
        """Test basic creation of morosidad prediction"""
        prediccion = self.create_test_prediction()

        self.assertEqual(prediccion.titulo, 'Test Prediction')
        self.assertEqual(prediccion.modelo_usado, 'random_forest')
        self.assertEqual(prediccion.nivel_confianza, 'alto')
        self.assertEqual(prediccion.total_residentes_analizados, 50)

    def test_prediccion_con_resultados(self):
        """Test prediction with results"""
        resultados = {
            'predicciones_por_residente': [
                {'residente_id': 1, 'riesgo_morosidad': 'bajo', 'probabilidad': 0.15},
                {'residente_id': 2, 'riesgo_morosidad': 'medio', 'probabilidad': 0.65}
            ],
            'estadisticas_generales': {
                'riesgo_bajo': 30, 'riesgo_medio': 12, 'riesgo_alto': 8,
                'precision_modelo': 85.2
            }
        }

        prediccion = self.create_test_prediction(
            resultados=resultados,
            metricas_evaluacion={
                'accuracy': 0.852, 'precision': 0.82, 'recall': 0.79, 'f1_score': 0.80
            }
        )

        self.assertEqual(len(prediccion.resultados['predicciones_por_residente']), 2)
        self.assertEqual(prediccion.metricas_evaluacion['accuracy'], 0.852)

    def test_validaciones_modelo_usado(self):
        """Test validations for prediction model"""
        valid_models = ['random_forest', 'xgboost', 'neural_network', 'logistic_regression']
        for modelo in valid_models:
            prediccion = self.create_test_prediction(modelo_usado=modelo)
            self.assertEqual(prediccion.modelo_usado, modelo)

    def test_validaciones_nivel_confianza(self):
        """Test validations for confidence level"""
        valid_levels = ['bajo', 'medio', 'alto']
        for nivel in valid_levels:
            prediccion = self.create_test_prediction(nivel_confianza=nivel)
            self.assertEqual(prediccion.nivel_confianza, nivel)

    def test_propiedad_riesgo_porcentaje(self):
        """Test riesgo_porcentaje property"""
        prediccion = self.create_test_prediction(
            residentes_riesgo_alto=8,
            residentes_riesgo_medio=12,
            total_residentes_analizados=50
        )

        # (8 + 12) / 50 * 100 = 40%
        self.assertEqual(prediccion.riesgo_porcentaje, 40.0)