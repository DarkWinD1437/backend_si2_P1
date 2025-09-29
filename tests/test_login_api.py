#!/usr/bin/env python
import os
import sys
import django
import requests
import base64
from PIL import Image
from io import BytesIO
import numpy as np
import cv2

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

def probar_login_facial_api():
    """Probar el login facial usando la API real"""
    print("=== PRUEBA DE LOGIN FACIAL VIA API ===")

    # Crear una imagen de prueba que simule una captura de webcam
    img = np.random.randint(150, 200, (480, 640, 3), dtype=np.uint8)

    # Agregar un "rostro" simple (óvalo claro)
    center_y, center_x = 240, 320
    for y in range(center_y-80, center_y+80):
        for x in range(center_x-60, center_x+60):
            if 0 <= y < 480 and 0 <= x < 640:
                # Crear un óvalo
                dist = ((y - center_y)/80)**2 + ((x - center_x)/60)**2
                if dist <= 1:
                    brightness = 220 - int(dist * 50)  # Más brillante en el centro
                    img[y, x] = [brightness, brightness, brightness]

    # Convertir a base64
    pil_img = Image.fromarray(img)
    from io import BytesIO
    buffer = BytesIO()
    pil_img.save(buffer, format='JPEG', quality=80)
    imagen_base64 = base64.b64encode(buffer.getvalue()).decode()

    print(f"Imagen de prueba creada: {len(imagen_base64)} caracteres base64")

    # Hacer la petición a la API
    url = "http://localhost:8000/api/security/login-facial/"
    data = {
        "imagen_base64": imagen_base64,
        "ubicacion": "Prueba desde script"
    }

    try:
        print("Enviando petición a la API...")
        response = requests.post(url, json=data, timeout=30)

        print(f"Status code: {response.status_code}")
        print(f"Response: {response.json()}")

        if response.status_code == 200:
            result = response.json()
            if result.get('login_exitoso'):
                print("✅ LOGIN EXITOSO!")
                return True
            else:
                print("❌ Login fallido según API")
                return False
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            return False

    except Exception as e:
        print(f"❌ Error en petición: {e}")
        return False

def probar_con_imagen_realista():
    """Crear una imagen más realista y probar"""
    print("\n=== PRUEBA CON IMAGEN MÁS REALISTA ===")

    # Crear imagen con gradientes y textura
    img = np.random.randint(100, 180, (400, 600, 3), dtype=np.uint8)

    # Agregar ruido para simular webcam
    noise = np.random.normal(0, 20, img.shape).astype(np.uint8)
    img = cv2.add(img, noise)

    # Crear un rostro más detallado
    center_y, center_x = 200, 300

    # Cara ovalada
    for y in range(center_y-70, center_y+90):
        for x in range(center_x-50, center_x+50):
            if 0 <= y < 400 and 0 <= x < 600:
                dist_y = abs(y - center_y) / 80
                dist_x = abs(x - center_x) / 50
                dist = (dist_y**2 + dist_x**2)**0.5
                if dist <= 1:
                    factor = 1 - dist * 0.3
                    brightness = int(200 + factor * 55)
                    img[y, x] = [brightness, brightness - 10, brightness - 20]  # Tono piel

    # Ojos
    cv2.circle(img, (center_x-25, center_y-20), 8, (20, 20, 20), -1)
    cv2.circle(img, (center_x+25, center_y-20), 8, (20, 20, 20), -1)

    # Boca
    cv2.ellipse(img, (center_x, center_y+25), (15, 8), 0, 0, 180, (20, 20, 20), -1)

    # Convertir a base64
    pil_img = Image.fromarray(img)
    buffer = BytesIO()
    pil_img.save(buffer, format='JPEG', quality=85)
    imagen_base64 = base64.b64encode(buffer.getvalue()).decode()

    print(f"Imagen realista creada: {len(imagen_base64)} caracteres base64")

    # Probar con la API
    url = "http://localhost:8000/api/security/login-facial/"
    data = {
        "imagen_base64": imagen_base64,
        "ubicacion": "Prueba realista desde script"
    }

    try:
        response = requests.post(url, json=data, timeout=30)
        print(f"Status code: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            print(f"Login exitoso: {result.get('login_exitoso', False)}")
            print(f"Confianza: {result.get('confianza', 'N/A')}")
            if result.get('mensaje_ia'):
                print(f"Mensaje IA: {result['mensaje_ia'][:100]}...")

        return response.status_code == 200 and result.get('login_exitoso', False)

    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    print("Probando login facial con mejoras...")
    success1 = probar_login_facial_api()
    success2 = probar_con_imagen_realista()

    if success1 or success2:
        print("\n🎉 ¡ALGUNA PRUEBA FUNCIONÓ! Las mejoras están funcionando.")
    else:
        print("\n❌ Ninguna prueba funcionó. Puede que necesitemos más ajustes.")