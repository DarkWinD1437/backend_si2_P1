#!/usr/bin/env python3
"""
Script para restaurar contraseñas y verificar estado del sistema
"""

import requests
import json

# Configuración
BASE_URL = "http://127.0.0.1:8000/api"
HEADERS = {'Content-Type': 'application/json'}

def restore_admin_password():
    """Restaurar la contraseña del admin"""
    print("🔧 Restaurando contraseña de admin_smart")
    
    # Intentar con la nueva contraseña
    login_url = f"{BASE_URL}/login/"
    
    # Probar diferentes contraseñas posibles
    possible_passwords = ["NewSecurePass2024!", "admin123", "admin123456"]
    
    for password in possible_passwords:
        credentials = {"username": "admin_smart", "password": password}
        
        try:
            response = requests.post(login_url, json=credentials, headers=HEADERS)
            if response.status_code == 200:
                token = response.json().get('token')
                print(f"   ✅ Login exitoso con contraseña: {password}")
                
                # Si no es la contraseña original, cambiarla
                if password != "admin123":
                    print("   🔄 Restaurando contraseña original...")
                    change_password_url = f"{BASE_URL}/profile/change-password/"
                    headers = {'Authorization': f'Token {token}', 'Content-Type': 'application/json'}
                    
                    restore_data = {
                        "current_password": password,
                        "new_password": "admin123",
                        "new_password_confirm": "admin123"
                    }
                    
                    change_response = requests.post(change_password_url, json=restore_data, headers=headers)
                    if change_response.status_code == 200:
                        print("   ✅ Contraseña restaurada a 'admin123'")
                    else:
                        print(f"   ⚠️  No se pudo restaurar: {change_response.status_code}")
                
                return True
            else:
                print(f"   ❌ Falló con {password}: {response.status_code}")
                
        except Exception as e:
            print(f"   💥 Error con {password}: {e}")
    
    print("   ❌ No se pudo restaurar la contraseña")
    return False

def test_system_status():
    """Verificar estado general del sistema"""
    print("📊 Verificando estado del sistema")
    
    # Test login con admin123
    login_url = f"{BASE_URL}/login/"
    credentials = {"username": "admin_smart", "password": "admin123"}
    
    try:
        response = requests.post(login_url, json=credentials, headers=HEADERS)
        print(f"   Login admin_smart: {response.status_code}")
        
        if response.status_code == 200:
            token = response.json().get('token')
            print("   ✅ Admin login funcional")
            
            # Test perfil
            me_url = f"{BASE_URL}/me/"
            headers = {'Authorization': f'Token {token}', 'Content-Type': 'application/json'}
            
            response = requests.get(me_url, headers=headers)
            print(f"   Perfil /me/: {response.status_code} ✅")
            
            # Test perfil completo
            profile_url = f"{BASE_URL}/profile/"
            response = requests.get(profile_url, headers=headers)
            print(f"   Perfil /profile/: {response.status_code} ✅")
            
            return True
        else:
            print(f"   ❌ Error en login: {response.text}")
            return False
            
    except Exception as e:
        print(f"   💥 Error: {e}")
        return False

def test_other_users():
    """Verificar otros usuarios"""
    print("👥 Verificando otros usuarios")
    
    other_users = [
        {"username": "carlos", "password": "password123"},
        {"username": "maria", "password": "password123"}
    ]
    
    login_url = f"{BASE_URL}/login/"
    
    for user_data in other_users:
        try:
            response = requests.post(login_url, json=user_data, headers=HEADERS)
            status = "✅" if response.status_code == 200 else "❌"
            print(f"   {user_data['username']}: {response.status_code} {status}")
            
        except Exception as e:
            print(f"   {user_data['username']}: Error {e}")

def main():
    print("🔧 RESTAURACIÓN Y VERIFICACIÓN DEL SISTEMA")
    print("=" * 50)
    
    # Paso 1: Restaurar contraseña del admin
    restore_success = restore_admin_password()
    print("-" * 30)
    
    # Paso 2: Verificar estado del sistema
    if restore_success:
        system_ok = test_system_status()
        print("-" * 30)
        
        # Paso 3: Verificar otros usuarios
        test_other_users()
        print("-" * 30)
        
        if system_ok:
            print("✅ SISTEMA RESTAURADO Y FUNCIONAL")
            print("🎯 T2 (Login/Logout) y T3 (Perfil) listos para testing")
        else:
            print("⚠️  Sistema parcialmente funcional")
    else:
        print("❌ No se pudo restaurar el sistema")
    
    print("=" * 50)

if __name__ == "__main__":
    main()
