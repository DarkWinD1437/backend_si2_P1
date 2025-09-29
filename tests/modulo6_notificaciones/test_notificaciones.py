import json
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework import status

User = get_user_model()

# Test básico para verificar que la app funciona
class BasicTest(TestCase):
    """Test básico para verificar que la app está funcionando"""

    def test_app_exists(self):
        """Verificar que la app existe"""
        from django.apps import apps
        app = apps.get_app_config('modulo_notificaciones')
        self.assertIsNotNone(app)
        self.assertEqual(app.name, 'backend.apps.modulo_notificaciones')


class DispositivoTests(APITestCase):
    """Tests para el modelo y endpoints de Dispositivo"""

    def setUp(self):
        from backend.apps.modulo_notificaciones.models import Dispositivo
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_registrar_dispositivo(self):
        """Test registrar un nuevo dispositivo"""
        from backend.apps.modulo_notificaciones.models import Dispositivo
        url = reverse('dispositivos-registrar')
        data = {
            'token_push': 'fcm_token_12345',
            'tipo_dispositivo': 'android',
            'nombre_dispositivo': 'Mi Teléfono'
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Dispositivo.objects.count(), 1)
        dispositivo = Dispositivo.objects.first()
        self.assertEqual(dispositivo.usuario, self.user)
        self.assertEqual(dispositivo.token_push, 'fcm_token_12345')

    def test_listar_dispositivos(self):
        """Test listar dispositivos del usuario"""
        from backend.apps.modulo_notificaciones.models import Dispositivo
        # Crear dispositivo
        Dispositivo.objects.create(
            usuario=self.user,
            token_push='token1',
            tipo_dispositivo='android'
        )

        url = reverse('dispositivos-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_desactivar_dispositivo(self):
        """Test desactivar un dispositivo"""
        from backend.apps.modulo_notificaciones.models import Dispositivo
        dispositivo = Dispositivo.objects.create(
            usuario=self.user,
            token_push='token1',
            tipo_dispositivo='android'
        )

        url = reverse('dispositivos-desactivar', kwargs={'pk': dispositivo.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        dispositivo.refresh_from_db()
        self.assertFalse(dispositivo.activo)


class PreferenciasNotificacionTests(APITestCase):
    """Tests para preferencias de notificación"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_crear_preferencia(self):
        """Test crear una preferencia de notificación"""
        from backend.apps.modulo_notificaciones.models import PreferenciasNotificacion
        url = reverse('preferencias-list')
        data = {
            'tipo_notificacion': 'acceso_permitido',
            'push_enabled': True,
            'email_enabled': False,
            'sms_enabled': False
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PreferenciasNotificacion.objects.count(), 1)

    def test_actualizar_preferencias_bulk(self):
        """Test actualizar múltiples preferencias a la vez"""
        from backend.apps.modulo_notificaciones.models import PreferenciasNotificacion
        url = reverse('preferencias-bulk-update')
        data = {
            'preferencias': [
                {
                    'tipo_notificacion': 'acceso_permitido',
                    'push_enabled': True,
                    'email_enabled': False
                },
                {
                    'tipo_notificacion': 'nuevo_mensaje',
                    'push_enabled': True,
                    'email_enabled': True
                }
            ]
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(PreferenciasNotificacion.objects.count(), 2)


class NotificacionTests(APITestCase):
    """Tests para notificaciones"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_listar_notificaciones(self):
        """Test listar notificaciones del usuario"""
        from backend.apps.modulo_notificaciones.models import Notificacion
        # Crear notificación
        Notificacion.objects.create(
            titulo='Test',
            mensaje='Mensaje de prueba',
            tipo='sistema',
            usuario=self.user
        )

        url = reverse('notificaciones-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_marcar_leida(self):
        """Test marcar notificación como leída"""
        from backend.apps.modulo_notificaciones.models import Notificacion
        notificacion = Notificacion.objects.create(
            titulo='Test',
            mensaje='Mensaje',
            tipo='sistema',
            usuario=self.user
        )

        url = reverse('notificaciones-marcar-leida', kwargs={'pk': notificacion.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        notificacion.refresh_from_db()
        self.assertEqual(notificacion.estado, 'leida')
        self.assertIsNotNone(notificacion.fecha_lectura)

    def test_marcar_todas_leidas(self):
        """Test marcar todas las notificaciones como leídas"""
        from backend.apps.modulo_notificaciones.models import Notificacion
        Notificacion.objects.create(
            titulo='Test1',
            mensaje='Mensaje1',
            tipo='sistema',
            usuario=self.user
        )
        Notificacion.objects.create(
            titulo='Test2',
            mensaje='Mensaje2',
            tipo='sistema',
            usuario=self.user
        )

        url = reverse('notificaciones-marcar-todas-leidas')
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar que ambas están leídas
        leidas = Notificacion.objects.filter(
            usuario=self.user,
            estado='leida'
        ).count()
        self.assertEqual(leidas, 2)


class EnviarNotificacionTests(APITestCase):
    """Tests para envío de notificaciones"""

    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='admin123'
        )
        self.regular_user = User.objects.create_user(
            username='user',
            email='user@example.com',
            password='user123'
        )
        self.client.force_authenticate(user=self.admin_user)

    def test_enviar_notificacion_push(self):
        """Test enviar notificación push masiva"""
        from backend.apps.modulo_notificaciones.models import Notificacion
        url = reverse('enviar-push')
        data = {
            'titulo': 'Prueba de Notificación',
            'mensaje': 'Esta es una notificación de prueba',
            'tipo': 'sistema',
            'usuarios_ids': [self.regular_user.id],
            'prioridad': 3
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        # Verificar que se creó la notificación
        notificacion = Notificacion.objects.filter(
            usuario=self.regular_user,
            titulo='Prueba de Notificación'
        ).first()
        self.assertIsNotNone(notificacion)

    def test_crear_notificacion_individual(self):
        """Test crear notificación individual"""
        from backend.apps.modulo_notificaciones.models import Notificacion
        url = reverse('crear-notificacion')
        data = {
            'titulo': 'Notificación Individual',
            'mensaje': 'Mensaje personalizado',
            'tipo': 'sistema',
            'usuario': self.regular_user.id,
            'prioridad': 2
        }

        response = self.client.post(url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        notificacion = Notificacion.objects.filter(
            usuario=self.regular_user,
            titulo='Notificación Individual'
        ).first()
        self.assertIsNotNone(notificacion)


class NotificacionServiceTests(TestCase):
    """Tests para el servicio de notificaciones"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_crear_preferencias_default(self):
        """Test crear preferencias por defecto"""
        from backend.apps.modulo_notificaciones.services import NotificacionService
        from backend.apps.modulo_notificaciones.models import PreferenciasNotificacion
        service = NotificacionService()
        service.crear_preferencias_default(self.user)

        # Verificar que se crearon las preferencias
        preferencias = PreferenciasNotificacion.objects.filter(usuario=self.user)
        self.assertEqual(preferencias.count(), 8)  # 8 tipos de notificación

    def test_usuario_acepta_notificacion(self):
        """Test verificar si usuario acepta tipo de notificación"""
        from backend.apps.modulo_notificaciones.services import NotificacionService
        from backend.apps.modulo_notificaciones.models import PreferenciasNotificacion

        # Crear preferencia
        PreferenciasNotificacion.objects.create(
            usuario=self.user,
            tipo_notificacion='acceso_permitido',
            push_enabled=True
        )

        service = NotificacionService()
        acepta = service._usuario_acepta_notificacion(self.user, 'acceso_permitido')
        self.assertTrue(acepta)

        # Test con tipo no configurado (debe aceptar por defecto)
        acepta_default = service._usuario_acepta_notificacion(self.user, 'emergencia')
        self.assertTrue(acepta_default)