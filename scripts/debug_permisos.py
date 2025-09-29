"""
Script de debugging para verificar roles y permisos
"""

import requests
import json

BASE_URL = 'http://127.0.0.1:8000'
RESIDENT_USER = {'username': 'prueba2', 'password': 'clave123'}

# 1. Login del residente
print("🔍 DEBUGGING - Verificando rol y permisos del residente")
print("="*60)

response = requests.post(
    f'{BASE_URL}/api/auth-token/',
    json=RESIDENT_USER,
    headers={'Content-Type': 'application/json'}
)

if response.status_code == 200:
    token = response.json().get('token')
    print(f"✅ Login exitoso - Token: {token[:20]}...")
    
    # 2. Probar consultar admin sin parámetro residente
    print("\n🧪 Probando sin parámetro residente (debería mostrar solo su estado):")
    headers = {'Authorization': f'Token {token}', 'Content-Type': 'application/json'}
    
    response = requests.get(
        f'{BASE_URL}/api/finances/cargos/estado_cuenta/',
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Usuario consultado: {data['residente_info']['username']}")
    else:
        print(f"Error: {response.text}")
    
    # 3. Probar con parámetro residente=1 (admin)
    print("\n🧪 Probando con parámetro residente=1 (debería dar 403):")
    response = requests.get(
        f'{BASE_URL}/api/finances/cargos/estado_cuenta/?residente=1',
        headers=headers
    )
    
    print(f"Status: {response.status_code}")
    if response.status_code == 403:
        print("✅ Correcto: 403 Forbidden")
    else:
        print(f"❌ Error: Se esperaba 403, obtuvo {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Usuario consultado: {data['residente_info']['username']}")
        else:
            print(f"Respuesta: {response.text}")
    
    # 4. Verificar información del usuario actual
    print("\n🔍 Verificando información del usuario actual:")
    response = requests.get(
        f'{BASE_URL}/api/users/profile/',
        headers=headers
    )
    
    if response.status_code == 200:
        profile = response.json()
        print(f"ID: {profile.get('id', 'N/A')}")
        print(f"Username: {profile.get('username', 'N/A')}")
        print(f"Role: {profile.get('role', 'N/A')}")
        print(f"Is superuser: {profile.get('is_superuser', 'N/A')}")
    else:
        print(f"Error obteniendo perfil: {response.text}")
        
else:
    print(f"❌ Error en login: {response.text}")