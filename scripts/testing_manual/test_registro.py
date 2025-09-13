#!/usr/bin/env python3
"""
Script para probar el endpoint de registro de usuarios
Compatible con React y Flutter
"""

import requests
import json

# Configuración
BASE_URL = 'http://localhost:8000/api'
REGISTER_URL = f'{BASE_URL}/register/'

def test_user_registration():
    """Prueba el registro de un usuario nuevo"""
    
    # Datos de prueba para registro
    user_data = {
        "username": "test_user_2024",
        "email": "test@example.com",
        "password": "mypassword123",
        "password_confirm": "mypassword123",
        "first_name": "Usuario",
        "last_name": "Prueba",
        "role": "resident",
        "phone": "+1234567890",
        "address": "Apartamento 101, Torre A"
    }
    
    print("🚀 Probando endpoint de registro...")
    print(f"URL: {REGISTER_URL}")
    print(f"Datos: {json.dumps(user_data, indent=2)}")
    
    try:
        response = requests.post(REGISTER_URL, json=user_data)
        
        print(f"\n📊 Respuesta del servidor:")
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 201:
            data = response.json()
            print("✅ ¡Registro exitoso!")
            print(f"Usuario: {data.get('user', {})}")
            print(f"Tokens disponibles: {list(data.get('tokens', {}).keys())}")
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

def test_login_with_registered_user():
    """Prueba el login con el usuario registrado"""
    
    login_url = f'{BASE_URL}/token/'
    login_data = {
        "username": "test_user_2024",
        "password": "mypassword123"
    }
    
    print("\n🔐 Probando login con JWT...")
    
    try:
        response = requests.post(login_url, json=login_data)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ ¡Login exitoso!")
            print(f"Access token: {data.get('access', 'N/A')[:50]}...")
            print(f"Refresh token: {data.get('refresh', 'N/A')[:50]}...")
            return data
        else:
            print(f"❌ Error en login: {response.status_code}")
            print(f"Respuesta: {response.text}")
            
    except Exception as e:
        print(f"❌ Error en login: {e}")

if __name__ == "__main__":
    print("🧪 PRUEBA DE REGISTRO DE USUARIOS")
    print("=" * 50)
    
    # Probar registro
    registration_result = test_user_registration()
    
    # Si el registro fue exitoso, probar login
    if registration_result:
        test_login_with_registered_user()
    
    print("\n" + "=" * 50)
    print("✨ Prueba completada")
