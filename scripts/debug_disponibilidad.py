#!/usr/bin/env python3
import requests
from datetime import datetime, timedelta

# Login
response = requests.post('http://127.0.0.1:8000/api/auth-token/', json={'username': 'admin', 'password': 'clave123'})
if response.status_code == 200:
    token = response.json()['token']
    print('✅ Token obtenido')

    # Obtener áreas
    headers = {'Authorization': f'Token {token}'}
    response = requests.get('http://127.0.0.1:8000/api/reservations/areas/', headers=headers)
    if response.status_code == 200:
        areas = response.json()
        print(f'✅ Áreas encontradas: {len(areas)}')
        if areas:
            area_id = areas[0]['id']
            print(f'🎯 Usando área ID: {area_id}')

            # Consultar disponibilidad
            fecha_manana = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
            print(f'📅 Consultando disponibilidad para: {fecha_manana}')
            response = requests.get(f'http://127.0.0.1:8000/api/reservations/areas/{area_id}/disponibilidad/',
                                  headers=headers, params={'fecha': fecha_manana})
            print(f'📊 Status disponibilidad: {response.status_code}')
            if response.status_code == 200:
                data = response.json()
                slots = data.get('slots_disponibles', [])
                print(f'📋 Total slots: {len(slots)}')
                disponibles = [s for s in slots if s['disponible']]
                print(f'✅ Slots disponibles (libres): {len(disponibles)}')
                if disponibles:
                    print(f'🎯 Primer slot disponible: {disponibles[0]}')
                else:
                    print('❌ No hay slots disponibles')
                    print(f'Debug - slots totales: {len(slots)}')
                    if slots:
                        print(f'Primer slot (no disponible): {slots[0]}')
            else:
                print(f'❌ Error: {response.text}')
    else:
        print(f'❌ Error obteniendo áreas: {response.text}')
else:
    print(f'❌ Error login: {response.text}')