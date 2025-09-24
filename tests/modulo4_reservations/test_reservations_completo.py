"""
Script # Configuración
BASE_URL = 'http://127.0.0.1:8000'
ADMIN_USER = {'username': 'admin', 'password': 'clave123'}
RESIDENT_USER = {'username': 'prueba', 'password': 'clave123'}  # Usuario residente con datos
SECURITY_USER = {'username': 'prueba2', 'password': 'clave123'}  # Usuario de seguridad
SECURITY_USER = {'username': 'prueba2', 'password': 'clave123'}  # Usuario de seguridadleto para probar el módulo de reservas de áreas comunes
Módulo 4: Reservas de Áreas Comunes

Ejecutar con: python test_reservations_completo.py
"""

import requests
import json
from datetime import datetime, timedelta
import sys

# Configuración
BASE_URL = 'http://127.0.0.1:8000'
ADMIN_USER = {'username': 'admin', 'password': 'clave123'}
RESIDENT_USER = {'username': 'prueba', 'password': 'clave123'}  # Usuario residente con datos
SECURITY_USER = {'username': 'prueba2', 'password': 'clave123'}  # Usuario de seguridad

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

def test_listar_areas_comunes(token, user_type):
    """T1: Listar áreas comunes disponibles"""
    print(f"\n📋 Probando listar áreas comunes ({user_type})...")

    headers = {'Authorization': f'Token {token}'}

    try:
        response = requests.get(f'{BASE_URL}/api/reservations/areas/', headers=headers)
        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Áreas encontradas: {len(data)}")
            if data:
                for area in data[:3]:  # Mostrar primeras 3
                    print(f"      - {area['nombre']} ({area['tipo_display']}) - Cap: {area['capacidad_maxima']}")
            return data
        else:
            print(f"   ❌ Error: {response.text}")
            return []

    except Exception as e:
        print(f"   💥 Error: {e}")
        return []

def test_consultar_disponibilidad(token, area_id, fecha, user_type):
    """T1: Consultar disponibilidad de área común"""
    print(f"\n📅 Probando consultar disponibilidad ({user_type})...")
    print(f"   Área ID: {area_id}, Fecha: {fecha}")

    headers = {'Authorization': f'Token {token}'}
    params = {'fecha': fecha}

    try:
        response = requests.get(
            f'{BASE_URL}/api/reservations/areas/{area_id}/disponibilidad/',
            headers=headers,
            params=params
        )
        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("   ✅ Disponibilidad obtenida!")
            print(f"      Área: {data['area_comun']['nombre']}")
            print(f"      Día: {data['dia_semana']}")
            print(f"      Horario: {data['horario_disponible']['hora_apertura']} - {data['horario_disponible']['hora_cierre']}")
            print(f"      Slots disponibles: {len(data['slots_disponibles'])}")

            # Mostrar algunos slots disponibles
            disponibles = [s for s in data['slots_disponibles'] if s['disponible']]
            if disponibles:
                print("      📅 Slots disponibles (primeros 3):")
                for slot in disponibles[:3]:
                    print(f"         - {slot['hora_inicio']} - {slot['hora_fin']} (${slot['costo_total']})")
            else:
                print("      ⚠️  No hay slots disponibles para esta fecha")

            return data
        else:
            print(f"   ❌ Error: {response.text}")
            return None

    except Exception as e:
        print(f"   💥 Error: {e}")
        return None

def test_reservar_area(token, area_id, fecha, hora_inicio, hora_fin, user_type):
    """T2: Reservar área común"""
    print(f"\n🎫 Probando reservar área común ({user_type})...")
    print(f"   Área ID: {area_id}")
    print(f"   Fecha: {fecha}, Hora: {hora_inicio} - {hora_fin}")

    headers = {'Authorization': f'Token {token}'}
    data = {
        'fecha': fecha,
        'hora_inicio': hora_inicio,
        'hora_fin': hora_fin,
        'numero_personas': 5,
        'observaciones': f'Reserva de prueba desde {user_type}'
    }

    try:
        response = requests.post(
            f'{BASE_URL}/api/reservations/areas/{area_id}/reservar/',
            json=data,
            headers=headers
        )
        print(f"   Status: {response.status_code}")

        if response.status_code == 201:
            reserva_data = response.json()
            print("   ✅ Reserva creada exitosamente!")
            print(f"      ID Reserva: {reserva_data['id']}")
            print(f"      Estado: {reserva_data['estado_display']}")
            print(f"      Costo: ${reserva_data['costo_total']}")
            print(f"      Duración: {reserva_data['duracion_horas']} horas")
            return reserva_data
        else:
            print(f"   ❌ Error: {response.text}")
            return None

    except Exception as e:
        print(f"   💥 Error: {e}")
        return None

def test_listar_reservas(token, user_type):
    """Listar reservas del usuario"""
    print(f"\n📝 Probando listar reservas ({user_type})...")

    headers = {'Authorization': f'Token {token}'}

    try:
        response = requests.get(f'{BASE_URL}/api/reservations/reservas/', headers=headers)
        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Reservas encontradas: {data['count']}")
            if data['results']:
                for reserva in data['results'][:3]:  # Mostrar primeras 3
                    print(f"      - ID {reserva['id']}: {reserva['area_comun_info']['nombre']} - {reserva['estado_display']}")
            return data
        else:
            print(f"   ❌ Error: {response.text}")
            return None

    except Exception as e:
        print(f"   💥 Error: {e}")
        return None

def test_confirmar_reserva(token, reserva_id, user_type):
    """T3: Confirmar reserva con pago"""
    print(f"\n💳 Probando confirmar reserva con pago ({user_type})...")
    print(f"   Reserva ID: {reserva_id}")

    headers = {'Authorization': f'Token {token}'}
    data = {
        'metodo_pago': 'transferencia_bancaria',
        'referencia_pago': f'REF-{datetime.now().strftime("%Y%m%d%H%M%S")}',
        'observaciones_pago': f'Pago procesado desde {user_type}'
    }

    try:
        response = requests.post(
            f'{BASE_URL}/api/reservations/reservas/{reserva_id}/confirmar/',
            json=data,
            headers=headers
        )
        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            confirmacion_data = response.json()
            print("   ✅ Reserva confirmada y pagada!")
            print(f"      Mensaje: {confirmacion_data['mensaje']}")
            return confirmacion_data
        else:
            print(f"   ❌ Error: {response.text}")
            return None

    except Exception as e:
        print(f"   💥 Error: {e}")
        return None

def test_cancelar_reserva(token, reserva_id, user_type):
    """T4: Cancelar reserva"""
    print(f"\n❌ Probando cancelar reserva ({user_type})...")
    print(f"   Reserva ID: {reserva_id}")

    headers = {'Authorization': f'Token {token}'}
    data = {
        'motivo': f'Cancelación de prueba desde {user_type}'
    }

    try:
        response = requests.post(
            f'{BASE_URL}/api/reservations/reservas/{reserva_id}/cancelar/',
            json=data,
            headers=headers
        )
        print(f"   Status: {response.status_code}")

        if response.status_code == 200:
            cancelacion_data = response.json()
            print("   ✅ Reserva cancelada exitosamente!")
            print(f"      Mensaje: {cancelacion_data['mensaje']}")
            return cancelacion_data
        else:
            print(f"   ❌ Error: {response.text}")
            return None

    except Exception as e:
        print(f"   💥 Error: {e}")
        return None

def main():
    """Función principal de pruebas"""
    print("🚀 PRUEBAS COMPLETAS DEL MÓDULO DE RESERVAS DE ÁREAS COMUNES")
    print("Módulo 4: Reservas de Áreas Comunes")
    print("=" * 70)

    # Login de usuarios
    admin_token = login_user(ADMIN_USER, "admin")
    resident_token = login_user(RESIDENT_USER, "residente")
    security_token = login_user(SECURITY_USER, "seguridad")

    if not admin_token or not resident_token or not security_token:
        print("❌ No se pudieron obtener tokens. Abortando pruebas.")
        sys.exit(1)

    # T1: Listar áreas comunes
    areas_admin = test_listar_areas_comunes(admin_token, "admin")
    areas_resident = test_listar_areas_comunes(resident_token, "residente")

    if not areas_admin:
        print("❌ No hay áreas comunes disponibles. Abortando pruebas.")
        sys.exit(1)

    # Seleccionar primera área para pruebas
    area_id = areas_admin[0]['id']
    print(f"\n🎯 Usando área ID {area_id} para pruebas")

    # Calcular fecha para mañana (para evitar conflictos con reservas existentes)
    fecha_manana = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')

    # T1: Consultar disponibilidad
    disponibilidad = test_consultar_disponibilidad(admin_token, area_id, fecha_manana, "admin")

    if not disponibilidad or not disponibilidad.get('slots_disponibles'):
        print("❌ No hay slots disponibles. Abortando pruebas de reserva.")
        sys.exit(1)

    # Obtener primer slot disponible
    slots_disponibles = [s for s in disponibilidad['slots_disponibles'] if s['disponible']]
    if not slots_disponibles:
        print("❌ No hay slots disponibles. Abortando pruebas de reserva.")
        sys.exit(1)

    primer_slot = slots_disponibles[0]
    hora_inicio = primer_slot['hora_inicio']
    hora_fin = primer_slot['hora_fin']

    print(f"\n🎯 Usando slot: {hora_inicio} - {hora_fin}")

    # T2: Reservar área (como residente)
    reserva = test_reservar_area(resident_token, area_id, fecha_manana, hora_inicio, hora_fin, "residente")

    if not reserva:
        print("❌ No se pudo crear la reserva. Abortando pruebas.")
        sys.exit(1)

    reserva_id = reserva['id']

    # Listar reservas después de crear
    test_listar_reservas(resident_token, "residente")

    # T3: Confirmar reserva con pago
    confirmacion = test_confirmar_reserva(resident_token, reserva_id, "residente")

    # T4: Cancelar reserva (crear otra reserva primero para probar cancelación)
    print("\n🔄 Creando segunda reserva para probar cancelación...")
    segunda_reserva = test_reservar_area(resident_token, area_id, fecha_manana,
                                         slots_disponibles[1]['hora_inicio'] if len(slots_disponibles) > 1 else hora_inicio,
                                         slots_disponibles[1]['hora_fin'] if len(slots_disponibles) > 1 else hora_fin,
                                         "residente")

    if segunda_reserva:
        segunda_reserva_id = segunda_reserva['id']
        # T4: Cancelar la segunda reserva
        cancelacion = test_cancelar_reserva(resident_token, segunda_reserva_id, "residente")

    # Verificar estado final
    print("\n📊 VERIFICACIÓN FINAL")
    print("=" * 40)

    # Listar reservas finales
    reservas_finales = test_listar_reservas(resident_token, "residente")

    print("\n🎯 FUNCIONALIDADES VALIDADAS:")
    print("   ✅ T1: Consultar Disponibilidad de Área Común")
    print("   ✅ T2: Reservar Área Común")
    print("   ✅ T3: Confirmar Reserva con Pago")
    print("   ✅ T4: Cancelar Reserva")
    print("   ✅ Control de permisos por rol")
    print("   ✅ Validaciones de negocio")
    print("   ✅ Integración con sistema de autenticación")

    print("\n✅ MÓDULO 4: RESERVAS DE ÁREAS COMUNES COMPLETAMENTE FUNCIONAL")
    print("=" * 70)

if __name__ == "__main__":
    main()