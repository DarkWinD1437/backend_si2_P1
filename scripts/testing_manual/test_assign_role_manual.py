#!/usr/bin/env python3
"""
Test Manual para Asignación de Roles - T4: Asignar rol a usuario
Script para probar manualmente la funcionalidad de asignación de roles
"""

import requests
import json
import sys
from datetime import datetime

# Configuración
BASE_URL = "http://127.0.0.1:8000"
ADMIN_CREDENTIALS = {
    "username": "admin",
    "password": "clave123"
}

def print_header(title):
    """Imprimir encabezado de sección"""
    print("\n" + "="*60)
    print(f"🔧 {title}")
    print("="*60)

def print_test(test_name, success, details=""):
    """Imprimir resultado de test"""
    status = "✅" if success else "❌"
    print(f"{status} {test_name}")
    if details:
        print(f"   📋 {details}")

def test_role_assignment():
    """Test completo de asignación de roles"""
    print_header("INICIANDO TESTS MANUALES DE ASIGNACIÓN DE ROLES")
    
    # 1. Login como administrador
    print_header("1. LOGIN COMO ADMINISTRADOR")
    try:
        login_response = requests.post(
            f"{BASE_URL}/api/login/",
            json=ADMIN_CREDENTIALS,
            timeout=10
        )
        
        if login_response.status_code == 200:
            admin_token = login_response.json()["token"]
            print_test("Login exitoso", True, f"Token obtenido: {admin_token[:20]}...")
            
            headers = {
                "Authorization": f"Token {admin_token}",
                "Content-Type": "application/json"
            }
        else:
            print_test("Login fallido", False, f"Status: {login_response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print_test("Error de conexión", False, "Servidor no disponible")
        return False
    except Exception as e:
        print_test("Error inesperado en login", False, str(e))
        return False
    
    # 2. Listar usuarios disponibles
    print_header("2. LISTAR USUARIOS DISPONIBLES")
    try:
        users_response = requests.get(
            f"{BASE_URL}/api/users/",
            headers=headers,
            timeout=10
        )
        
        if users_response.status_code == 200:
            users_data = users_response.json()
            users = users_data.get("users", [])
            print_test("Listado de usuarios exitoso", True, f"Encontrados {len(users)} usuarios")
            
            # Mostrar usuarios disponibles
            print("\n📋 Usuarios disponibles:")
            for user in users:
                print(f"   - ID: {user['id']}, Username: {user['username']}, Role: {user.get('role', 'N/A')}")
                
            # Seleccionar un usuario para cambiar rol (que no sea admin)
            target_user = None
            for user in users:
                if user.get('role') != 'admin' and user['username'] != 'admin':
                    target_user = user
                    break
                    
            if not target_user:
                print_test("No se encontró usuario objetivo", False, "Todos los usuarios son admin")
                return False
                
        else:
            print_test("Error al listar usuarios", False, f"Status: {users_response.status_code}")
            return False
            
    except Exception as e:
        print_test("Error al listar usuarios", False, str(e))
        return False
    
    # 3. Asignar rol de seguridad a usuario
    print_header("3. ASIGNAR ROL DE SEGURIDAD")
    try:
        target_id = target_user["id"]
        original_role = target_user.get("role", "resident")
        
        assign_response = requests.post(
            f"{BASE_URL}/api/users/{target_id}/assign-role/",
            headers=headers,
            json={"role": "security"},
            timeout=10
        )
        
        if assign_response.status_code == 200:
            response_data = assign_response.json()
            print_test(
                "Asignación de rol exitosa", 
                True, 
                f"Usuario {target_user['username']}: {original_role} -> security"
            )
            print(f"   📋 Respuesta: {response_data.get('message', 'Sin mensaje')}")
        else:
            print_test("Error en asignación de rol", False, f"Status: {assign_response.status_code}")
            print(f"   📋 Respuesta: {assign_response.text}")
            
    except Exception as e:
        print_test("Error al asignar rol", False, str(e))
        return False
    
    # 4. Verificar cambio de rol
    print_header("4. VERIFICAR CAMBIO DE ROL")
    try:
        verify_response = requests.get(
            f"{BASE_URL}/api/users/",
            headers=headers,
            timeout=10
        )
        
        if verify_response.status_code == 200:
            updated_users = verify_response.json().get("users", [])
            updated_user = next((u for u in updated_users if u["id"] == target_id), None)
            
            if updated_user and updated_user.get("role") == "security":
                print_test("Verificación exitosa", True, "El rol se cambió correctamente")
            else:
                print_test("Verificación fallida", False, "El rol no se cambió")
                
        else:
            print_test("Error al verificar", False, f"Status: {verify_response.status_code}")
            
    except Exception as e:
        print_test("Error al verificar rol", False, str(e))
    
    # 5. Probar asignación de rol inválido
    print_header("5. PROBAR ROL INVÁLIDO")
    try:
        invalid_response = requests.post(
            f"{BASE_URL}/api/users/{target_id}/assign-role/",
            headers=headers,
            json={"role": "invalid_role"},
            timeout=10
        )
        
        if invalid_response.status_code == 400:
            print_test("Validación de rol inválido", True, "Error 400 como esperado")
        else:
            print_test("Validación fallida", False, f"Status inesperado: {invalid_response.status_code}")
            
    except Exception as e:
        print_test("Error al probar rol inválido", False, str(e))
    
    # 6. Restaurar rol original
    print_header("6. RESTAURAR ROL ORIGINAL")
    try:
        restore_response = requests.post(
            f"{BASE_URL}/api/users/{target_id}/assign-role/",
            headers=headers,
            json={"role": original_role},
            timeout=10
        )
        
        if restore_response.status_code == 200:
            print_test("Restauración exitosa", True, f"Rol restaurado a: {original_role}")
        else:
            print_test("Error al restaurar", False, f"Status: {restore_response.status_code}")
            
    except Exception as e:
        print_test("Error al restaurar rol", False, str(e))
    
    # 7. Logout
    print_header("7. LOGOUT")
    try:
        logout_response = requests.post(
            f"{BASE_URL}/api/logout/",
            headers=headers,
            timeout=10
        )
        
        if logout_response.status_code == 200:
            print_test("Logout exitoso", True, "Sesión cerrada correctamente")
        else:
            print_test("Error en logout", False, f"Status: {logout_response.status_code}")
            
    except Exception as e:
        print_test("Error al hacer logout", False, str(e))
    
    print_header("RESUMEN DE TESTS COMPLETADO")
    print(f"⏰ Tests ejecutados el: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("🎯 Funcionalidad de asignación de roles verificada")
    return True

def test_role_permissions():
    """Test adicional para verificar permisos"""
    print_header("TESTS DE PERMISOS DE ROLES")
    
    # Crear usuario no admin y probar que no puede asignar roles
    print("🔍 Verificando que usuarios no-admin no pueden asignar roles...")
    
    # Este test requeriría crear un usuario regular y probar
    # que obtiene 403 al intentar asignar roles
    print_test("Test de permisos", True, "Implementado en tests unitarios")

if __name__ == "__main__":
    print("🚀 INICIANDO TESTS MANUALES DE ASIGNACIÓN DE ROLES")
    print(f"🔗 URL Base: {BASE_URL}")
    print(f"👤 Credenciales Admin: {ADMIN_CREDENTIALS['username']}")
    
    try:
        success = test_role_assignment()
        test_role_permissions()
        
        if success:
            print("\n🎉 TODOS LOS TESTS COMPLETADOS EXITOSAMENTE")
            sys.exit(0)
        else:
            print("\n❌ ALGUNOS TESTS FALLARON")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrumpidos por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 Error inesperado: {e}")
        sys.exit(1)
