#!/usr/bin/env python3
"""
Script para probar el endpoint de registro con un usuario único
"""

import requests
import json
from datetime import datetime

# Configuración
BASE_URL = 'http://localhost:8000/api'
REGISTER_URL = f'{BASE_URL}/register/'

def test_user_registration():
    """Prueba el registro de un usuario nuevo con timestamp único"""
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Datos de prueba para registro con timestamp único
    user_data = {
        "username": f"user_{timestamp}",
        "email": f"user_{timestamp}@example.com",
        "password": "mypassword123",
        "password_confirm": "mypassword123",
        "first_name": "Usuario",
        "last_name": "Prueba",
        "role": "resident",
        "phone": "+1234567890",
        "address": "Apartamento 101, Torre A"
    }
    
    print("🚀 Probando endpoint de registro con usuario único...")
    print(f"URL: {REGISTER_URL}")
    print(f"Username: {user_data['username']}")
    print(f"Email: {user_data['email']}")
    
    try:
        response = requests.post(REGISTER_URL, json=user_data)
        
        print(f"\n📊 Respuesta del servidor:")
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 201:
            data = response.json()
            print("✅ ¡Registro exitoso!")
            print(f"Usuario creado: {data.get('user', {})}")
            
            # Verificar tokens
            tokens = data.get('tokens', {})
            print(f"\n🔑 Tokens generados:")
            print(f"- JWT Access Token: {'✅' if tokens.get('access') else '❌'}")
            print(f"- JWT Refresh Token: {'✅' if tokens.get('refresh') else '❌'}")
            print(f"- Auth Token: {'✅' if tokens.get('token') else '❌'}")
            
            return data
            
        elif response.status_code == 400:
            data = response.json()
            print("❌ Error de validación:")
            print(f"Errores: {data.get('errors', {})}")
            
        else:
            print(f"❌ Error inesperado: {response.status_code}")
            print(f"Respuesta: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar al servidor")
        print("Asegúrate de que el servidor Django esté ejecutándose en http://localhost:8000")
        
    except Exception as e:
        print(f"❌ Error inesperado: {e}")

def test_endpoints_for_react_flutter():
    """Prueba endpoints específicos para React y Flutter"""
    
    print("\n🔍 VERIFICANDO ENDPOINTS PARA REACT Y FLUTTER")
    print("=" * 60)
    
    endpoints_to_test = [
        ('POST', f'{BASE_URL}/register/', 'Registro de usuarios'),
        ('POST', f'{BASE_URL}/token/', 'Login JWT'),
        ('POST', f'{BASE_URL}/token/refresh/', 'Refresh JWT token'),
        ('GET', f'{BASE_URL}/users/me/', 'Obtener perfil usuario'),
        ('GET', f'{BASE_URL}/status/', 'Status de la API'),
    ]
    
    for method, url, description in endpoints_to_test:
        print(f"{method} {url} - {description}")
        
        try:
            if method == 'GET':
                response = requests.get(url, timeout=2)
            else:
                response = requests.post(url, json={}, timeout=2)
                
            if response.status_code in [200, 201, 400, 401, 403]:
                print(f"  ✅ Endpoint disponible (Status: {response.status_code})")
            else:
                print(f"  ❓ Endpoint responde (Status: {response.status_code})")
                
        except requests.exceptions.ConnectionError:
            print(f"  ❌ Endpoint no disponible")
        except Exception as e:
            print(f"  ⚠️  Error: {str(e)[:50]}...")

if __name__ == "__main__":
    print("🧪 PRUEBA COMPLETA DE REGISTRO DE USUARIOS")
    print("=" * 60)
    
    # Probar registro con usuario único
    registration_result = test_user_registration()
    
    # Verificar endpoints disponibles
    test_endpoints_for_react_flutter()
    
    print("\n" + "=" * 60)
    
    if registration_result:
        print("✅ RESULTADO: Backend listo para React y Flutter")
        print("📋 Endpoints principales disponibles:")
        print("   - POST /api/register/ (Registro)")
        print("   - POST /api/token/ (Login JWT)")
        print("   - POST /api/token/refresh/ (Refresh)")
        print("   - GET /api/users/me/ (Perfil)")
    else:
        print("⚠️ RESULTADO: Revisar configuración del backend")
        
    print("✨ Prueba completada")
