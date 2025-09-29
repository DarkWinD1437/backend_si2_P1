import json
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from rest_framework.test import APITestCase
from rest_framework import status
from backend.apps.modulo_ia.models import RostroRegistrado, VehiculoRegistrado, Acceso

User = get_user_model()

class ModelosSeguridadTestCase(TestCase):
    """Tests para los modelos del módulo de seguridad"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )

    def test_crear_rostro_registrado(self):
        """Test creación de rostro registrado"""
        rostro = RostroRegistrado.objects.create(
            usuario=self.user,
            nombre_identificador='Rostro principal',
            embedding_ia={'vector': [0.1] * 512},
            confianza_minima=0.85
        )

        self.assertEqual(rostro.usuario, self.user)
        self.assertEqual(rostro.nombre_identificador, 'Rostro principal')
        self.assertTrue(rostro.activo)
        self.assertEqual(str(rostro), f"Rostro de {self.user.get_full_name()} - Rostro principal")

    def test_crear_vehiculo_registrado_placa_valida(self):
        """Test creación de vehículo con placa válida boliviana"""
        vehiculo = VehiculoRegistrado.objects.create(
            usuario=self.user,
            placa='1234ABC',
            marca='Toyota',
            modelo='Corolla',
            color='Blanco'
        )

        self.assertEqual(vehiculo.placa, '1234ABC')
        self.assertEqual(vehiculo.marca, 'Toyota')
        self.assertTrue(vehiculo.activo)

    def test_placa_invalida_levanta_error(self):
        """Test que placa con formato inválido levante ValidationError"""
        from django.core.exceptions import ValidationError
        vehiculo = VehiculoRegistrado(
            usuario=self.user,
            placa='ABC-123',  # Formato antiguo inválido
            marca='Toyota',
            modelo='Corolla'
        )
        with self.assertRaises(ValidationError):
            vehiculo.full_clean()  # Esto ejecuta las validaciones del modelo

    def test_placas_validas_bolivianas(self):
        """Test placas válidas en formato boliviano"""
        placas_validas = ['123ABC', '1234ABC', '999ZZZ', '001AAA']

        for placa in placas_validas:
            with self.subTest(placa=placa):
                vehiculo = VehiculoRegistrado.objects.create(
                    usuario=self.user,
                    placa=placa,
                    marca='Test',
                    modelo='Test'
                )
                self.assertEqual(vehiculo.placa, placa)

    def test_crear_acceso(self):
        """Test creación de registro de acceso"""
        acceso = Acceso.objects.create(
            usuario=self.user,
            tipo_acceso='manual',
            estado='permitido',
            ubicacion='Puerta Principal',
            observaciones='Acceso manual autorizado'
        )

        self.assertEqual(acceso.usuario, self.user)
        self.assertEqual(acceso.tipo_acceso, 'manual')
        self.assertEqual(acceso.estado, 'permitido')
        self.assertEqual(acceso.ubicacion, 'Puerta Principal')


class APISeguridadTestCase(APITestCase):
    """Tests para la API del módulo de seguridad"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )

        # Crear token JWT de autenticación
        from rest_framework_simplejwt.tokens import RefreshToken
        refresh = RefreshToken.for_user(self.user)
        self.token = str(refresh.access_token)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.token}')

    def test_listar_rostros_autenticado(self):
        """Test listar rostros con autenticación"""
        response = self.client.get('/api/security/rostros/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_listar_rostros_sin_autenticacion(self):
        """Test que requiere autenticación"""
        self.client.credentials()  # Remover credenciales
        response = self.client.get('/api/security/rostros/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_registrar_vehiculo_placa_valida(self):
        """Test registrar vehículo con placa boliviana válida"""
        data = {
            'placa': '5678XYZ',
            'marca': 'Honda',
            'modelo': 'Civic',
            'color': 'Negro'
        }

        response = self.client.post('/api/security/vehiculos/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['placa'], '5678XYZ')

    def test_registrar_vehiculo_placa_invalida(self):
        """Test registrar vehículo con placa inválida"""
        data = {
            'placa': 'INVALID',
            'marca': 'Honda',
            'modelo': 'Civic',
            'color': 'Negro'
        }

        response = self.client.post('/api/security/vehiculos/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_reconocimiento_facial_sin_rostros_registrados(self):
        """Test reconocimiento facial cuando no hay rostros registrados"""
        data = {
            'imagen_base64': 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ',
            'ubicacion': 'Puerta Principal'
        }

        response = self.client.post('/api/security/reconocimiento-facial/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(response.data['acceso_permitido'])

    def test_lectura_placa_simulada(self):
        """Test lectura de placa con simulación"""
        # Primero registrar un vehículo
        VehiculoRegistrado.objects.create(
            usuario=self.user,
            placa='1234ABC',
            marca='Test',
            modelo='Test'
        )

        data = {
            'imagen_base64': 'data:image/jpeg;base64,/9j/4AAQSkZJRgABAQAAAQ',
            'ubicacion': 'Entrada Vehicular'
        }

        response = self.client.post('/api/security/lectura-placa/', data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Nota: En simulación, puede que no encuentre la placa exacta

    def test_historial_accesos(self):
        """Test consultar historial de accesos"""
        # Crear algunos accesos de prueba
        Acceso.objects.create(
            usuario=self.user,
            tipo_acceso='manual',
            estado='permitido',
            ubicacion='Puerta Principal'
        )

        response = self.client.get('/api/security/accesos/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)

    def test_filtros_historial(self):
        """Test filtros en historial de accesos"""
        # Crear accesos de diferentes tipos
        Acceso.objects.create(
            usuario=self.user,
            tipo_acceso='facial',
            estado='permitido',
            ubicacion='Puerta 1'
        )
        Acceso.objects.create(
            usuario=self.user,
            tipo_acceso='placa',
            estado='denegado',
            ubicacion='Entrada'
        )

        # Filtrar por tipo
        response = self.client.get('/api/security/accesos/?tipo=facial')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['tipo_acceso'], 'facial')

        # Filtrar por estado
        response = self.client.get('/api/security/accesos/?estado=denegado')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['estado'], 'denegado')