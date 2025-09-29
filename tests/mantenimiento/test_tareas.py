"""
Test individual: Tareas de Mantenimiento
Módulo 7: Gestión de Mantenimiento

Ejecutar con: python test_tareas.py
"""

import requests
import json

# Configuración
BASE_URL = 'http://127.0.0.1:8000'

# Credenciales de test
ADMIN_USER = {'username': 'admin', 'password': 'clave123'}
MAINTENANCE_USER = {'username': 'prueba2', 'password': 'clave123'}

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

def crear_solicitud_test():
    """Crear una solicitud de test para usar en los tests"""
    from test_solicitudes import login_user as login_resident, get_auth_headers as get_headers, RESIDENT_USER

    token = login_resident(RESIDENT_USER)
    if not token:
        return None

    data = {
        "descripcion": "Solicitud de test para tareas",
        "ubicacion": "Area de test",
        "prioridad": "baja"
    }

    response = requests.post(
        f"{BASE_URL}/api/maintenance/solicitudes/",
        json=data,
        headers=get_headers(token)
    )

    if response.status_code == 201:
        return response.json()['id']
    return None

def test_asignar_tarea():
    """Test: POST /api/maintenance/solicitudes/{id}/asignar_tarea/"""
    print("\n👷 Test: Asignar Tarea de Mantenimiento")

    # Crear solicitud primero
    solicitud_id = crear_solicitud_test()
    if not solicitud_id:
        print("❌ No se pudo crear solicitud de test")
        return None

    # Login como admin
    token = login_user(ADMIN_USER)
    if not token:
        print("❌ No se pudo hacer login como admin")
        return None

    data = {
        "asignado_a_id": 1,  # ID del admin para testing
        "descripcion_tarea": "Revisar y reparar el problema reportado",
        "notas": "Verificar todos los componentes"
    }

    response = requests.post(
        f"{BASE_URL}/api/maintenance/solicitudes/{solicitud_id}/asignar_tarea/",
        json=data,
        headers=get_auth_headers(token)
    )

    print(f"   Status: {response.status_code}")

    if response.status_code == 201:
        tarea = response.json()
        print("   ✅ Tarea asignada exitosamente")
        print(f"      ID Tarea: {tarea['id']}")
        print(f"      ID Solicitud: {tarea['solicitud_info']['id']}")
        print(f"      Asignado a: {tarea['asignado_a_info']['username']}")
        print(f"      Estado: {tarea['estado']}")

        # Validaciones
        assert tarea['estado'] == 'asignada'
        assert tarea['solicitud_info']['id'] == solicitud_id
        assert 'descripcion_tarea' in tarea
        assert 'fecha_asignacion' in tarea

        return tarea['id']
    else:
        print(f"   ❌ Error: {response.text}")
        return None

def test_listar_tareas():
    """Test: GET /api/maintenance/tareas/"""
    print("\n📋 Test: Listar Tareas de Mantenimiento")

    token = login_user(ADMIN_USER)
    if not token:
        print("❌ No se pudo hacer login")
        return False

    response = requests.get(
        f"{BASE_URL}/api/maintenance/tareas/",
        headers=get_auth_headers(token)
    )

    print(f"   Status: {response.status_code}")

    if response.status_code == 200:
        tareas = response.json()
        print(f"   ✅ Lista obtenida ({len(tareas)} tareas)")

        if tareas:
            primera = tareas[0]
            print(f"      Primera tarea ID: {primera['id']}")
            print(f"      Estado: {primera['estado']}")

            # Validaciones
            assert isinstance(tareas, list)
            assert 'id' in primera
            assert 'estado' in primera
            assert 'solicitud_info' in primera

        return True
    else:
        print(f"   ❌ Error: {response.text}")
        return False

def test_actualizar_estado_tarea(tarea_id):
    """Test: POST /api/maintenance/tareas/{id}/actualizar_estado/"""
    print(f"\n📊 Test: Actualizar Estado de Tarea {tarea_id}")

    token = login_user(ADMIN_USER)  # Usar admin para testing
    if not token:
        print("❌ No se pudo hacer login como admin")
        return False

    data = {
        "estado": "en_progreso",
        "notas": "Iniciando trabajo en el problema reportado"
    }

    response = requests.post(
        f"{BASE_URL}/api/maintenance/tareas/{tarea_id}/actualizar_estado/",
        json=data,
        headers=get_auth_headers(token)
    )

    print(f"   Status: {response.status_code}")

    if response.status_code == 200:
        tarea = response.json()
        print("   ✅ Estado de tarea actualizado")
        print(f"      Nuevo estado: {tarea['estado']}")
        print(f"      Notas agregadas: {data['notas'] in tarea['notas']}")

        # Validaciones
        assert tarea['estado'] == 'en_progreso'
        assert data['notas'] in tarea['notas']

        return True
    else:
        print(f"   ❌ Error: {response.text}")
        return False

def test_completar_tarea(tarea_id):
    """Test: Completar tarea"""
    print(f"\n✅ Test: Completar Tarea {tarea_id}")

    token = login_user(ADMIN_USER)  # Usar admin para testing
    if not token:
        return False

    data = {
        "estado": "completada",
        "notas": "Trabajo completado satisfactoriamente"
    }

    response = requests.post(
        f"{BASE_URL}/api/maintenance/tareas/{tarea_id}/actualizar_estado/",
        json=data,
        headers=get_auth_headers(token)
    )

    print(f"   Status: {response.status_code}")

    if response.status_code == 200:
        tarea = response.json()
        print("   ✅ Tarea completada")
        print(f"      Estado final: {tarea['estado']}")
        print(f"      Fecha completado: {tarea['fecha_completado']}")

        # Validaciones
        assert tarea['estado'] == 'completada'
        assert tarea['fecha_completado'] is not None

        return True
    else:
        print(f"   ❌ Error: {response.text}")
        return False

def main():
    """Función principal"""
    print("🧪 Tests de Tareas de Mantenimiento")
    print("=" * 50)

    resultados = []

    # Test 1: Asignar tarea
    tarea_id = test_asignar_tarea()
    resultados.append(tarea_id is not None)

    # Test 2: Listar tareas
    resultados.append(test_listar_tareas())

    # Test 3: Actualizar estado (si se asignó tarea)
    if tarea_id:
        resultados.append(test_actualizar_estado_tarea(tarea_id))

        # Test 4: Completar tarea
        resultados.append(test_completar_tarea(tarea_id))

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
