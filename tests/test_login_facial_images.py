#!/usr/bin/env python3
"""
Script para probar el endpoint de login facial con diferentes tipos de imágenes
"""
import requests
import base64
import json
from PIL import Image, ImageDraw
import numpy as np

# Configuración
BASE_URL = 'http://localhost:8000/api/security'
HEADERS = {'Content-Type': 'application/json'}

def create_uniform_image(color=(0, 0, 0), size=(640, 480)):
    """Crear una imagen uniforme de un color específico"""
    img = Image.new('RGB', size, color)
    return img

def image_to_base64(image):
    """Convertir imagen PIL a base64"""
    from io import BytesIO
    buffer = BytesIO()
    image.save(buffer, format='JPEG')
    return base64.b64encode(buffer.getvalue()).decode()

def test_login_facial(image_base64, description):
    """Probar login facial con una imagen específica"""
    print(f"\n=== Probando: {description} ===")

    data = {
        'imagen_base64': image_base64
    }

    try:
        response = requests.post(f'{BASE_URL}/login-facial/', json=data, headers=HEADERS)
        result = response.json()

        print(f"Status Code: {response.status_code}")
        print(f"Login Exitoso: {result.get('login_exitoso', 'N/A')}")
        print(f"Confianza: {result.get('confianza', 'N/A')}")
        print(f"Mensaje: {result.get('mensaje', 'N/A')}")

        if 'mensaje_ia' in result:
            print(f"Mensaje IA: {result['mensaje_ia'][:100]}...")

        return result

    except Exception as e:
        print(f"Error: {e}")
        return None

def main():
    print("=== PRUEBA DE LOGIN FACIAL ===")

    # 1. Probar con imagen negra (debería ser rechazada)
    black_image = create_uniform_image(color=(0, 0, 0))
    black_base64 = image_to_base64(black_image)
    test_login_facial(black_base64, "Imagen negra uniforme")

    # 2. Probar con imagen blanca (debería ser rechazada)
    white_image = create_uniform_image(color=(255, 255, 255))
    white_base64 = image_to_base64(white_image)
    test_login_facial(white_base64, "Imagen blanca uniforme")

    # 3. Probar con imagen gris (debería ser rechazada)
    gray_image = create_uniform_image(color=(128, 128, 128))
    gray_base64 = image_to_base64(gray_image)
    test_login_facial(gray_base64, "Imagen gris uniforme")

    # 4. Probar con imagen de ruido (debería ser rechazada si no hay rostro)
    noise_array = np.random.randint(0, 256, (480, 640, 3), dtype=np.uint8)
    noise_image = Image.fromarray(noise_array)
    noise_base64 = image_to_base64(noise_image)
    test_login_facial(noise_base64, "Imagen de ruido aleatorio")

    print("\n=== FIN DE PRUEBAS ===")

if __name__ == '__main__':
    main()