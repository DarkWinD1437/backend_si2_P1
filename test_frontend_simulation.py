#!/usr/bin/env python
"""
Script de prueba para simular la petición del frontend
"""
import requests
import json
from datetime import date

# Configuración
API_BASE_URL = 'http://127.0.0.1:8000/api/finances'
TOKEN = 'Token TU_TOKEN_AQUI'  # Reemplaza con un token válido

headers = {
    'Content-Type': 'application/json',
    'Authorization': TOKEN
}

def test_frontend_simulation():
    """Simular exactamente lo que hace el frontend"""
    print("=== SIMULACIÓN DE PETICIÓN DEL FRONTEND ===")

    # Datos que vendrían del formulario del frontend (simulando edición)
    concepto_form = {
        'nombre': 'Actualización Ascensor',
        'descripcion': 'Nueva descripción desde el frontend',
        'tipo': 'otros',  # Tipo válido
        'monto': '800000.00',
        'estado': 'activo',
        'fecha_vigencia_desde': '2025-09-28',
        'fecha_vigencia_hasta': '',  # Vacío, debería convertirse a null
        'es_recurrente': False,
        'aplica_a_todos': True
    }

    print(f"Datos del formulario: {concepto_form}")

    # Limpiar datos como lo hace el frontend
    clean_data = concepto_form.copy()

    # Si fecha_vigencia_hasta está vacía, enviar null en lugar de cadena vacía
    if not clean_data['fecha_vigencia_hasta'] or clean_data['fecha_vigencia_hasta'].strip() == '':
        clean_data['fecha_vigencia_hasta'] = None

    print(f"Datos limpios: {clean_data}")

    # Hacer la petición PUT
    concepto_id = 1  # ID del concepto a actualizar
    url = f"{API_BASE_URL}/conceptos/{concepto_id}/"

    try:
        response = requests.put(url, json=clean_data, headers=headers)
        print(f"Status code: {response.status_code}")
        print(f"Response: {response.text}")

        if response.status_code == 200:
            data = response.json()
            print(f"✅ Actualización exitosa")
            print(f"Descripción devuelta: '{data.get('descripcion')}'")
        else:
            print(f"❌ Error en la actualización: {response.status_code}")

    except Exception as e:
        print(f"❌ Error de conexión: {e}")

if __name__ == '__main__':
    test_frontend_simulation()