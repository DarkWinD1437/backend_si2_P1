"""
Test individual: Permisos de Mantenimiento
Módulo 7: Gestión de Mantenimiento

Ejecutar con: python test_permisos.py
"""

import requests
import json

# Configuración
BASE_URL = 'http://127.0.0.1:8000'

# Credenciales de test
ADMIN_USER = {'username': 'admin', 'password': 'clave123'}
RESIDENT_USER = {'username': 'prueba', 'password': 'clave123'}
MAINTENANCE_USER = {'username': 'prueba2', 'password': 'clave123'}
SECURITY_USER = {'username': 'prueba3', 'password': 'clave123'}

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

def test_admin_acceso_completo():
    """Test: Admin tiene acceso completo"""
    print("\n👑 Test: Admin - Acceso Completo")

    token = login_user(ADMIN_USER)
    if not token:
        return False

    # Puede listar solicitudes
    response = requests.get(
        f"{BASE_URL}/api/maintenance/solicitudes/",
        headers=get_auth_headers(token)
    )

    if response.status_code != 200:
        print(f"   ❌ Admin no puede listar solicitudes: {response.status_code}")
        return False

    # Puede listar tareas
    response = requests.get(
        f"{BASE_URL}/api/maintenance/tareas/",
        headers=get_auth_headers(token)
    )

    if response.status_code != 200:
        print(f"   ❌ Admin no puede listar tareas: {response.status_code}")
        return False

    print("   ✅ Admin tiene acceso completo")
    return True

def test_residente_crear_solicitud():
    """Test: Residente puede crear solicitudes"""
    print("\n🏠 Test: Residente - Crear Solicitud")

    token = login_user(RESIDENT_USER)
    if not token:
        return False

    data = {
        "descripcion": "Test de permisos - residente",
        "ubicacion": "Area de test",
        "prioridad": "baja"
    }

    response = requests.post(
        f"{BASE_URL}/api/maintenance/solicitudes/",
        json=data,
        headers=get_auth_headers(token)
    )

    if response.status_code == 201:
        print("   ✅ Residente puede crear solicitudes")
        solicitud = response.json()
        return solicitud['id']
    else:
        print(f"   ❌ Residente no puede crear solicitudes: {response.status_code}")
        return None

def test_residente_ver_sus_solicitudes(solicitud_id):
    """Test: Residente puede ver sus propias solicitudes"""
    print(f"\n👀 Test: Residente - Ver Solicitud Propia {solicitud_id}")

    token = login_user(RESIDENT_USER)
    if not token:
        return False

    response = requests.get(
        f"{BASE_URL}/api/maintenance/solicitudes/{solicitud_id}/",
        headers=get_auth_headers(token)
    )

    if response.status_code == 200:
        print("   ✅ Residente puede ver su propia solicitud")
        return True
    else:
        print(f"   ❌ Residente no puede ver su solicitud: {response.status_code}")
        return False

def test_residente_no_puede_asignar():
    """Test: Residente NO puede asignar tareas"""
    print("\n🚫 Test: Residente - No Puede Asignar Tareas")

    token = login_user(RESIDENT_USER)
    if not token:
        return False

    # Crear solicitud primero
    data_solicitud = {
        "descripcion": "Test asignacion residente",
        "ubicacion": "Test",
        "prioridad": "baja"
    }

    response = requests.post(
        f"{BASE_URL}/api/maintenance/solicitudes/",
        json=data_solicitud,
        headers=get_auth_headers(token)
    )

    if response.status_code != 201:
        print("   ❌ No se pudo crear solicitud para test")
        return False

    solicitud_id = response.json()['id']

    # Intentar asignar tarea
    data_tarea = {
        "asignado_a_id": 2,
        "descripcion_tarea": "Test",
        "notas": "Test"
    }

    response = requests.post(
        f"{BASE_URL}/api/maintenance/solicitudes/{solicitud_id}/asignar_tarea/",
        json=data_tarea,
        headers=get_auth_headers(token)
    )

    if response.status_code == 403:
        print("   ✅ Residente correctamente rechazado al asignar tarea")
        return True
    else:
        print(f"   ❌ Residente pudo asignar tarea (esperado 403): {response.status_code}")
        return False

def test_mantenimiento_asignar_tarea():
    """Test: Mantenimiento puede asignar tareas"""
    print("\n🔧 Test: Mantenimiento - Asignar Tarea")

    # Crear solicitud como residente
    resident_token = login_user(RESIDENT_USER)
    if not resident_token:
        return False

    data_solicitud = {
        "descripcion": "Test asignacion mantenimiento",
        "ubicacion": "Test",
        "prioridad": "baja"
    }

    response = requests.post(
        f"{BASE_URL}/api/maintenance/solicitudes/",
        json=data_solicitud,
        headers=get_auth_headers(resident_token)
    )

    if response.status_code != 201:
        print("   ❌ No se pudo crear solicitud")
        return False

    solicitud_id = response.json()['id']

    # Asignar como mantenimiento
    maintenance_token = login_user(MAINTENANCE_USER)
    if not maintenance_token:
        return False

    data_tarea = {
        "asignado_a_id": 2,  # Asumiendo que el usuario de mantenimiento tiene ID 2
        "descripcion_tarea": "Test asignacion por mantenimiento",
        "notas": "Test"
    }

    response = requests.post(
        f"{BASE_URL}/api/maintenance/solicitudes/{solicitud_id}/asignar_tarea/",
        json=data_tarea,
        headers=get_auth_headers(maintenance_token)
    )

    if response.status_code == 201:
        print("   ✅ Mantenimiento puede asignar tareas")
        tarea = response.json()
        return tarea['id']
    else:
        print(f"   ❌ Mantenimiento no puede asignar tareas: {response.status_code}")
        return None

def test_mantenimiento_actualizar_su_tarea(tarea_id):
    """Test: Mantenimiento puede actualizar sus tareas asignadas"""
    print(f"\n📝 Test: Mantenimiento - Actualizar Tarea Asignada {tarea_id}")

    token = login_user(MAINTENANCE_USER)
    if not token:
        return False

    data = {
        "estado": "en_progreso",
        "notas": "Actualizando tarea asignada"
    }

    response = requests.post(
        f"{BASE_URL}/api/maintenance/tareas/{tarea_id}/actualizar_estado/",
        json=data,
        headers=get_auth_headers(token)
    )

    if response.status_code == 200:
        print("   ✅ Mantenimiento puede actualizar su tarea asignada")
        return True
    else:
        print(f"   ❌ Mantenimiento no puede actualizar tarea: {response.status_code}")
        return False

def test_seguridad_solo_lectura():
    """Test: Seguridad tiene solo acceso de lectura"""
    print("\n👮 Test: Seguridad - Solo Lectura")

    token = login_user(SECURITY_USER)
    if not token:
        return False

    # Puede leer solicitudes
    response = requests.get(
        f"{BASE_URL}/api/maintenance/solicitudes/",
        headers=get_auth_headers(token)
    )

    if response.status_code != 200:
        print(f"   ❌ Seguridad no puede leer solicitudes: {response.status_code}")
        return False

    # Puede leer tareas
    response = requests.get(
        f"{BASE_URL}/api/maintenance/tareas/",
        headers=get_auth_headers(token)
    )

    if response.status_code != 200:
        print(f"   ❌ Seguridad no puede leer tareas: {response.status_code}")
        return False

    # NO puede crear solicitudes
    data = {
        "descripcion": "Test seguridad",
        "ubicacion": "Test",
        "prioridad": "baja"
    }

    response = requests.post(
        f"{BASE_URL}/api/maintenance/solicitudes/",
        json=data,
        headers=get_auth_headers(token)
    )

    if response.status_code == 403:
        print("   ✅ Seguridad correctamente limitado a solo lectura")
        return True
    else:
        print(f"   ❌ Seguridad pudo crear solicitud (esperado 403): {response.status_code}")
        return False

def test_sin_autenticacion():
    """Test: Sin autenticación debe ser rechazado"""
    print("\n🔒 Test: Sin Autenticación")

    # Intentar acceder sin token
    response = requests.get(
        f"{BASE_URL}/api/maintenance/solicitudes/",
        headers={'Content-Type': 'application/json'}
    )

    if response.status_code == 401:
        print("   ✅ Correctamente rechazado sin autenticación")
        return True
    else:
        print(f"   ❌ Acceso permitido sin auth (esperado 401): {response.status_code}")
        return False

def main():
    """Función principal"""
    print("🧪 Tests de Permisos de Mantenimiento")
    print("=" * 50)

    resultados = []

    # Test 1: Admin acceso completo
    resultados.append(test_admin_acceso_completo())

    # Test 2: Residente crear solicitud
    solicitud_id = test_residente_crear_solicitud()
    resultados.append(solicitud_id is not None)

    # Test 3: Residente ver sus solicitudes
    if solicitud_id:
        resultados.append(test_residente_ver_sus_solicitudes(solicitud_id))

    # Test 4: Residente no puede asignar
    resultados.append(test_residente_no_puede_asignar())

    # Test 5: Mantenimiento asignar tarea
    tarea_id = test_mantenimiento_asignar_tarea()
    resultados.append(tarea_id is not None)

    # Test 6: Mantenimiento actualizar su tarea
    if tarea_id:
        resultados.append(test_mantenimiento_actualizar_su_tarea(tarea_id))

    # Test 7: Seguridad solo lectura
    resultados.append(test_seguridad_solo_lectura())

    # Test 8: Sin autenticación
    resultados.append(test_sin_autenticacion())

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
        print("\n🎉 TODOS LOS TESTS DE PERMISOS PASARON!")
        return True
    else:
        print(f"\n⚠️  {total - exitosos} tests fallaron")
        return False

if __name__ == "__main__":
    main()
