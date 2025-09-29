#!/usr/bin/env python3
import requests

response = requests.get('http://127.0.0.1:8000/api/reservations/areas/')
print(f'Status: {response.status_code}')
if response.status_code == 200:
    data = response.json()
    print(f'Áreas encontradas: {len(data)}')
    for area in data[:3]:  # Mostrar primeras 3
        print(f'- {area["nombre"]} ({area["tipo_display"]})')
else:
    print(f'Error: {response.text[:200]}...')