#!/usr/bin/env python
"""
Script de Prueba para Notificaciones Push - SmartCondominium
===========================================================

Este script permite probar el funcionamiento completo del módulo de notificaciones,
incluyendo la conexión con Firebase Cloud Messaging (FCM) y el envío de notificaciones.

Uso:
    python test_notificaciones.py [opciones]

Opciones:
    --test-connection    Solo probar conexión con Firebase
    --test-notification  Enviar notificación de prueba
    --test-device        Registrar dispositivo de prueba
    --full-test         Ejecutar todas las pruebas
    --help              Mostrar esta ayuda

Ejemplos:
    python test_notificaciones.py --test-connection
    python test_notificaciones.py --full-test
"""

import os
import sys
import json
import argparse
import requests
from pathlib import Path

# Agregar el directorio del proyecto al path
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
import django
django.setup()

from django.conf import settings
from backend.apps.modulo_notificaciones.services import NotificacionService
from backend.apps.modulo_notificaciones.models import Dispositivo, Notificacion
from django.contrib.auth import get_user_model

User = get_user_model()

class NotificacionesTester:
    def __init__(self):
        self.service = NotificacionService()
        self.api_base = "http://localhost:8000/api"
        self.test_user_id = None
        self.test_device_token = "test-device-token-12345"

    def print_header(self, title):
        print(f"\n{'='*60}")
        print(f"🔍 {title}")
        print(f"{'='*60}")

    def print_success(self, message):
        print(f"✅ {message}")

    def print_error(self, message):
        print(f"❌ {message}")

    def print_info(self, message):
        print(f"ℹ️  {message}")

    def test_firebase_connection(self):
        """Prueba la conexión básica con Firebase"""
        self.print_header("Probando Conexión con Firebase")

        # Verificar configuración
        print(f"Project ID: {self.service.fcm_project_id or 'NO CONFIGURADO'}")
        print(f"Credentials path: {self.service.fcm_credentials_path or 'NO CONFIGURADO'}")

        if not self.service.fcm_project_id:
            self.print_error("FCM_PROJECT_ID no está configurado")
            return False

        if not self.service.fcm_credentials_path:
            self.print_error("FCM_CREDENTIALS_PATH no está configurado")
            return False

        # Verificar archivo de credenciales
        import os
        if not os.path.exists(self.service.fcm_credentials_path):
            self.print_error(f"Archivo de credenciales no encontrado: {self.service.fcm_credentials_path}")
            return False

        self.print_success("Archivo de credenciales encontrado")

        # Probar obtener access token
        try:
            token = self.service._get_access_token()
            if token:
                self.print_success(f"Access token obtenido correctamente (primeros 20 chars: {token[:20]}...)")
                return True
            else:
                self.print_error("No se pudo obtener access token")
                return False
        except Exception as e:
            self.print_error(f"Error obteniendo access token: {e}")
            return False

    def create_test_user(self):
        """Crear usuario de prueba si no existe"""
        try:
            user, created = User.objects.get_or_create(
                username='test_user',
                defaults={
                    'email': 'test@example.com',
                    'first_name': 'Usuario',
                    'last_name': 'Prueba'
                }
            )
            if created:
                user.set_password('testpass123')
                user.save()
                self.print_success(f"Usuario de prueba creado: {user.username} (ID: {user.id})")
            else:
                self.print_success(f"Usuario de prueba existente: {user.username} (ID: {user.id})")

            self.test_user_id = user.id
            return user.id
        except Exception as e:
            self.print_error(f"Error creando usuario de prueba: {e}")
            return None

    def test_device_registration(self):
        """Probar registro de dispositivo"""
        self.print_header("Probando Registro de Dispositivo")

        if not self.test_user_id:
            self.test_user_id = self.create_test_user()

        if not self.test_user_id:
            return False

        # Verificar si ya existe el dispositivo
        existing_device = Dispositivo.objects.filter(
            usuario_id=self.test_user_id,
            token_push=self.test_device_token
        ).first()

        if existing_device:
            self.print_success(f"Dispositivo ya registrado (ID: {existing_device.id})")
            return True

        # Crear dispositivo usando el modelo directamente
        try:
            device = Dispositivo.objects.create(
                usuario_id=self.test_user_id,
                token_push=self.test_device_token,
                tipo_dispositivo='web',
                activo=True
            )
            self.print_success(f"Dispositivo registrado exitosamente (ID: {device.id})")
            return True
        except Exception as e:
            self.print_error(f"Error registrando dispositivo: {e}")
            return False

    def test_notification_sending(self):
        """Probar envío de notificación"""
        self.print_header("Probando Envío de Notificación")

        if not self.test_user_id:
            self.test_user_id = self.create_test_user()

        if not self.test_user_id:
            return False

        # Crear notificación de prueba
        try:
            # Usar el servicio para enviar notificación
            resultado = self.service.enviar_notificacion_masiva(
                titulo="🧪 Notificación de Prueba",
                mensaje="Esta es una notificación de prueba automática. Si la ves, ¡Firebase está funcionando! 🎉",
                tipo="prueba",
                usuarios_ids=[self.test_user_id],
                prioridad=1
            )

            if resultado['push_enviados'] > 0:
                self.print_success("Notificación enviada exitosamente")
                self.print_info(f"Resultado: {resultado}")
                return True
            else:
                self.print_error(f"Error enviando notificación: {resultado.get('errores', 'Error desconocido')}")
                return False

        except Exception as e:
            self.print_error(f"Error en envío de notificación: {e}")
            return False

    def test_api_endpoints(self):
        """Probar endpoints de la API REST"""
        self.print_header("Probando Endpoints de API")

        if not self.test_user_id:
            self.test_user_id = self.create_test_user()

        # Nota: Para probar los endpoints REST necesitarías autenticación
        # Por ahora solo verificamos que los URLs están configurados
        from django.urls import reverse
        try:
            # Verificar que las URLs existen
            url_dispositivos = reverse('dispositivos-list')
            url_notificaciones = reverse('notificaciones-list')
            url_preferencias = reverse('preferencias-list')

            self.print_success("URLs de API configuradas correctamente:")
            self.print_info(f"  Dispositivos: {url_dispositivos}")
            self.print_info(f"  Notificaciones: {url_notificaciones}")
            self.print_info(f"  Preferencias: {url_preferencias}")
            return True
        except Exception as e:
            self.print_error(f"Error en configuración de URLs: {e}")
            return False

    def run_full_test(self):
        """Ejecutar todas las pruebas"""
        self.print_header("🚀 INICIANDO PRUEBAS COMPLETAS DEL SISTEMA DE NOTIFICACIONES")

        results = []

        # Prueba 1: Conexión Firebase
        results.append(("Conexión Firebase", self.test_firebase_connection()))

        # Prueba 2: Registro de dispositivo
        results.append(("Registro Dispositivo", self.test_device_registration()))

        # Prueba 3: Envío de notificación
        results.append(("Envío Notificación", self.test_notification_sending()))

        # Prueba 4: Endpoints API
        results.append(("Endpoints API", self.test_api_endpoints()))

        # Resumen final
        self.print_header("📊 RESUMEN DE PRUEBAS")

        passed = 0
        total = len(results)

        for test_name, success in results:
            status = "✅ PASÓ" if success else "❌ FALLÓ"
            print(f"{test_name}: {status}")
            if success:
                passed += 1

        print(f"\nResultado Final: {passed}/{total} pruebas pasaron")

        if passed == total:
            self.print_success("🎉 ¡Todas las pruebas pasaron! El sistema de notificaciones está funcionando correctamente.")
            return True
        else:
            self.print_error("⚠️  Algunas pruebas fallaron. Revisa la configuración de Firebase.")
            return False

def main():
    parser = argparse.ArgumentParser(description='Script de prueba para notificaciones push')
    parser.add_argument('--test-connection', action='store_true', help='Solo probar conexión con Firebase')
    parser.add_argument('--test-notification', action='store_true', help='Enviar notificación de prueba')
    parser.add_argument('--test-device', action='store_true', help='Registrar dispositivo de prueba')
    parser.add_argument('--full-test', action='store_true', help='Ejecutar todas las pruebas')

    args = parser.parse_args()

    if len(sys.argv) == 1:
        parser.print_help()
        return

    tester = NotificacionesTester()

    if args.test_connection:
        tester.test_firebase_connection()
    elif args.test_device:
        tester.test_device_registration()
    elif args.test_notification:
        tester.test_notification_sending()
    elif args.full_test:
        success = tester.run_full_test()
        sys.exit(0 if success else 1)
    else:
        print("Usa --help para ver las opciones disponibles")

if __name__ == '__main__':
    main()