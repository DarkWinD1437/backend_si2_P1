"""
Tests de carga y rendimiento para el módulo de Analytics
Tests que simulan carga alta en los endpoints
"""

import time
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.test import TestCase
from django.test.utils import override_settings
from rest_framework.test import APIClient
from rest_framework import status

from backend.apps.analytics.models import (
    ReporteFinanciero,
    ReporteSeguridad,
    ReporteUsoAreas,
    PrediccionMorosidad
)
from django.contrib.auth import get_user_model

User = get_user_model()


class AnalyticsLoadTestCase(TestCase):
    """Tests de carga para el módulo de Analytics"""

    def setUp(self):
        """Configurar datos de prueba para tests de carga"""
        # Crear usuario admin para tests
        self.admin_user = User.objects.create_user(
            username='loadtest_admin',
            email='loadtest@admin.com',
            password='loadtest123',
            role='admin'
        )

        # Crear datos base para tests
        self.base_financial_data = {
            'titulo': 'Load Test Financial Report',
            'descripcion': 'Test de carga para reportes financieros',
            'tipo': 'ingresos',
            'periodo': 'mensual',
            'formato': 'json',
            'fecha_inicio': '2024-01-01',
            'fecha_fin': '2024-01-31'
        }

        self.base_security_data = {
            'titulo': 'Load Test Security Report',
            'descripcion': 'Test de carga para reportes de seguridad',
            'tipo': 'accesos',
            'periodo': 'diario',
            'fecha_inicio': '2024-01-01',
            'fecha_fin': '2024-01-31'
        }

        self.base_area_data = {
            'titulo': 'Load Test Area Report',
            'descripcion': 'Test de carga para reportes de áreas',
            'area': 'gimnasio',
            'periodo': 'semanal',
            'metrica_principal': 'ocupacion',
            'fecha_inicio': '2024-01-01',
            'fecha_fin': '2024-01-31'
        }

        self.base_prediction_data = {
            'titulo': 'Load Test Prediction',
            'descripcion': 'Test de carga para predicciones',
            'modelo_usado': 'random_forest',
            'periodo_predicho': '3_meses'
        }

    def _create_client_with_auth(self):
        """Crear cliente API con autenticación"""
        client = APIClient()
        client.force_authenticate(user=self.admin_user)
        return client

    def test_concurrent_financial_reports_creation(self):
        """Test creación concurrente de reportes financieros"""
        num_requests = 20
        results = []
        errors = []

        def create_financial_report(request_id):
            try:
                client = self._create_client_with_auth()
                data = self.base_financial_data.copy()
                data['titulo'] = f'{data["titulo"]} #{request_id}'

                start_time = time.time()
                response = client.post('/api/analytics/reportes-financieros/', data, format='json')
                end_time = time.time()

                results.append({
                    'request_id': request_id,
                    'status_code': response.status_code,
                    'response_time': end_time - start_time,
                    'success': response.status_code == status.HTTP_201_CREATED
                })

            except Exception as e:
                errors.append({
                    'request_id': request_id,
                    'error': str(e)
                })

        # Ejecutar requests concurrentemente
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(create_financial_report, i) for i in range(num_requests)]
            for future in as_completed(futures):
                future.result()

        # Analizar resultados
        successful_requests = [r for r in results if r['success']]
        failed_requests = [r for r in results if not r['success']]

        # Calcular métricas
        if successful_requests:
            avg_response_time = sum(r['response_time'] for r in successful_requests) / len(successful_requests)
            max_response_time = max(r['response_time'] for r in successful_requests)
            min_response_time = min(r['response_time'] for r in successful_requests)

            print(f"""
            Load Test Results - Financial Reports:
            Total Requests: {num_requests}
            Successful: {len(successful_requests)}
            Failed: {len(failed_requests)}
            Success Rate: {len(successful_requests)/num_requests*100:.2f}%
            Average Response Time: {avg_response_time:.3f}s
            Max Response Time: {max_response_time:.3f}s
            Min Response Time: {min_response_time:.3f}s
            """)

        # Verificar que al menos el 95% de las requests fueron exitosas
        success_rate = len(successful_requests) / num_requests
        self.assertGreaterEqual(success_rate, 0.95, f"Success rate too low: {success_rate*100:.2f}%")

        # Verificar que no hay errores
        self.assertEqual(len(errors), 0, f"Errors occurred: {errors}")

    def test_concurrent_security_reports_creation(self):
        """Test creación concurrente de reportes de seguridad"""
        num_requests = 15
        results = []

        def create_security_report(request_id):
            client = self._create_client_with_auth()
            data = self.base_security_data.copy()
            data['titulo'] = f'{data["titulo"]} #{request_id}'

            start_time = time.time()
            response = client.post('/api/analytics/reportes-seguridad/', data, format='json')
            end_time = time.time()

            results.append({
                'request_id': request_id,
                'status_code': response.status_code,
                'response_time': end_time - start_time,
                'success': response.status_code == status.HTTP_201_CREATED
            })

        # Ejecutar requests concurrentemente
        threads = []
        for i in range(num_requests):
            thread = threading.Thread(target=create_security_report, args=(i,))
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        successful_requests = [r for r in results if r['success']]
        success_rate = len(successful_requests) / num_requests

        self.assertGreaterEqual(success_rate, 0.95)

    def test_mixed_load_test(self):
        """Test de carga mixta con diferentes tipos de operaciones"""
        results = {'create': [], 'read': [], 'update': [], 'delete': []}

        # Crear algunos reportes base para operaciones de lectura/actualización/eliminación
        client = self._create_client_with_auth()

        # Crear reportes base
        base_reports = []
        for i in range(5):
            data = self.base_financial_data.copy()
            data['titulo'] = f'Base Report {i}'
            response = client.post('/api/analytics/reportes-financieros/', data, format='json')
            if response.status_code == status.HTTP_201_CREATED:
                base_reports.append(response.data['id'])

        def perform_operations(operation_type, request_id):
            client = self._create_client_with_auth()
            start_time = time.time()

            try:
                if operation_type == 'create':
                    data = self.base_financial_data.copy()
                    data['titulo'] = f'Mixed Load Create {request_id}'
                    response = client.post('/api/analytics/reportes-financieros/', data, format='json')
                    success = response.status_code == status.HTTP_201_CREATED

                elif operation_type == 'read' and base_reports:
                    report_id = base_reports[request_id % len(base_reports)]
                    response = client.get(f'/api/analytics/reportes-financieros/{report_id}/')
                    success = response.status_code == status.HTTP_200_OK

                elif operation_type == 'update' and base_reports:
                    report_id = base_reports[request_id % len(base_reports)]
                    data = {'titulo': f'Updated Mixed Load {request_id}'}
                    response = client.patch(f'/api/analytics/reportes-financieros/{report_id}/', data, format='json')
                    success = response.status_code == status.HTTP_200_OK

                elif operation_type == 'delete' and base_reports:
                    report_id = base_reports[request_id % len(base_reports)]
                    response = client.delete(f'/api/analytics/reportes-financieros/{report_id}/')
                    success = response.status_code == status.HTTP_204_NO_CONTENT

                else:
                    success = False
                    response = None

                end_time = time.time()

                results[operation_type].append({
                    'request_id': request_id,
                    'response_time': end_time - start_time,
                    'success': success,
                    'status_code': response.status_code if response else None
                })

            except Exception as e:
                results[operation_type].append({
                    'request_id': request_id,
                    'error': str(e),
                    'success': False
                })

        # Ejecutar operaciones mixtas
        operations = ['create', 'read', 'update', 'delete']
        num_operations_per_type = 10

        threads = []
        for op_type in operations:
            for i in range(num_operations_per_type):
                thread = threading.Thread(target=perform_operations, args=(op_type, i))
                threads.append(thread)
                thread.start()

        for thread in threads:
            thread.join()

        # Analizar resultados por tipo de operación
        for op_type in operations:
            op_results = results[op_type]
            if op_results:
                successful = [r for r in op_results if r.get('success', False)]
                success_rate = len(successful) / len(op_results)

                if successful:
                    avg_time = sum(r['response_time'] for r in successful) / len(successful)
                    print(f"{op_type.upper()}: {len(successful)}/{len(op_results)} successful ({success_rate*100:.1f}%), avg time: {avg_time:.3f}s")

                self.assertGreaterEqual(success_rate, 0.90, f"Low success rate for {op_type}: {success_rate*100:.1f}%")

    def test_memory_usage_under_load(self):
        """Test de uso de memoria bajo carga"""
        import psutil
        import os

        # Obtener uso de memoria inicial
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Realizar operaciones intensivas
        client = self._create_client_with_auth()

        for i in range(50):
            data = self.base_financial_data.copy()
            data['titulo'] = f'Memory Test Report {i}'
            response = client.post('/api/analytics/reportes-financieros/', data, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Verificar uso de memoria final
        final_memory = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = final_memory - initial_memory

        print(f"Memory usage: Initial: {initial_memory:.2f}MB, Final: {final_memory:.2f}MB, Increase: {memory_increase:.2f}MB")

        # El aumento de memoria no debería ser excesivo (menos de 50MB para 50 operaciones)
        self.assertLess(memory_increase, 50.0, f"Excessive memory increase: {memory_increase:.2f}MB")

    def test_database_connection_pooling(self):
        """Test de pool de conexiones a base de datos bajo carga"""
        from django.db import connection

        initial_connections = len(connection.queries)

        # Realizar múltiples operaciones de base de datos
        client = self._create_client_with_auth()

        for i in range(25):
            # Crear reporte
            data = self.base_financial_data.copy()
            data['titulo'] = f'Connection Pool Test {i}'
            response = client.post('/api/analytics/reportes-financieros/', data, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

            # Leer reporte
            if response.data.get('id'):
                client.get(f'/api/analytics/reportes-financieros/{response.data["id"]}/')

        final_connections = len(connection.queries)
        total_queries = final_connections - initial_connections

        print(f"Database queries executed: {total_queries}")

        # Verificar que no hay un número excesivo de queries
        # Para 25 operaciones CRUD, esperamos alrededor de 50-75 queries máximo
        self.assertLess(total_queries, 100, f"Too many database queries: {total_queries}")

    @override_settings(DEBUG=True)
    def test_sql_query_analysis_under_load(self):
        """Test análisis de queries SQL bajo carga"""
        from django.test.utils import override_settings
        from django.db import connection, reset_queries

        # Limpiar queries previas
        reset_queries()

        client = self._create_client_with_auth()

        # Realizar operaciones
        for i in range(10):
            data = self.base_financial_data.copy()
            data['titulo'] = f'SQL Analysis Test {i}'
            response = client.post('/api/analytics/reportes-financieros/', data, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # Analizar queries ejecutadas
        queries = connection.queries
        select_queries = [q for q in queries if q['sql'].strip().upper().startswith('SELECT')]
        insert_queries = [q for q in queries if q['sql'].strip().upper().startswith('INSERT')]

        print(f"SQL Analysis: {len(select_queries)} SELECT, {len(insert_queries)} INSERT")

        # Verificar que hay un balance razonable entre SELECT e INSERT
        # Para operaciones de creación, esperamos más INSERT que SELECT
        self.assertGreater(len(insert_queries), len(select_queries) * 0.5)

    def test_api_response_format_consistency(self):
        """Test consistencia en el formato de respuestas de la API"""
        client = self._create_client_with_auth()

        # Crear múltiples reportes y verificar formato consistente
        responses = []
        for i in range(5):
            data = self.base_financial_data.copy()
            data['titulo'] = f'Format Consistency Test {i}'
            response = client.post('/api/analytics/reportes-financieros/', data, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
            responses.append(response.data)

        # Verificar que todos los responses tienen los mismos campos requeridos
        required_fields = ['id', 'titulo', 'tipo', 'periodo', 'formato', 'fecha_generacion', 'generado_por']

        for response in responses:
            for field in required_fields:
                self.assertIn(field, response, f"Missing field '{field}' in response")

        # Verificar que los tipos de datos son consistentes
        for response in responses:
            self.assertIsInstance(response['id'], int)
            self.assertIsInstance(response['titulo'], str)
            self.assertIsInstance(response['tipo'], str)
            self.assertIsInstance(response['generado_por'], dict)

    def test_error_handling_under_load(self):
        """Test manejo de errores bajo carga"""
        client = self._create_client_with_auth()

        # Intentar crear reportes con datos inválidos bajo carga
        invalid_data_list = [
            {'titulo': '', 'tipo': 'invalid'},  # Datos vacíos/inválidos
            {'titulo': 'Test', 'tipo': 'ingresos'},  # Faltan campos requeridos
            {'titulo': 'Test', 'tipo': 'ingresos', 'periodo': 'mensual'},  # Más campos faltantes
        ] * 10  # Repetir para simular carga

        error_responses = 0
        success_responses = 0

        for invalid_data in invalid_data_list:
            response = client.post('/api/analytics/reportes-financieros/', invalid_data, format='json')
            if response.status_code >= 400:
                error_responses += 1
            elif response.status_code < 300:
                success_responses += 1

        # Deberíamos tener principalmente respuestas de error
        self.assertGreater(error_responses, success_responses,
                          "Too many successful responses with invalid data")

        print(f"Error handling: {error_responses} errors, {success_responses} unexpected successes")

    def test_rate_limiting_simulation(self):
        """Test simulación de rate limiting"""
        # Este test simula comportamiento bajo rate limiting
        # En una implementación real, se usaría middleware de rate limiting

        client = self._create_client_with_auth()

        # Simular muchas requests rápidas
        start_time = time.time()
        request_count = 0

        while time.time() - start_time < 1.0:  # En 1 segundo
            data = self.base_financial_data.copy()
            data['titulo'] = f'Rate Limit Test {request_count}'
            response = client.post('/api/analytics/reportes-financieros/', data, format='json')

            if response.status_code == status.HTTP_201_CREATED:
                request_count += 1
            else:
                break  # Si hay error, detener

        elapsed_time = time.time() - start_time
        requests_per_second = request_count / elapsed_time

        print(f"Rate limiting simulation: {request_count} requests in {elapsed_time:.2f}s ({requests_per_second:.2f} req/s)")

        # En condiciones normales, deberíamos poder hacer varias requests por segundo
        self.assertGreater(requests_per_second, 5.0, f"Low throughput: {requests_per_second:.2f} req/s")