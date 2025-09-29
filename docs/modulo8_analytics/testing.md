# Guía de Testing - Módulo 8: Reportes y Analítica

## Descripción

Esta guía describe las pruebas automatizadas implementadas para el Módulo de Reportes y Analítica, incluyendo pruebas unitarias, de integración y de rendimiento.

## Estructura de Tests

```
backend/apps/analytics/tests/
├── __init__.py
├── test_models.py              # Pruebas de modelos
├── test_serializers.py         # Pruebas de serializadores
├── test_views.py              # Pruebas de vistas/endpoints
├── test_permissions.py        # Pruebas de permisos
├── test_rate_limiting.py      # Pruebas de rate limiting
├── test_reports.py            # Pruebas de lógica de reportes
├── test_predictions.py        # Pruebas de predicciones IA
├── test_integration.py        # Pruebas de integración
├── test_performance.py        # Pruebas de rendimiento
├── fixtures/                  # Datos de prueba
│   ├── users.json
│   ├── financial_data.json
│   ├── security_events.json
│   ├── reservations.json
│   └── predictions.json
└── utils/                     # Utilidades de testing
    ├── test_helpers.py
    └── mock_data.py
```

## Configuración de Tests

### Settings de Test
```python
# backend/settings/test.py
TESTING = True
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Deshabilitar rate limiting en tests
RATELIMIT_ENABLE = False

# Configuración de logging para tests
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'analytics': {
            'handlers': ['console'],
            'level': 'DEBUG',
        },
    },
}
```

### Base de Clase de Test
```python
# test_base.py
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from rest_framework import status
from analytics.models import *

class AnalyticsTestBase(APITestCase):
    """Base class for analytics tests"""

    def setUp(self):
        self.user_admin = get_user_model().objects.create_user(
            username='admin', email='admin@test.com',
            password='password', role='admin'
        )
        self.user_staff = get_user_model().objects.create_user(
            username='staff', email='staff@test.com',
            password='password', role='staff'
        )
        self.user_resident = get_user_model().objects.create_user(
            username='resident', email='resident@test.com',
            password='password', role='resident'
        )

    def authenticate_as_admin(self):
        self.client.force_authenticate(user=self.user_admin)

    def authenticate_as_staff(self):
        self.client.force_authenticate(user=self.user_staff)

    def authenticate_as_resident(self):
        self.client.force_authenticate(user=self.user_resident)
```

## Pruebas de Modelos

### Test de Modelos Financieros
```python
# test_models.py
class ReporteFinancieroModelTest(AnalyticsTestBase):

    def test_crear_reporte_financiero(self):
        """Test creación de reporte financiero"""
        reporte = ReporteFinanciero.objects.create(
            titulo="Test Report",
            tipo="ingresos",
            periodo="mensual",
            formato="pdf",
            fecha_inicio="2024-01-01",
            fecha_fin="2024-01-31",
            generado_por=self.user_admin
        )

        self.assertEqual(reporte.titulo, "Test Report")
        self.assertEqual(reporte.tipo, "ingresos")
        self.assertIsNotNone(reporte.fecha_generacion)

    def test_validaciones_reporte_financiero(self):
        """Test validaciones de modelo"""
        with self.assertRaises(ValidationError):
            ReporteFinanciero.objects.create(
                titulo="",
                tipo="invalid_type",  # Tipo inválido
                periodo="mensual",
                formato="pdf",
                fecha_inicio="2024-01-31",  # Fecha fin antes de inicio
                fecha_fin="2024-01-01",
                generado_por=self.user_admin
            )

    def test_relaciones_reporte_financiero(self):
        """Test relaciones del modelo"""
        reporte = ReporteFinanciero.objects.create(
            titulo="Test Report",
            tipo="ingresos",
            periodo="mensual",
            formato="pdf",
            fecha_inicio="2024-01-01",
            fecha_fin="2024-01-31",
            generado_por=self.user_admin
        )

        # Verificar relación con usuario
        self.assertEqual(reporte.generado_por, self.user_admin)
        self.assertEqual(reporte.generado_por_info['username'], 'admin')
```

## Pruebas de Serializers

### Test de Serializers
```python
# test_serializers.py
class ReporteFinancieroSerializerTest(AnalyticsTestBase):

    def test_serializer_create(self):
        """Test serialización de creación"""
        data = {
            "titulo": "Test Report",
            "tipo": "ingresos",
            "periodo": "mensual",
            "formato": "pdf",
            "fecha_inicio": "2024-01-01",
            "fecha_fin": "2024-01-31"
        }

        serializer = ReporteFinancieroCreateSerializer(
            data=data,
            context={'request': self.get_request_with_user(self.user_admin)}
        )

        self.assertTrue(serializer.is_valid())
        reporte = serializer.save()
        self.assertEqual(reporte.titulo, "Test Report")

    def test_serializer_read(self):
        """Test serialización de lectura"""
        reporte = ReporteFinanciero.objects.create(
            titulo="Test Report",
            tipo="ingresos",
            periodo="mensual",
            formato="pdf",
            fecha_inicio="2024-01-01",
            fecha_fin="2024-01-31",
            generado_por=self.user_admin
        )

        serializer = ReporteFinancieroReadSerializer(reporte)
        data = serializer.data

        self.assertIn('generado_por_info', data)
        self.assertEqual(data['generado_por_info']['username'], 'admin')

    def test_serializer_validation(self):
        """Test validaciones del serializer"""
        data = {
            "titulo": "",  # Título vacío
            "tipo": "invalid_type",  # Tipo inválido
            "periodo": "mensual",
            "formato": "pdf",
            "fecha_inicio": "2024-01-31",
            "fecha_fin": "2024-01-01"  # Fecha inválida
        }

        serializer = ReporteFinancieroCreateSerializer(data=data)
        self.assertFalse(serializer.is_valid())
        self.assertIn('titulo', serializer.errors)
        self.assertIn('tipo', serializer.errors)
        self.assertIn('fecha_fin', serializer.errors)
```

## Pruebas de Vistas/Endpoints

### Test de Endpoints Financieros
```python
# test_views.py
class ReporteFinancieroAPITest(AnalyticsTestBase):

    def test_list_reportes_admin(self):
        """Test listar reportes como admin"""
        self.authenticate_as_admin()

        # Crear algunos reportes
        ReporteFinanciero.objects.create(
            titulo="Report 1", tipo="ingresos", periodo="mensual",
            formato="pdf", fecha_inicio="2024-01-01", fecha_fin="2024-01-31",
            generado_por=self.user_admin
        )

        response = self.client.get('/api/analytics/reportes-financieros/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_list_reportes_staff_limitado(self):
        """Test listar reportes como staff con limitaciones"""
        self.authenticate_as_staff()

        # Crear reporte antiguo
        old_date = timezone.now() - timedelta(days=200)
        ReporteFinanciero.objects.create(
            titulo="Old Report", tipo="balance", periodo="mensual",
            formato="pdf", fecha_inicio="2024-01-01", fecha_fin="2024-01-31",
            generado_por=self.user_admin, fecha_generacion=old_date
        )

        response = self.client.get('/api/analytics/reportes-financieros/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Staff no debería ver reportes antiguos o balances
        self.assertEqual(len(response.data), 0)

    def test_create_reporte_financiero(self):
        """Test crear reporte financiero"""
        self.authenticate_as_admin()

        data = {
            "titulo": "Nuevo Report",
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
        self.assertEqual(response.data['titulo'], "Nuevo Report")

    def test_generar_reporte_financiero(self):
        """Test generar reporte financiero con datos"""
        self.authenticate_as_admin()

        data = {
            "titulo": "Reporte Generado",
            "tipo": "ingresos",
            "periodo": "mensual",
            "formato": "json",
            "fecha_inicio": "2024-01-01",
            "fecha_fin": "2024-01-31"
        }

        response = self.client.post(
            '/api/analytics/reportes-financieros/generar_reporte/',
            data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('datos', response.data)
        self.assertIn('total_registros', response.data)

    def test_permissions_residente(self):
        """Test que residente no puede crear reportes"""
        self.authenticate_as_resident()

        data = {
            "titulo": "Reporte Residente",
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
```

## Pruebas de Permisos

### Test de Permisos
```python
# test_permissions.py
class AnalyticsPermissionsTest(AnalyticsTestBase):

    def test_admin_full_access(self):
        """Test que admin tiene acceso completo"""
        self.authenticate_as_admin()

        # Crear reporte
        response = self.client.post(
            '/api/analytics/reportes-financieros/',
            {
                "titulo": "Admin Report",
                "tipo": "balance",
                "periodo": "mensual",
                "formato": "pdf",
                "fecha_inicio": "2024-01-01",
                "fecha_fin": "2024-01-31"
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_staff_limited_access(self):
        """Test que staff tiene acceso limitado"""
        self.authenticate_as_staff()

        # Intentar crear balance (no permitido)
        response = self.client.post(
            '/api/analytics/reportes-financieros/',
            {
                "titulo": "Staff Balance Report",
                "tipo": "balance",  # No permitido para staff
                "periodo": "mensual",
                "formato": "pdf",
                "fecha_inicio": "2024-01-01",
                "fecha_fin": "2024-01-31"
            },
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_resident_no_access(self):
        """Test que residente no tiene acceso"""
        self.authenticate_as_resident()

        # Intentar cualquier operación
        response = self.client.get('/api/analytics/reportes-financieros/')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

        response = self.client.post('/api/analytics/reportes-financieros/', {})
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
```

## Pruebas de Lógica de Reportes

### Test de Generación de Reportes
```python
# test_reports.py
class ReportGenerationTest(AnalyticsTestBase):

    def setUp(self):
        super().setUp()
        # Crear datos de prueba
        self.create_test_financial_data()

    def create_test_financial_data(self):
        """Crear datos financieros de prueba"""
        # Crear pagos de prueba
        from condominio.models import Pago, CuotaMantenimiento

        cuota = CuotaMantenimiento.objects.create(
            residente=self.user_resident,
            monto=100.00,
            mes="2024-01",
            estado="pagado",
            fecha_pago="2024-01-15"
        )

        Pago.objects.create(
            cuota=cuota,
            monto_pagado=100.00,
            fecha_pago="2024-01-15",
            metodo_pago="transferencia"
        )

    def test_generar_reporte_ingresos(self):
        """Test generación de reporte de ingresos"""
        self.authenticate_as_admin()

        data = {
            "titulo": "Ingresos Enero 2024",
            "tipo": "ingresos",
            "periodo": "mensual",
            "formato": "json",
            "fecha_inicio": "2024-01-01",
            "fecha_fin": "2024-01-31"
        }

        response = self.client.post(
            '/api/analytics/reportes-financieros/generar_reporte/',
            data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        reporte_data = response.data['datos']
        self.assertIn('total_ingresos', reporte_data)
        self.assertIn('ingresos_por_mes', reporte_data)
        self.assertGreaterEqual(reporte_data['total_ingresos'], 0)

    def test_filtros_reporte_financiero(self):
        """Test aplicación de filtros en reportes"""
        self.authenticate_as_admin()

        data = {
            "titulo": "Ingresos Filtrados",
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
        self.assertIn('filtros_aplicados', response.data)
```

## Pruebas de Predicciones IA

### Test de Predicciones
```python
# test_predictions.py
from unittest.mock import patch, MagicMock

class PredictionTest(AnalyticsTestBase):

    def setUp(self):
        super().setUp()
        self.create_test_prediction_data()

    def create_test_prediction_data(self):
        """Crear datos históricos para predicciones"""
        # Crear historial de pagos de prueba
        from condominio.models import Pago, CuotaMantenimiento

        for i in range(12):  # 12 meses de historial
            fecha = timezone.now() - timedelta(days=30*i)
            cuota = CuotaMantenimiento.objects.create(
                residente=self.user_resident,
                monto=100.00,
                mes=fecha.strftime("%Y-%m"),
                estado="pagado" if i < 10 else "pendiente",
                fecha_pago=fecha if i < 10 else None
            )

            if i < 10:
                Pago.objects.create(
                    cuota=cuota,
                    monto_pagado=100.00,
                    fecha_pago=fecha,
                    metodo_pago="transferencia"
                )

    @patch('analytics.views.RandomForestClassifier')
    def test_generar_prediccion_morosidad(self, mock_rf):
        """Test generación de predicción de morosidad"""
        self.authenticate_as_admin()

        # Mock del modelo de IA
        mock_model = MagicMock()
        mock_model.predict_proba.return_value = [[0.2, 0.8]]  # 80% riesgo
        mock_model.predict.return_value = [1]  # Riesgo alto
        mock_rf.return_value = mock_model

        data = {
            "titulo": "Predicción Test",
            "modelo_usado": "random_forest",
            "periodo_predicho": "Próximos 3 meses",
            "parametros_modelo": {
                "n_estimators": 10,
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

    def test_prediccion_sin_permisos(self):
        """Test que staff no puede generar predicciones"""
        self.authenticate_as_staff()

        data = {
            "titulo": "Predicción Staff",
            "modelo_usado": "random_forest"
        }

        response = self.client.post(
            '/api/analytics/predicciones-morosidad/generar_prediccion/',
            data,
            format='json'
        )

        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
```

## Pruebas de Integración

### Test de Flujo Completo
```python
# test_integration.py
class AnalyticsIntegrationTest(AnalyticsTestBase):

    def setUp(self):
        super().setUp()
        self.create_complete_test_data()

    def create_complete_test_data(self):
        """Crear conjunto completo de datos de prueba"""
        # Crear usuarios, pagos, reservas, eventos de seguridad, etc.
        pass

    def test_flujo_completo_admin(self):
        """Test flujo completo como administrador"""
        self.authenticate_as_admin()

        # 1. Generar reporte financiero
        financial_data = {
            "titulo": "Reporte Completo",
            "tipo": "balance",
            "periodo": "mensual",
            "formato": "json",
            "fecha_inicio": "2024-01-01",
            "fecha_fin": "2024-01-31"
        }

        response = self.client.post(
            '/api/analytics/reportes-financieros/generar_reporte/',
            financial_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        financial_report_id = response.data['id']

        # 2. Generar reporte de seguridad
        security_data = {
            "titulo": "Seguridad Enero",
            "tipo": "incidentes",
            "periodo": "mensual",
            "fecha_inicio": "2024-01-01",
            "fecha_fin": "2024-01-31"
        }

        response = self.client.post(
            '/api/analytics/reportes-seguridad/generar_reporte/',
            security_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 3. Generar predicción
        prediction_data = {
            "titulo": "Predicción IA",
            "modelo_usado": "random_forest"
        }

        response = self.client.post(
            '/api/analytics/predicciones-morosidad/generar_prediccion/',
            prediction_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 4. Listar todos los reportes
        response = self.client.get('/api/analytics/reportes-financieros/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
```

## Pruebas de Rendimiento

### Test de Performance
```python
# test_performance.py
from django.test.utils import override_settings
import time

class AnalyticsPerformanceTest(AnalyticsTestBase):

    def setUp(self):
        super().setUp()
        self.create_large_dataset()

    def create_large_dataset(self):
        """Crear conjunto grande de datos para pruebas de rendimiento"""
        # Crear 1000 registros de prueba
        for i in range(1000):
            ReporteFinanciero.objects.create(
                titulo=f"Report {i}",
                tipo="ingresos",
                periodo="mensual",
                formato="pdf",
                fecha_inicio="2024-01-01",
                fecha_fin="2024-01-31",
                generado_por=self.user_admin
            )

    def test_list_performance(self):
        """Test rendimiento de listados"""
        self.authenticate_as_admin()

        start_time = time.time()
        response = self.client.get('/api/analytics/reportes-financieros/')
        end_time = time.time()

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertLess(end_time - start_time, 2.0)  # Menos de 2 segundos

    @override_settings(DEBUG=False)  # Deshabilitar queries en log
    def test_bulk_operations_performance(self):
        """Test rendimiento de operaciones masivas"""
        self.authenticate_as_admin()

        # Crear múltiples reportes en bulk
        start_time = time.time()

        for i in range(100):
            data = {
                "titulo": f"Bulk Report {i}",
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

        end_time = time.time()
        total_time = end_time - start_time

        # Verificar que el tiempo total es razonable (menos de 30 segundos para 100 operaciones)
        self.assertLess(total_time, 30.0)
```

## Ejecución de Tests

### Comandos de Ejecución

```bash
# Ejecutar todos los tests del módulo analytics
python manage.py test analytics --verbosity=2

# Ejecutar tests específicos
python manage.py test analytics.tests.test_models --verbosity=2
python manage.py test analytics.tests.test_views --verbosity=2
python manage.py test analytics.tests.test_permissions --verbosity=2

# Ejecutar con coverage
coverage run --source=analytics manage.py test analytics
coverage report -m

# Ejecutar tests de performance
python manage.py test analytics.tests.test_performance --verbosity=2

# Ejecutar tests de integración
python manage.py test analytics.tests.test_integration --verbosity=2
```

### Configuración de CI/CD

```yaml
# .github/workflows/test-analytics.yml
name: Test Analytics Module

on:
  push:
    paths:
      - 'backend/apps/analytics/**'
  pull_request:
    paths:
      - 'backend/apps/analytics/**'

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v2
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.12'

    - name: Install dependencies
      run: |
        pip install -r requirements.txt
        pip install coverage

    - name: Run tests
      run: |
        python manage.py test analytics --verbosity=2 --keepdb

    - name: Generate coverage report
      run: |
        coverage run --source=analytics manage.py test analytics
        coverage xml

    - name: Upload coverage to Codecov
      uses: codecov/codecov-action@v1
      with:
        file: ./coverage.xml
```

## Cobertura de Tests

### Métricas Objetivo

- **Cobertura de Código**: > 90%
- **Cobertura de Ramas**: > 85%
- **Tiempo de Ejecución**: < 5 minutos
- **Tests por Endpoint**: Mínimo 3 (happy path, error cases, edge cases)

### Reporte de Cobertura

```bash
# Generar reporte HTML de cobertura
coverage run --source=analytics manage.py test analytics
coverage html

# Ver reporte en navegador
# Abrir htmlcov/index.html
```

## Mocks y Fixtures

### Fixtures de Datos

#### users.json
```json
[
  {
    "model": "auth.user",
    "pk": 1,
    "fields": {
      "username": "admin",
      "email": "admin@test.com",
      "role": "admin",
      "is_active": true
    }
  }
]
```

#### financial_data.json
```json
[
  {
    "model": "analytics.reportefinanciero",
    "pk": 1,
    "fields": {
      "titulo": "Test Report",
      "tipo": "ingresos",
      "periodo": "mensual",
      "formato": "json",
      "fecha_inicio": "2024-01-01",
      "fecha_fin": "2024-01-31",
      "generado_por": 1,
      "fecha_generacion": "2024-01-15T10:00:00Z"
    }
  }
]
```

## Debugging de Tests

### Comandos Útiles

```bash
# Ejecutar test específico con debug
python manage.py test analytics.tests.test_views.ReporteFinancieroAPITest.test_create_reporte_financiero --verbosity=2 --debug-mode

# Ver queries ejecutadas
python manage.py test analytics.tests.test_models --verbosity=2 --keepdb --debug-sql

# Ejecutar tests en paralelo
python manage.py test analytics --parallel 4

# Generar reporte JUnit para CI
python manage.py test analytics --junitxml=test-results.xml
```

### Troubleshooting

#### Tests que Fallan Intermitentemente
- Verificar uso de `setUp` vs `setUpTestData`
- Asegurar limpieza de datos entre tests
- Usar transacciones para aislamiento

#### Tests Lentos
- Optimizar creación de datos de prueba
- Usar `bulk_create` para múltiples objetos
- Implementar fixtures para datos estáticos

#### Errores de Permisos
- Verificar autenticación en `setUp`
- Comprobar configuración de roles
- Validar URLs de endpoints

## Mejores Prácticas

### Estructura de Tests
1. **Un test por funcionalidad**: Cada test debe verificar una cosa específica
2. **Nombres descriptivos**: `test_crear_reporte_con_datos_invalidos`
3. **Arrange-Act-Assert**: Preparar datos, ejecutar acción, verificar resultado
4. **Independencia**: Tests no deben depender unos de otros

### Mocks y Stubs
- **Usar mocks** para dependencias externas (APIs, modelos IA)
- **Evitar mocks excesivos** que oculten bugs reales
- **Verificar llamadas** a mocks cuando sea relevante

### Fixtures y Factories
- **Usar factories** para datos complejos (Factory Boy)
- **Crear fixtures** para datos estáticos
- **Reutilizar datos** entre tests cuando sea posible

### Performance
- **Ejecutar tests en paralelo** cuando sea posible
- **Optimizar setUp** para evitar recrear datos innecesariamente
- **Usar --keepdb** para desarrollo local