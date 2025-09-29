#!/usr/bin/env python3
"""
Script para probar login facial con imagen que simula un rostro real
"""
import requests
import base64
from PIL import Image, ImageDraw
import numpy as np

# Configuración
BASE_URL = 'http://localhost:8000/api/security'
HEADERS = {'Content-Type': 'application/json'}

def create_simulated_face_image():
    """Crear una imagen que simule características faciales básicas"""
    # Crear imagen base
    img = Image.new('RGB', (320, 240), color=(200, 180, 160))  # Tono de piel
    draw = ImageDraw.Draw(img)

    # Dibujar forma ovalada (simulando rostro)
    draw.ellipse([80, 60, 240, 180], fill=(210, 190, 170))

    # Agregar algunos detalles para simular características faciales
    # Ojos
    draw.ellipse([120, 100, 140, 120], fill=(255, 255, 255))
    draw.ellipse([180, 100, 200, 120], fill=(255, 255, 255))
    draw.ellipse([125, 105, 135, 115], fill=(0, 0, 0))
    draw.ellipse([185, 105, 195, 115], fill=(0, 0, 0))

    # Boca
    draw.arc([140, 130, 180, 150], start=0, end=180, fill=(150, 50, 50), width=3)

    # Nariz
    draw.polygon([(160, 110), (155, 125), (165, 125)], fill=(190, 170, 150))

    # Agregar textura para simular piel
    img_array = np.array(img)
    noise = np.random.normal(0, 10, img_array.shape).astype(np.uint8)
    img_array = np.clip(img_array + noise, 0, 255)
    img = Image.fromarray(img_array)

    return img

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
    print("=== PRUEBA DE LOGIN FACIAL CON IMAGEN SIMULADA ===")

    # Probar con imagen que simula un rostro
    simulated_face = create_simulated_face_image()
    simulated_base64 = base64.b64encode(simulated_face.tobytes()).decode()

    # Usar el método correcto para convertir a base64
    from io import BytesIO
    buffer = BytesIO()
    simulated_face.save(buffer, format='JPEG')
    simulated_base64 = base64.b64encode(buffer.getvalue()).decode()

    test_login_facial(simulated_base64, "Imagen simulada de rostro")

    print("\n=== FIN DE PRUEBA ===")

if __name__ == '__main__':
    main()