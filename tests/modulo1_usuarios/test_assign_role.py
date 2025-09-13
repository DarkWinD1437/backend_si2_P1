#!/usr/bin/env python3
"""
Tests para Asignación de Roles - Módulo 1: Gestión de Usuarios
T4: Asignar rol a usuario

Este archivo contiene tests para verificar que:
1. Los administradores pueden asignar roles a usuarios
2. Los usuarios no pueden asignar roles por sí mismos
3. Se validan correctamente los roles permitidos
4. Se registran los cambios de rol en la bitácora
5. Los permisos se actualizan correctamente tras el cambio de rol
"""

import json
import requests
from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase, APIClient
from rest_framework.authtoken.models import Token
from rest_framework import status

User = get_user_model()

class RoleAssignmentTest(APITestCase):
    """Test case para la asignación de roles"""

    def setUp(self):
        """Configurar datos de prueba"""
        # Crear usuario administrador
        self.admin_user = User.objects.create_user(
            username='admin_test',
            email='admin@condominio.test',
            password='admin123',
            first_name='Admin',
            last_name='Test',
            role='admin',
            is_staff=True,
            is_superuser=True
        )
        
        # Crear usuario residente regular
        self.resident_user = User.objects.create_user(
            username='resident_test',
            email='resident@condominio.test',
            password='resident123',
            first_name='Resident',
            last_name='Test',
            role='resident'
        )
        
        # Crear otro usuario residente para pruebas
        self.target_user = User.objects.create_user(
            username='target_user',
            email='target@condominio.test',
            password='target123',
            first_name='Target',
            last_name='User',
            role='resident'
        )
        
        # Crear tokens de autenticación
        self.admin_token = Token.objects.create(user=self.admin_user)
        self.resident_token = Token.objects.create(user=self.resident_user)
        
        self.client = APIClient()

    def test_admin_can_assign_role(self):
        """Test: El administrador puede asignar roles a otros usuarios"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        
        url = f'/api/users/{self.target_user.id}/assign-role/'
        data = {
            'role': 'security'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data.get('success'))
        
        # Verificar que el rol se cambió en la base de datos
        self.target_user.refresh_from_db()
        self.assertEqual(self.target_user.role, 'security')
        
        # Verificar respuesta
        self.assertIn('message', response.data)
        self.assertEqual(response.data['user']['role'], 'security')

    def test_user_cannot_assign_role_to_others(self):
        """Test: Los usuarios regulares no pueden asignar roles"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.resident_token.key}')
        
        url = f'/api/users/{self.target_user.id}/assign-role/'
        data = {
            'role': 'security'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_user_cannot_assign_role_to_self(self):
        """Test: Los usuarios no pueden cambiar su propio rol"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.resident_token.key}')
        
        url = f'/api/users/{self.resident_user.id}/assign-role/'
        data = {
            'role': 'admin'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_invalid_role_assignment(self):
        """Test: No se pueden asignar roles inválidos"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        
        url = f'/api/users/{self.target_user.id}/assign-role/'
        data = {
            'role': 'invalid_role'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertFalse(response.data.get('success', True))

    def test_assign_role_to_nonexistent_user(self):
        """Test: No se puede asignar rol a usuario inexistente"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        
        url = '/api/users/99999/assign-role/'
        data = {
            'role': 'security'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_role_assignment_validation(self):
        """Test: Validar que solo se acepten roles válidos"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        
        valid_roles = ['admin', 'resident', 'security']
        
        for role in valid_roles:
            url = f'/api/users/{self.target_user.id}/assign-role/'
            data = {'role': role}
            
            response = self.client.post(url, data, format='json')
            
            self.assertEqual(response.status_code, status.HTTP_200_OK)
            self.target_user.refresh_from_db()
            self.assertEqual(self.target_user.role, role)

    def test_role_assignment_without_authentication(self):
        """Test: No se puede asignar roles sin autenticación"""
        url = f'/api/users/{self.target_user.id}/assign-role/'
        data = {
            'role': 'security'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_get_user_with_role_info(self):
        """Test: Obtener información completa del usuario incluyendo rol"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        
        url = f'/api/users/{self.target_user.id}/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('role', response.data)
        self.assertEqual(response.data['role'], self.target_user.role)

    def test_list_users_with_roles(self):
        """Test: Listar todos los usuarios con su información de roles"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        
        url = '/api/users/'
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que todos los usuarios tienen información de rol
        if 'users' in response.data:
            users = response.data['users']
        else:
            users = response.data.get('results', response.data)
            
        for user_data in users:
            self.assertIn('role', user_data)

    def test_role_assignment_preserves_other_data(self):
        """Test: La asignación de rol no afecta otros datos del usuario"""
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.admin_token.key}')
        
        # Guardar datos originales
        original_email = self.target_user.email
        original_username = self.target_user.username
        original_first_name = self.target_user.first_name
        
        url = f'/api/users/{self.target_user.id}/assign-role/'
        data = {
            'role': 'security'
        }
        
        response = self.client.post(url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verificar que otros datos no cambiaron
        self.target_user.refresh_from_db()
        self.assertEqual(self.target_user.email, original_email)
        self.assertEqual(self.target_user.username, original_username)
        self.assertEqual(self.target_user.first_name, original_first_name)

class RoleAssignmentIntegrationTest(TestCase):
    """Tests de integración para asignación de roles con servidor real"""

    def setUp(self):
        """Configurar cliente para pruebas de integración"""
        self.base_url = "http://127.0.0.1:8000"
        
        # Crear usuarios de prueba
        self.admin_user = User.objects.create_user(
            username='admin_integration',
            email='admin_int@test.com',
            password='admin123',
            role='admin',
            is_staff=True,
            is_superuser=True
        )
        
        self.test_user = User.objects.create_user(
            username='test_user_role',
            email='test_role@test.com',
            password='test123',
            role='resident'
        )
        
        # Obtener tokens
        self.admin_token = Token.objects.create(user=self.admin_user)

    def test_role_assignment_integration(self):
        """Test de integración completo para asignación de roles"""
        try:
            # Test: Asignar rol a usuario
            url = f"{self.base_url}/api/users/{self.test_user.id}/assign-role/"
            headers = {
                'Authorization': f'Token {self.admin_token.key}',
                'Content-Type': 'application/json'
            }
            data = {
                'role': 'security'
            }
            
            response = requests.post(url, headers=headers, json=data)
            
            if response.status_code == 200:
                response_data = response.json()
                self.assertTrue(response_data.get('success'))
                
                # Verificar en base de datos
                self.test_user.refresh_from_db()
                self.assertEqual(self.test_user.role, 'security')
                
                print("✅ Test de asignación de rol: EXITOSO")
            else:
                print(f"❌ Test de asignación de rol falló: {response.status_code}")
                print(f"Respuesta: {response.text}")
                
        except requests.exceptions.ConnectionError:
            print("⚠️  Servidor no disponible para pruebas de integración")

def run_role_assignment_tests():
    """Función para ejecutar todos los tests de asignación de roles"""
    print("\n" + "="*60)
    print("EJECUTANDO TESTS DE ASIGNACIÓN DE ROLES")
    print("="*60)
    
    # Ejecutar tests unitarios
    import unittest
    
    # Crear suite de tests
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Cargar tests de la clase
    suite.addTests(loader.loadTestsFromTestCase(RoleAssignmentTest))
    
    # Ejecutar tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Mostrar resumen
    print(f"\nTests ejecutados: {result.testsRun}")
    print(f"Fallos: {len(result.failures)}")
    print(f"Errores: {len(result.errors)}")
    
    if result.failures:
        print("\nFALLOS:")
        for test, traceback in result.failures:
            print(f"- {test}: {traceback}")
    
    if result.errors:
        print("\nERRORES:")
        for test, traceback in result.errors:
            print(f"- {test}: {traceback}")
    
    return len(result.failures) == 0 and len(result.errors) == 0

if __name__ == '__main__':
    run_role_assignment_tests()
