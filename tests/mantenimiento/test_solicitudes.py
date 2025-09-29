"""
Test individual: Solicitudes de Manteni    print("Test: Crear Solicitud de Mantenimiento")iento
Módulo 7: Gestión de Mantenimiento

Ejecutar con: python test_solicitudes.py
"""

import requests
import json
from datetime import datetime

# Configuración
BASE_URL = 'http://127.0.0.1:8000'

# Credenciales de test
ADMIN_USER = {'username': 'admin', 'password': 'clave123'}
RESIDENT_USER = {'username': 'prueba', 'password': 'clave123'}

def get_auth_headers(token):
    """Retorna headers con token de autenticación"""
    return {
        'Authorization': f'Token {token}',
        'Content-Type': 'application/json'
    }

def login_user(user_data):
    """Login de usuario y retorno de token"""
    print(f"🔑 Login de {user_data['username']}...")
    response = requests.post(
        f'{BASE_URL}/api/auth-token/',
        json=user_data,
        headers={'Content-Type': 'application/json'}
    )

    if response.status_code == 200:
        token = response.json()['token']
        print("   ✅ Login exitoso")
        return token
    else:
        print(f"   ❌ Error: {response.text}")
        return None

def test_crear_solicitud():
    """Test: POST /api/maintenance/solicitudes/"""
    print("\n🏗️  Test: Crear Solicitud de Mantenimiento")

    token = login_user(RESIDENT_USER)
    if not token:
        print("❌ No se pudo hacer login")
        return None

    data = {
        "descripcion": "La luz del pasillo del piso 3 no funciona correctamente",
        "ubicacion": "Pasillo piso 3, cerca del ascensor",
        "prioridad": "media"
    }

    response = requests.post(
        f"{BASE_URL}/api/maintenance/solicitudes/",
        json=data,
        headers=get_auth_headers(token)
    )

    print(f"   Status: {response.status_code}")

    if response.status_code == 201:
        solicitud = response.json()
        print("   ✅ Solicitud creada exitosamente")
        print(f"      ID: {solicitud['id']}")
        print(f"      Estado: {solicitud['estado']}")
        print(f"      Prioridad: {solicitud['prioridad']}")

        # Validaciones
        assert solicitud['estado'] == 'pendiente'
        assert solicitud['prioridad'] == 'media'
        assert 'descripcion' in solicitud
        assert 'ubicacion' in solicitud
        assert 'fecha_solicitud' in solicitud

        return solicitud['id']
    else:
        print(f"   ❌ Error: {response.text}")
        return None

def test_listar_solicitudes():
    """Test: GET /api/maintenance/solicitudes/"""
    print("\n📋 Test: Listar Solicitudes de Mantenimiento")

    token = login_user(ADMIN_USER)
    if not token:
        print("❌ No se pudo hacer login")
        return False

    response = requests.get(
        f"{BASE_URL}/api/maintenance/solicitudes/",
        headers=get_auth_headers(token)
    )

    print(f"   Status: {response.status_code}")

    if response.status_code == 200:
        solicitudes = response.json()
        print(f"   ✅ Lista obtenida ({len(solicitudes)} solicitudes)")

        if solicitudes:
            primera = solicitudes[0]
            print(f"      Primera solicitud ID: {primera['id']}")
            print(f"      Estado: {primera['estado']}")

            # Validaciones
            assert isinstance(solicitudes, list)
            assert 'id' in primera
            assert 'estado' in primera
            assert 'prioridad' in primera

        return True
    else:
        print(f"   ❌ Error: {response.text}")
        return False

def test_filtrar_solicitudes():
    """Test: GET /api/maintenance/solicitudes/?estado=pendiente"""
    print("\n🔍 Test: Filtrar Solicitudes por Estado")

    token = login_user(ADMIN_USER)
    if not token:
        print("❌ No se pudo hacer login")
        return False

    params = {'estado': 'pendiente'}

    response = requests.get(
        f"{BASE_URL}/api/maintenance/solicitudes/",
        params=params,
        headers=get_auth_headers(token)
    )

    print(f"   Status: {response.status_code}")

    if response.status_code == 200:
        solicitudes = response.json()
        print(f"   ✅ Filtro aplicado ({len(solicitudes)} solicitudes pendientes)")

        # Validar que todas las solicitudes filtradas tienen el estado correcto
        for solicitud in solicitudes:
            assert solicitud['estado'] == 'pendiente', f"Solicitud {solicitud['id']} no tiene estado 'pendiente'"

        print("   ✅ Todas las solicitudes filtradas correctamente")
        return True
    else:
        print(f"   ❌ Error: {response.text}")
        return False

def test_detalle_solicitud(solicitud_id):
    """Test: GET /api/maintenance/solicitudes/{id}/"""
    print(f"\n📄 Test: Detalle de Solicitud {solicitud_id}")

    token = login_user(ADMIN_USER)
    if not token:
        print("❌ No se pudo hacer login")
        return False

    response = requests.get(
        f"{BASE_URL}/api/maintenance/solicitudes/{solicitud_id}/",
        headers=get_auth_headers(token)
    )

    print(f"   Status: {response.status_code}")

    if response.status_code == 200:
        solicitud = response.json()
        print("   ✅ Detalle obtenido")
        print(f"      ID: {solicitud['id']}")
        print(f"      Descripción: {solicitud['descripcion'][:50]}...")
        print(f"      Estado: {solicitud['estado']}")

        # Validaciones
        assert solicitud['id'] == solicitud_id
        assert 'descripcion' in solicitud
        assert 'ubicacion' in solicitud
        assert 'estado' in solicitud
        assert 'prioridad' in solicitud
        assert 'solicitante_info' in solicitud

        return True
    else:
        print(f"   ❌ Error: {response.text}")
        return False

def test_solicitud_sin_autenticacion():
    """Test: Acceso sin autenticación debe fallar"""
    print("\n🚫 Test: Solicitud sin Autenticación")

    data = {
        "descripcion": "Test sin auth",
        "ubicacion": "Test",
        "prioridad": "baja"
    }

    response = requests.post(
        f"{BASE_URL}/api/maintenance/solicitudes/",
        json=data,
        headers={'Content-Type': 'application/json'}
    )

    print(f"   Status: {response.status_code}")

    if response.status_code == 401:
        print("   ✅ Correctamente rechazado sin autenticación")
        return True
    else:
        print(f"   ❌ Error: Se esperaba 401, se obtuvo {response.status_code}")
        return False

def test_datos_invalidos():
    """Test: Crear solicitud con datos inválidos"""
    print("\n❌ Test: Datos Inválidos en Solicitud")

    token = login_user(RESIDENT_USER)
    if not token:
        return False

    # Datos incompletos
    data = {
        "descripcion": "Test",
        # Falta ubicacion y prioridad
    }

    response = requests.post(
        f"{BASE_URL}/api/maintenance/solicitudes/",
        json=data,
        headers=get_auth_headers(token)
    )

    print(f"   Status: {response.status_code}")

    if response.status_code == 400:
        print("   ✅ Correctamente rechazado por datos inválidos")
        return True
    else:
        print(f"   ❌ Error: Se esperaba 400, se obtuvo {response.status_code}")
        print(f"      Respuesta: {response.text}")
        return False

def main():
    """Función principal"""
    print("Tests de Solicitudes de Mantenimiento")
    print("=" * 50)

    resultados = []

    # Test 1: Crear solicitud
    solicitud_id = test_crear_solicitud()
    resultados.append(solicitud_id is not None)

    # Test 2: Listar solicitudes
    resultados.append(test_listar_solicitudes())

    # Test 3: Filtrar solicitudes
    resultados.append(test_filtrar_solicitudes())

    # Test 4: Detalle de solicitud (si se creó una)
    if solicitud_id:
        resultados.append(test_detalle_solicitud(solicitud_id))

    # Test 5: Sin autenticación
    resultados.append(test_solicitud_sin_autenticacion())

    # Test 6: Datos inválidos
    resultados.append(test_datos_invalidos())

    # Resultados finales
    print("\n" + "=" * 50)
    print("📊 RESULTADOS FINALES")
    print("=" * 50)

    exitosos = sum(resultados)
    total = len(resultados)

    print(f"Tests exitosos: {exitosos}/{total}")

    for i, resultado in enumerate(resultados, 1):
        status = "✅" if resultado else "❌"
        print(f"  Test {i}: {status}")

    if exitosos == total:
        print("\n🎉 TODOS LOS TESTS PASARON!")
        return True
    else:
        print(f"\n⚠️  {total - exitosos} tests fallaron")
        return False

if __name__ == "__main__":
    main()
