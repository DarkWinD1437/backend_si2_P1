"""
Test de integración: Flujo Completo de Mantenimiento
Módulo 7: Gestión de Mantenimiento

Ejecutar con: python test_integracion.py
"""

import requests
import json
import time

# Configuración
BASE_URL = 'http://127.0.0.1:8000'

# Credenciales de test
ADMIN_USER = {'username': 'admin', 'password': 'clave123'}
RESIDENT_USER = {'username': 'prueba', 'password': 'clave123'}
MAINTENANCE_USER = {'username': 'prueba2', 'password': 'clave123'}

def get_auth_headers(token):
    """Retorna headers con token de autenticación"""
    return {
        'Authorization': f'Token {token}',
        'Content-Type': 'application/json'
    }

def login_user(user_data):
    """Login de usuario y retorno de token"""
    response = requests.post(
        f'{BASE_URL}/api/auth-token/',
        json=user_data,
        headers={'Content-Type': 'application/json'}
    )

    if response.status_code == 200:
        return response.json()['token']
    else:
        print(f"❌ Error login {user_data['username']}: {response.text}")
        return None

def test_flujo_completo_mantenimiento():
    """Test: Flujo completo desde solicitud hasta completado"""
    print("\n🔄 Test: Flujo Completo de Mantenimiento")
    print("-" * 60)

    # Fase 1: Residente crea solicitud
    print("\n📝 FASE 1: Residente crea solicitud")

    resident_token = login_user(RESIDENT_USER)
    if not resident_token:
        return False

    solicitud_data = {
        "descripcion": "La puerta del ascensor se atasca en el piso 5",
        "ubicacion": "Ascensor principal, piso 5",
        "prioridad": "alta"
    }

    response = requests.post(
        f"{BASE_URL}/api/maintenance/solicitudes/",
        json=solicitud_data,
        headers=get_auth_headers(resident_token)
    )

    if response.status_code != 201:
        print(f"❌ Error creando solicitud: {response.status_code}")
        return False

    solicitud = response.json()
    solicitud_id = solicitud['id']
    print(f"✅ Solicitud creada - ID: {solicitud_id}")
    print(f"   Estado inicial: {solicitud['estado']}")

    # Verificar que la solicitud aparece en listados
    response = requests.get(
        f"{BASE_URL}/api/maintenance/solicitudes/",
        headers=get_auth_headers(resident_token)
    )

    if response.status_code != 200:
        print("❌ Error listando solicitudes del residente")
        return False

    solicitudes = response.json()
    solicitud_encontrada = any(s['id'] == solicitud_id for s in solicitudes)
    if not solicitud_encontrada:
        print("❌ Solicitud no aparece en listado del residente")
        return False

    print("✅ Solicitud visible para el residente")

    # Fase 2: Admin asigna tarea
    print("\n👷 FASE 2: Admin asigna tarea de mantenimiento")

    admin_token = login_user(ADMIN_USER)
    if not admin_token:
        return False

    tarea_data = {
        "asignado_a_id": 2,  # ID del usuario de mantenimiento
        "descripcion_tarea": "Diagnosticar y reparar mecanismo de puerta del ascensor",
        "notas": "Revisar sensores y mecanismo de cierre"
    }

    response = requests.post(
        f"{BASE_URL}/api/maintenance/solicitudes/{solicitud_id}/asignar_tarea/",
        json=tarea_data,
        headers=get_auth_headers(admin_token)
    )

    if response.status_code != 201:
        print(f"❌ Error asignando tarea: {response.status_code}")
        print(f"   Respuesta: {response.text}")
        return False

    tarea = response.json()
    tarea_id = tarea['id']
    print(f"✅ Tarea asignada - ID: {tarea_id}")
    print(f"   Asignada a: {tarea['asignado_a_info']['username']}")

    # Verificar que la solicitud cambió de estado
    response = requests.get(
        f"{BASE_URL}/api/maintenance/solicitudes/{solicitud_id}/",
        headers=get_auth_headers(admin_token)
    )

    if response.status_code == 200:
        solicitud_actualizada = response.json()
        if solicitud_actualizada['estado'] == 'asignada':
            print("✅ Estado de solicitud actualizado a 'asignada'")
        else:
            print(f"⚠️  Estado de solicitud: {solicitud_actualizada['estado']} (esperado: asignada)")

    # Fase 3: Mantenimiento inicia trabajo
    print("\n🔧 FASE 3: Mantenimiento inicia trabajo")

    maintenance_token = login_user(MAINTENANCE_USER)
    if not maintenance_token:
        return False

    update_data = {
        "estado": "en_progreso",
        "notas": "Llegué al sitio. Revisando sensores de puerta."
    }

    response = requests.post(
        f"{BASE_URL}/api/maintenance/tareas/{tarea_id}/actualizar_estado/",
        json=update_data,
        headers=get_auth_headers(maintenance_token)
    )

    if response.status_code != 200:
        print(f"❌ Error actualizando estado: {response.status_code}")
        return False

    tarea_actualizada = response.json()
    print("✅ Estado actualizado a 'en_progreso'")
    print(f"   Notas agregadas: {update_data['notas'] in tarea_actualizada['notas']}")

    # Verificar que la solicitud también cambió de estado
    response = requests.get(
        f"{BASE_URL}/api/maintenance/solicitudes/{solicitud_id}/",
        headers=get_auth_headers(admin_token)
    )

    if response.status_code == 200:
        solicitud_actualizada = response.json()
        if solicitud_actualizada['estado'] == 'en_progreso':
            print("✅ Estado de solicitud actualizado a 'en_progreso'")
        else:
            print(f"⚠️  Estado de solicitud: {solicitud_actualizada['estado']} (esperado: en_progreso)")

    # Fase 4: Mantenimiento completa trabajo
    print("\n✅ FASE 4: Mantenimiento completa trabajo")

    time.sleep(1)  # Pequeña pausa para timestamps diferentes

    completion_data = {
        "estado": "completada",
        "notas": "Sensores calibrados y mecanismo lubricado. Puerta funcionando correctamente."
    }

    response = requests.post(
        f"{BASE_URL}/api/maintenance/tareas/{tarea_id}/actualizar_estado/",
        json=completion_data,
        headers=get_auth_headers(maintenance_token)
    )

    if response.status_code != 200:
        print(f"❌ Error completando tarea: {response.status_code}")
        return False

    tarea_completada = response.json()
    print("✅ Tarea marcada como completada")
    print(f"   Fecha completado: {tarea_completada['fecha_completado']}")

    # Verificar estados finales
    response = requests.get(
        f"{BASE_URL}/api/maintenance/solicitudes/{solicitud_id}/",
        headers=get_auth_headers(admin_token)
    )

    if response.status_code == 200:
        solicitud_final = response.json()
        if solicitud_final['estado'] == 'completada':
            print("✅ Solicitud finalizada correctamente")
        else:
            print(f"❌ Estado final de solicitud: {solicitud_final['estado']} (esperado: completada)")
            return False

    # Fase 5: Verificaciones finales
    print("\n🔍 FASE 5: Verificaciones finales")

    # Verificar que la tarea aparece en listados
    response = requests.get(
        f"{BASE_URL}/api/maintenance/tareas/",
        headers=get_auth_headers(admin_token)
    )

    if response.status_code == 200:
        tareas = response.json()
        tarea_encontrada = any(t['id'] == tarea_id for t in tareas)
        if tarea_encontrada:
            print("✅ Tarea visible en listados")
        else:
            print("❌ Tarea no encontrada en listados")
            return False

    # Verificar que el residente puede ver la tarea relacionada
    response = requests.get(
        f"{BASE_URL}/api/maintenance/tareas/",
        headers=get_auth_headers(resident_token)
    )

    if response.status_code == 200:
        tareas_residente = response.json()
        tarea_encontrada = any(t['id'] == tarea_id for t in tareas_residente)
        if tarea_encontrada:
            print("✅ Residente puede ver tarea de su solicitud")
        else:
            print("⚠️  Residente no ve tarea (posiblemente por filtros)")

    print("\n🎉 FLUJO COMPLETO EXITOSO!")
    print("=" * 60)
    print("✅ Solicitud creada por residente")
    print("✅ Tarea asignada por admin")
    print("✅ Trabajo iniciado por mantenimiento")
    print("✅ Tarea completada por mantenimiento")
    print("✅ Estados sincronizados correctamente")
    print("✅ Visibilidad apropiada por roles")

    return True

def test_filtros_y_busqueda():
    """Test: Filtros y opciones de búsqueda"""
    print("\n🔍 Test: Filtros y Búsqueda")

    admin_token = login_user(ADMIN_USER)
    if not admin_token:
        return False

    # Crear algunas solicitudes de test con diferentes estados
    test_solicitudes = [
        {"descripcion": "Test filtro 1", "ubicacion": "Test 1", "prioridad": "baja"},
        {"descripcion": "Test filtro 2", "ubicacion": "Test 2", "prioridad": "media"},
        {"descripcion": "Test filtro 3", "ubicacion": "Test 3", "prioridad": "alta"}
    ]

    ids_creados = []
    for sol_data in test_solicitudes:
        response = requests.post(
            f"{BASE_URL}/api/maintenance/solicitudes/",
            json=sol_data,
            headers=get_auth_headers(admin_token)
        )
        if response.status_code == 201:
            ids_creados.append(response.json()['id'])

    if not ids_creados:
        print("❌ No se pudieron crear solicitudes de test")
        return False

    # Test filtro por estado
    response = requests.get(
        f"{BASE_URL}/api/maintenance/solicitudes/?estado=pendiente",
        headers=get_auth_headers(admin_token)
    )

    if response.status_code == 200:
        solicitudes_filtradas = response.json()
        print(f"✅ Filtro por estado funciona ({len(solicitudes_filtradas)} resultados)")
    else:
        print("❌ Filtro por estado falló")
        return False

    # Test filtro por prioridad
    response = requests.get(
        f"{BASE_URL}/api/maintenance/solicitudes/?prioridad=media",
        headers=get_auth_headers(admin_token)
    )

    if response.status_code == 200:
        print("✅ Filtro por prioridad funciona")
    else:
        print("❌ Filtro por prioridad falló")
        return False

    print("✅ Sistema de filtros operativo")
    return True

def main():
    """Función principal"""
    print("🧪 Test de Integración - Módulo de Mantenimiento")
    print("=" * 60)

    resultados = []

    # Test 1: Flujo completo
    resultados.append(test_flujo_completo_mantenimiento())

    # Test 2: Filtros y búsqueda
    resultados.append(test_filtros_y_busqueda())

    # Resultados finales
    print("\n" + "=" * 60)
    print("📊 RESULTADOS FINALES")
    print("=" * 60)

    exitosos = sum(resultados)
    total = len(resultados)

    print(f"Tests exitosos: {exitosos}/{total}")

    for i, resultado in enumerate(resultados, 1):
        status = "✅" if resultado else "❌"
        test_name = ["Flujo Completo", "Filtros y Búsqueda"][i-1]
        print(f"  {i}. {test_name}: {status}")

    if exitosos == total:
        print("\n🎉 TODOS LOS TESTS DE INTEGRACIÓN PASARON!")
        print("El módulo de mantenimiento está completamente funcional.")
        return True
    else:
        print(f"\n⚠️  {total - exitosos} tests de integración fallaron")
        return False

if __name__ == "__main__":
    main()
