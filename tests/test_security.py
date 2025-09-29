#!/usr/bin/env python3
"""
Script de prueba de seguridad para el sistema de reconocimiento facial avanzado.
Verifica que solo rostros registrados puedan hacer login y que no haya falsos positivos.
"""

import os
import sys
import json
import requests
import base64
from PIL import Image
import numpy as np

# Configuración
BASE_URL = "http://127.0.0.1:8000"
API_URL = f"{BASE_URL}/api"

def encode_image_to_base64(image_path):
    """Codifica una imagen a base64."""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')

def test_security():
    """Prueba la seguridad del sistema facial."""
    print("🛡️  Iniciando pruebas de seguridad del sistema facial...")

    # 1. Intentar login con imagen no registrada
    print("\n1. Probando login con rostro NO registrado...")

    # Usar una imagen de prueba (asegurarse de que no esté registrada)
    test_image_path = "c:\\Users\\PG\\Desktop\\Materias\\Sistemas de informacion 2\\Proyectos\\Parcial 1\\Backend_Django\\media\\test_unregistered_face.jpg"

    # Crear directorio si no existe
    os.makedirs(os.path.dirname(test_image_path), exist_ok=True)

    if not os.path.exists(test_image_path):
        print(f"❌ Imagen de prueba no encontrada: {test_image_path}")
        print("   Creando imagen de prueba básica...")
        # Crear una imagen básica para prueba
        img = Image.new('RGB', (100, 100), color='red')
        img.save(test_image_path)

    try:
        with open(test_image_path, "rb") as f:
            image_data = base64.b64encode(f.read()).decode('utf-8')

        payload = {
            "image": image_data,
            "user_id": None  # Sin user_id para login general
        }

        response = requests.post(f"{API_URL}/facial-login/", json=payload)
        result = response.json()

        if response.status_code == 200:
            if result.get('success'):
                print("❌ ERROR: Login exitoso con rostro NO registrado!")
                print(f"   Usuario: {result.get('user', {}).get('username', 'N/A')}")
                return False
            else:
                print("✅ Correcto: Login rechazado para rostro no registrado")
                print(f"   Mensaje: {result.get('message', 'Rostro no reconocido')}")
        else:
            print(f"✅ Correcto: Error HTTP {response.status_code} para rostro no registrado")
            print(f"   Mensaje: {result.get('detail', 'Error esperado')}")

    except Exception as e:
        print(f"❌ Error en prueba de login no registrado: {e}")
        return False

    # 2. Verificar que usuarios registrados existen
    print("\n2. Verificando usuarios registrados...")

    try:
        response = requests.get(f"{API_URL}/facial-users/")
        if response.status_code == 200:
            users = response.json()
            print(f"✅ Usuarios registrados encontrados: {len(users)}")
            for user in users[:3]:  # Mostrar primeros 3
                print(f"   - {user.get('username', 'N/A')}: {user.get('facial_data_count', 0)} registros faciales")
        else:
            print(f"❌ Error obteniendo usuarios: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error verificando usuarios: {e}")
        return False

    # 3. Probar login con datos inválidos
    print("\n3. Probando login con datos inválidos...")

    invalid_payloads = [
        {"image": "", "user_id": None},  # Imagen vacía
        {"image": "invalid_base64", "user_id": None},  # Base64 inválido
        {"user_id": None},  # Sin imagen
    ]

    for i, payload in enumerate(invalid_payloads, 1):
        try:
            response = requests.post(f"{API_URL}/facial-login/", json=payload)
            if response.status_code != 200:
                print(f"✅ Correcto: Payload inválido {i} rechazado (HTTP {response.status_code})")
            else:
                result = response.json()
                if not result.get('success'):
                    print(f"✅ Correcto: Payload inválido {i} rechazado")
                else:
                    print(f"❌ ERROR: Payload inválido {i} aceptado!")
                    return False
        except Exception as e:
            print(f"❌ Error en payload inválido {i}: {e}")
            return False

    print("\n🎉 Todas las pruebas de seguridad pasaron exitosamente!")
    return True

if __name__ == "__main__":
    success = test_security()
    sys.exit(0 if success else 1)