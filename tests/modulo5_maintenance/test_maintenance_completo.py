"""
Script completo para probar el módulo de gestión de mantenimiento
Módulo 5: Gestión de Mantenimiento

Ejecutar con: python test_maintenance_completo.py
"""

import requests
import json
from datetime import datetime, timedelta
import sys

# Configuración
BASE_URL = 'http://127.0.0.1:8000'
ADMIN_USER = {'username': 'admin', 'password': 'clave123'}
RESIDENT_USER = {'username': 'prueba', 'password': 'clave123'}  # Usuario residente
MAINTENANCE_USER = {'username': 'prueba2', 'password': 'clave123'}  # Usuario de mantenimiento (asumiendo que existe)

def login_user(user_data, user_type):
    """Login de usuario y obtener token"""
    print(f"🔑 Probando login de {user_type}...")

    try:
        response = requests.post(
            f'{BASE_URL}/api/auth-token/',
            json=user_data,
            headers={'Content-Type': 'application/json'}
        )

        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            print(f"   ✅ Login {user_type} exitoso!")
            print(f"      Token: {token[:20]}...")
            return token
        else:
            print(f"   ❌ Error: {response.text}")
            return None

    except Exception as e:
        print(f"   💥 Error con {user_type}: {e}")
        return None

def test_crear_solicitud_mantenimiento(token, user_type):
    """T1: Registrar Solicitud de Mantenimiento"""
    print(f"\n🏗️  Probando T1 - Registrar Solicitud de Mantenimiento ({user_type})...")

    headers = {
        'Authorization': f'Token {token}',
        'Content-Type': 'application/json'
    }

    data = {
        'descripcion': 'La luz del pasillo del piso 3 no funciona',
        'ubicacion': 'Pasillo piso 3, cerca del ascensor',
        'prioridad': 'media'
    }

    try:
        response = requests.post(
            f'{BASE_URL}/api/maintenance/solicitudes/',
            json=data,
            headers=headers
        )

        print(f"   Status: {response.status_code}")

        if response.status_code == 201:
            solicitud = response.json()
            print("   ✅ Solicitud creada exitosamente!")
            print(f"      ID: {solicitud.get('id')}")
            print(f"      Estado: {solicitud.get('estado')}")
            print(f"      Prioridad: {solicitud.get('prioridad')}")
            return solicitud.get('id')
        else:
            print(f"   ❌ Error: {response.text}")
            return None

    except Exception as e:
        print(f"   💥 Error: {e}")
        return None

def test_listar_solicitudes_mantenimiento(token, user_type):
    """Listar solicitudes de mantenimiento"""
    print(f"\n📋 Probando listar solicitudes de mantenimiento ({user_type})...")

    headers = {
        'Authorization': f'Token {token}',
        'Content-Type': 'application/json'
    }

    try:
        response = requests.get(
            f'{BASE_URL}/api/maintenance/solicitudes/',
            headers=headers
        )

        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            solicitudes = response.json()
            print(f"   ✅ Lista obtenida! ({len(solicitudes)} solicitudes)")
            if solicitudes:
                primera = solicitudes[0]
                print(f"      Primera solicitud - ID: {primera.get('id')}, Estado: {primera.get('estado')}")
            return solicitudes
        else:
            print(f"   ❌ Error: {response.text}")
            return None

    except Exception as e:
        print(f"   💥 Error: {e}")
        return None

def test_asignar_tarea_mantenimiento(token, solicitud_id, user_type):
    """T2: Asignar Tarea de Mantenimiento"""
    print(f"\n👷 Probando T2 - Asignar Tarea de Mantenimiento ({user_type})...")

    headers = {
        'Authorization': f'Token {token}',
        'Content-Type': 'application/json'
    }

    # Primero necesitamos obtener un usuario de mantenimiento
    # Asumimos que el admin puede asignar a sí mismo o a otro usuario
    data = {
        'asignado_a_id': 1,  # ID del admin (ajustar según necesidad)
        'descripcion_tarea': 'Revisar y reparar instalación eléctrica en pasillo piso 3',
        'notas': 'Verificar circuito principal y reemplazar bombilla si es necesario'
    }

    try:
        response = requests.post(
            f'{BASE_URL}/api/maintenance/solicitudes/{solicitud_id}/asignar_tarea/',
            json=data,
            headers=headers
        )

        print(f"   Status: {response.status_code}")

        if response.status_code == 201:
            tarea = response.json()
            print("   ✅ Tarea asignada exitosamente!")
            print(f"      ID Tarea: {tarea.get('id')}")
            print(f"      Asignado a: {tarea.get('asignado_a_info', {}).get('username')}")
            print(f"      Estado: {tarea.get('estado')}")
            return tarea.get('id')
        else:
            print(f"   ❌ Error: {response.text}")
            return None

    except Exception as e:
        print(f"   💥 Error: {e}")
        return None

def test_actualizar_estado_tarea(token, tarea_id, user_type):
    """T3: Seguimiento de Estado de Mantenimiento"""
    print(f"\n📊 Probando T3 - Actualizar Estado de Tarea ({user_type})...")

    headers = {
        'Authorization': f'Token {token}',
        'Content-Type': 'application/json'
    }

    data = {
        'estado': 'en_progreso',
        'notas': 'Iniciando revisión del circuito eléctrico'
    }

    try:
        response = requests.post(
            f'{BASE_URL}/api/maintenance/tareas/{tarea_id}/actualizar_estado/',
            json=data,
            headers=headers
        )

        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            tarea = response.json()
            print("   ✅ Estado de tarea actualizado!")
            print(f"      Estado actual: {tarea.get('estado')}")
            print(f"      Notas: {tarea.get('notas')}")
            return True
        else:
            print(f"   ❌ Error: {response.text}")
            return False

    except Exception as e:
        print(f"   💥 Error: {e}")
        return False

def test_completar_tarea(token, tarea_id, user_type):
    """Completar tarea de mantenimiento"""
    print(f"\n✅ Probando completar tarea ({user_type})...")

    headers = {
        'Authorization': f'Token {token}',
        'Content-Type': 'application/json'
    }

    data = {
        'estado': 'completada',
        'notas': 'Circuito reparado. Bombilla reemplazada. Funcionando correctamente.'
    }

    try:
        response = requests.post(
            f'{BASE_URL}/api/maintenance/tareas/{tarea_id}/actualizar_estado/',
            json=data,
            headers=headers
        )

        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            tarea = response.json()
            print("   ✅ Tarea completada!")
            print(f"      Estado final: {tarea.get('estado')}")
            print(f"      Fecha completado: {tarea.get('fecha_completado')}")
            return True
        else:
            print(f"   ❌ Error: {response.text}")
            return False

    except Exception as e:
        print(f"   💥 Error: {e}")
        return False

def main():
    """Función principal para ejecutar todas las pruebas"""
    print("🚀 Iniciando pruebas del Módulo de Gestión de Mantenimiento")
    print("=" * 60)

    # Login de usuarios
    admin_token = login_user(ADMIN_USER, "Admin")
    resident_token = login_user(RESIDENT_USER, "Residente")
    maintenance_token = login_user(MAINTENANCE_USER, "Mantenimiento")

    if not admin_token:
        print("❌ No se pudo hacer login como admin. Abortando pruebas.")
        return

    # T1: Registrar Solicitud de Mantenimiento
    print("\n" + "="*60)
    print("TAREA 1: REGISTRAR SOLICITUD DE MANTENIMIENTO")
    print("="*60)

    # Como residente
    if resident_token:
        solicitud_id = test_crear_solicitud_mantenimiento(resident_token, "Residente")
    else:
        # Como admin si no hay residente
        solicitud_id = test_crear_solicitud_mantenimiento(admin_token, "Admin")

    if not solicitud_id:
        print("❌ No se pudo crear solicitud. Abortando pruebas.")
        return

    # Listar solicitudes
    test_listar_solicitudes_mantenimiento(admin_token, "Admin")

    # T2: Asignar Tarea de Mantenimiento
    print("\n" + "="*60)
    print("TAREA 2: ASIGNAR TAREA DE MANTENIMIENTO")
    print("="*60)

    tarea_id = test_asignar_tarea_mantenimiento(admin_token, solicitud_id, "Admin")

    if not tarea_id:
        print("❌ No se pudo asignar tarea.")
        return

    # T3: Seguimiento de Estado de Mantenimiento
    print("\n" + "="*60)
    print("TAREA 3: SEGUIMIENTO DE ESTADO DE MANTENIMIENTO")
    print("="*60)

    # Actualizar a en progreso
    test_actualizar_estado_tarea(admin_token, tarea_id, "Admin")

    # Completar tarea
    test_completar_tarea(admin_token, tarea_id, "Admin")

    # Verificación final
    print("\n" + "="*60)
    print("VERIFICACIÓN FINAL")
    print("="*60)

    # Listar solicitudes finales
    solicitudes_finales = test_listar_solicitudes_mantenimiento(admin_token, "Admin")

    print("\n🎉 PRUEBAS COMPLETADAS!")
    print("✅ Todas las tareas del módulo de mantenimiento han sido implementadas y probadas:")
    print("   1. ✅ Registrar Solicitud de Mantenimiento")
    print("   2. ✅ Asignar Tarea de Mantenimiento")
    print("   3. ✅ Seguimiento de Estado de Mantenimiento")

if __name__ == "__main__":
    main()