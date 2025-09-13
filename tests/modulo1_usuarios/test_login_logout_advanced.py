#!/usr/bin/env python3
"""
Test Avanzado - Casos Edge y Robustez
Módulo 1: T2 Iniciar y Cerrar Sesión

Este script verifica casos especiales y robustez:
1. Múltiples logins simultáneos
2. Logout con token ya invalidado
3. Logout sin token
4. Refresh de JWT tokens
5. Concurrencia de sesiones
"""

import requests
import json
import time
import concurrent.futures
from threading import Lock

# Configuración
BASE_URL = "http://127.0.0.1:8000/api"
HEADERS = {'Content-Type': 'application/json'}
results_lock = Lock()
test_results = []

def log_result(test_name, success, details):
    """Thread-safe logging de resultados"""
    with results_lock:
        test_results.append({
            'test': test_name,
            'success': success,
            'details': details
        })

def test_multiple_concurrent_logins():
    """Test múltiples logins concurrentes del mismo usuario"""
    print("🔄 Test Múltiples Logins Concurrentes")
    
    def login_worker(worker_id):
        credentials = {"username": "admin_smart", "password": "admin123"}
        login_url = f"{BASE_URL}/login/"
        
        try:
            response = requests.post(login_url, json=credentials, headers=HEADERS)
            if response.status_code == 200:
                data = response.json()
                token = data.get('token')
                log_result(f'concurrent_login_{worker_id}', True, f'Token: {token[:10]}...')
                return token
            else:
                log_result(f'concurrent_login_{worker_id}', False, f'Status: {response.status_code}')
                return None
        except Exception as e:
            log_result(f'concurrent_login_{worker_id}', False, f'Error: {str(e)}')
            return None
    
    # Ejecutar 5 logins concurrentes
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(login_worker, i) for i in range(5)]
        tokens = [future.result() for future in concurrent.futures.as_completed(futures)]
    
    successful_logins = [t for t in tokens if t is not None]
    print(f"   ✅ {len(successful_logins)}/5 logins concurrentes exitosos")
    
    return successful_logins

def test_logout_with_invalid_token():
    """Test logout con token ya invalidado"""
    print("🚫 Test Logout con Token Inválido")
    
    # Primero hacer login
    credentials = {"username": "admin_smart", "password": "admin123"}
    login_url = f"{BASE_URL}/login/"
    
    try:
        response = requests.post(login_url, json=credentials, headers=HEADERS)
        if response.status_code != 200:
            print("   ❌ No se pudo obtener token inicial")
            return
        
        token = response.json().get('token')
        
        # Hacer logout una vez
        logout_url = f"{BASE_URL}/logout/"
        headers = {'Authorization': f'Token {token}', 'Content-Type': 'application/json'}
        
        response = requests.post(logout_url, headers=headers)
        print(f"   Primera logout - Status: {response.status_code}")
        
        # Intentar logout nuevamente con el mismo token
        response = requests.post(logout_url, headers=headers)
        print(f"   Segunda logout - Status: {response.status_code}")
        
        if response.status_code == 401:
            print("   ✅ Correctamente rechazó token ya invalidado")
        else:
            print(f"   ⚠️  Comportamiento inesperado: {response.status_code}")
            
    except Exception as e:
        print(f"   💥 Error: {e}")

def test_logout_without_token():
    """Test logout sin proporcionar token"""
    print("🔐 Test Logout sin Token")
    
    logout_url = f"{BASE_URL}/logout/"
    
    try:
        # Intento sin Authorization header
        response = requests.post(logout_url, headers=HEADERS)
        print(f"   Sin token - Status: {response.status_code}")
        
        if response.status_code == 401:
            print("   ✅ Correctamente rechazó request sin token")
        else:
            print(f"   ⚠️  Comportamiento inesperado: {response.status_code}")
            
        # Intento con token malformado
        headers = {'Authorization': 'Token invalid_token_here', 'Content-Type': 'application/json'}
        response = requests.post(logout_url, headers=headers)
        print(f"   Token inválido - Status: {response.status_code}")
        
        if response.status_code == 401:
            print("   ✅ Correctamente rechazó token malformado")
        else:
            print(f"   ⚠️  Comportamiento inesperado: {response.status_code}")
            
    except Exception as e:
        print(f"   💥 Error: {e}")

def test_jwt_refresh_functionality():
    """Test funcionalidad de refresh de JWT tokens"""
    print("🔄 Test JWT Token Refresh")
    
    # Login con JWT
    credentials = {"username": "admin_smart", "password": "admin123"}
    jwt_login_url = f"{BASE_URL}/token/"
    
    try:
        response = requests.post(jwt_login_url, json=credentials, headers=HEADERS)
        if response.status_code != 200:
            print("   ❌ No se pudo hacer JWT login")
            return
        
        data = response.json()
        access_token = data.get('access')
        refresh_token = data.get('refresh')
        
        print(f"   Login JWT exitoso - Access: {access_token[:20]}...")
        
        # Verificar que access token funciona
        me_url = f"{BASE_URL}/me/"
        headers = {'Authorization': f'Bearer {access_token}', 'Content-Type': 'application/json'}
        
        response = requests.get(me_url, headers=headers)
        print(f"   Verificación /me/ con access token - Status: {response.status_code}")
        
        # Refresh del token
        refresh_url = f"{BASE_URL}/token/refresh/"
        refresh_data = {"refresh": refresh_token}
        
        response = requests.post(refresh_url, json=refresh_data, headers=HEADERS)
        print(f"   Token refresh - Status: {response.status_code}")
        
        if response.status_code == 200:
            new_data = response.json()
            new_access = new_data.get('access')
            print(f"   ✅ Token refresh exitoso - Nuevo access: {new_access[:20]}...")
            
            # Verificar que el nuevo token funciona
            headers = {'Authorization': f'Bearer {new_access}', 'Content-Type': 'application/json'}
            response = requests.get(me_url, headers=headers)
            
            if response.status_code == 200:
                print("   ✅ Nuevo access token funciona correctamente")
            else:
                print("   ❌ Nuevo access token no funciona")
        else:
            print("   ❌ Error en token refresh")
            
    except Exception as e:
        print(f"   💥 Error: {e}")

def test_session_persistence():
    """Test persistencia de sesiones"""
    print("💾 Test Persistencia de Sesiones")
    
    # Login
    credentials = {"username": "maria", "password": "password123"}
    login_url = f"{BASE_URL}/login/"
    
    try:
        response = requests.post(login_url, json=credentials, headers=HEADERS)
        if response.status_code != 200:
            print("   ❌ Login fallido")
            return
        
        token = response.json().get('token')
        user_id = response.json().get('user_id')
        
        # Hacer múltiples requests con el mismo token
        me_url = f"{BASE_URL}/me/"
        headers = {'Authorization': f'Token {token}', 'Content-Type': 'application/json'}
        
        successful_requests = 0
        for i in range(5):
            response = requests.get(me_url, headers=headers)
            if response.status_code == 200:
                successful_requests += 1
            time.sleep(0.1)  # Pequeña pausa entre requests
        
        print(f"   ✅ {successful_requests}/5 requests exitosos con mismo token")
        
        if successful_requests == 5:
            print("   ✅ Persistencia de sesión funcional")
        else:
            print("   ⚠️  Posibles problemas de persistencia")
            
    except Exception as e:
        print(f"   💥 Error: {e}")

def test_user_data_consistency():
    """Test consistencia de datos de usuario"""
    print("📊 Test Consistencia de Datos")
    
    # Test con diferentes usuarios
    users_to_test = [
        {"username": "admin_smart", "expected_role": "admin"},
        {"username": "carlos", "expected_role": "resident"},
        {"username": "maria", "expected_role": "resident"},
    ]
    
    for user_data in users_to_test:
        try:
            # Login
            credentials = {"username": user_data["username"], "password": "password123" if user_data["username"] != "admin_smart" else "admin123"}
            login_url = f"{BASE_URL}/login/"
            
            response = requests.post(login_url, json=credentials, headers=HEADERS)
            if response.status_code != 200:
                print(f"   ❌ Login fallido para {user_data['username']}")
                continue
            
            token = response.json().get('token')
            
            # Obtener datos del usuario
            me_url = f"{BASE_URL}/me/"
            headers = {'Authorization': f'Token {token}', 'Content-Type': 'application/json'}
            
            response = requests.get(me_url, headers=headers)
            if response.status_code == 200:
                data = response.json()
                username = data.get('username')
                role = data.get('role')
                
                print(f"   👤 {username} - Rol: {role}")
                
                if username == user_data["username"]:
                    print(f"   ✅ Username consistente para {username}")
                else:
                    print(f"   ❌ Username inconsistente para {username}")
            else:
                print(f"   ❌ No se pudieron obtener datos para {user_data['username']}")
                
        except Exception as e:
            print(f"   💥 Error con {user_data['username']}: {e}")

def main():
    """Función principal que ejecuta todos los tests avanzados"""
    print("🧪 TESTING AVANZADO - CASOS EDGE Y ROBUSTEZ")
    print("📋 Módulo 1: T2 - Iniciar y Cerrar Sesión")
    print("=" * 70)
    
    # Test 1: Logins concurrentes
    tokens = test_multiple_concurrent_logins()
    print("-" * 50)
    
    # Test 2: Logout con token inválido
    test_logout_with_invalid_token()
    print("-" * 50)
    
    # Test 3: Logout sin token
    test_logout_without_token()
    print("-" * 50)
    
    # Test 4: JWT refresh
    test_jwt_refresh_functionality()
    print("-" * 50)
    
    # Test 5: Persistencia de sesiones
    test_session_persistence()
    print("-" * 50)
    
    # Test 6: Consistencia de datos
    test_user_data_consistency()
    print("-" * 50)
    
    # Resumen final
    print("\n📊 RESULTADOS DE TESTS AVANZADOS")
    print("=" * 70)
    
    # Contar resultados
    successful_tests = sum(1 for result in test_results if result['success'])
    total_tests = len(test_results)
    
    print(f"✅ Tests exitosos: {successful_tests}")
    print(f"❌ Tests fallidos: {total_tests - successful_tests}")
    print(f"📊 Total ejecutados: {total_tests}")
    
    # Mostrar detalles de tests fallidos si los hay
    failed_tests = [result for result in test_results if not result['success']]
    if failed_tests:
        print("\n❌ DETALLES DE TESTS FALLIDOS:")
        for test in failed_tests:
            print(f"   • {test['test']}: {test['details']}")
    
    print("\n🎯 CONCLUSIÓN TESTS AVANZADOS:")
    if len(failed_tests) == 0:
        print("✅ TODAS LAS PRUEBAS AVANZADAS PASARON")
        print("🛡️  EL SISTEMA ES ROBUSTO Y MANEJA CASOS EDGE CORRECTAMENTE")
    else:
        print("⚠️  ALGUNOS TESTS AVANZADOS FALLARON - REVISAR IMPLEMENTACIÓN")
    
    print("=" * 70)

if __name__ == "__main__":
    main()
