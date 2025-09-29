#!/usr/bin/env python
"""
Script de debug para probar el endpoint de la API de reservas
"""

import requests
import json
from datetime import datetime, timedelta

# Configuración
BASE_URL = 'http://127.0.0.1:8000'
RESIDENT_USER = {'username': 'prueba', 'password': 'clave123'}

def debug_api_reserva():
    print("🔍 DEBUG API: Probando endpoint de reservas")
    print("=" * 60)

    # Login
    print("🔑 Probando login...")
    response = requests.post(
        f'{BASE_URL}/api/auth-token/',
        json=RESIDENT_USER,
        headers={'Content-Type': 'application/json'}
    )

    if response.status_code != 200:
        print(f"❌ Error en login: {response.status_code} - {response.text}")
        return

    token = response.json()['token']
    print(f"✅ Login exitoso, token: {token[:20]}...")

    headers = {'Authorization': f'Token {token}'}

    # Listar áreas
    print("\n📋 Probando listar áreas...")
    response = requests.get(f'{BASE_URL}/api/reservations/areas/', headers=headers)

    if response.status_code != 200:
        print(f"❌ Error listando áreas: {response.status_code} - {response.text}")
        return

    areas = response.json()
    print(f"✅ Áreas encontradas: {len(areas)}")

    if not areas:
        print("❌ No hay áreas disponibles")
        return

    area_id = areas[0]['id']
    print(f"🎯 Usando área ID: {area_id}")

    # Consultar disponibilidad
    fecha_manana = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    print(f"\n📅 Probando disponibilidad para fecha: {fecha_manana}")

    response = requests.get(
        f'{BASE_URL}/api/reservations/areas/{area_id}/disponibilidad/',
        headers=headers,
        params={'fecha': fecha_manana}
    )

    if response.status_code != 200:
        print(f"❌ Error consultando disponibilidad: {response.status_code} - {response.text}")
        return

    disponibilidad = response.json()
    print("✅ Disponibilidad obtenida")

    slots_disponibles = [s for s in disponibilidad['slots_disponibles'] if s['disponible']]
    print(f"📋 Slots disponibles: {len(slots_disponibles)}")

    if not slots_disponibles:
        print("❌ No hay slots disponibles")
        return

    # Usar primer slot
    slot = slots_disponibles[0]
    hora_inicio = slot['hora_inicio']
    hora_fin = slot['hora_fin']

    print(f"🎯 Intentando reservar: {hora_inicio} - {hora_fin}")

    # Crear reserva
    print("\n🎫 Probando crear reserva...")
    data = {
        'fecha': fecha_manana,
        'hora_inicio': hora_inicio,
        'hora_fin': hora_fin,
        'numero_personas': 5,
        'observaciones': 'Reserva de debug API'
    }

    print(f"📤 Enviando datos: {json.dumps(data, indent=2)}")

    response = requests.post(
        f'{BASE_URL}/api/reservations/areas/{area_id}/reservar/',
        json=data,
        headers=headers
    )

    print(f"📥 Status: {response.status_code}")
    print(f"📥 Response: {response.text}")

    if response.status_code == 201:
        reserva = response.json()
        print("✅ Reserva creada exitosamente!")
        print(f"   ID: {reserva['id']}")
        print(f"   Estado: {reserva['estado_display']}")
        print(f"   Costo: ${reserva['costo_total']}")
    else:
        print("❌ Error creando reserva")
        try:
            error_data = response.json()
            print(f"   Error details: {json.dumps(error_data, indent=2)}")
        except:
            print(f"   Raw response: {response.text}")

if __name__ == "__main__":
    debug_api_reserva()