#!/usr/bin/env python3
"""
Script para probar que el login facial rechaza imágenes sin rostro
"""
import base64
import requests
import json
import cv2
import numpy as np
from PIL import Image
import io

def crear_imagen_sin_rostro():
    """Crear una imagen simple sin rostro (solo colores)"""
    # Crear una imagen de 320x240 con gradiente
    img = np.zeros((240, 320, 3), dtype=np.uint8)

    # Crear un gradiente simple
    for i in range(240):
        for j in range(320):
            img[i, j] = [i//2, j//2, 128]  # Gradiente azul-rojo

    # Convertir a base64
    pil_img = Image.fromarray(img)
    buffer = io.BytesIO()
    pil_img.save(buffer, format='JPEG')
    img_base64 = base64.b64encode(buffer.getvalue()).decode()

    return f"data:image/jpeg;base64,{img_base64}"

def crear_imagen_con_ruido():
    """Crear una imagen con ruido aleatorio (sin rostro)"""
    # Crear imagen con ruido aleatorio
    img = np.random.randint(0, 255, (240, 320, 3), dtype=np.uint8)

    # Convertir a base64
    pil_img = Image.fromarray(img)
    buffer = io.BytesIO()
    pil_img.save(buffer, format='JPEG')
    img_base64 = base64.b64encode(buffer.getvalue()).decode()

    return f"data:image/jpeg;base64,{img_base64}"

def probar_login_sin_rostro(url_base, imagen_base64):
    """Probar login facial con imagen sin rostro"""
    print("🧪 Probando login facial con imagen SIN rostro...")

    payload = {
        'imagen_base64': imagen_base64
    }

    try:
        response = requests.post(f"{url_base}/api/security/login-facial/", json=payload, timeout=30)
        print(f"📡 Respuesta del servidor: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            login_exitoso = data.get('login_exitoso', False)

            if login_exitoso:
                print("❌ ERROR: Login exitoso cuando NO debería serlo (no hay rostro)")
                print(f"   Usuario: {data.get('usuario', {}).get('username', 'N/A')}")
                print(f"   Confianza: {data.get('confianza', 'N/A')}")
                return False
            else:
                print("✅ CORRECTO: Login rechazado correctamente")
                print(f"   Mensaje: {data.get('mensaje', 'N/A')}")
                return True
        else:
            print(f"❌ Error HTTP: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error en la petición: {e}")
        return False

def main():
    """Función principal"""
    url_base = "http://localhost:8000"

    print("🚀 Iniciando pruebas de seguridad facial...")
    print(f"📍 URL del servidor: {url_base}")
    print()

    # Prueba 1: Imagen con gradiente (sin rostro)
    print("Test 1: Imagen con gradiente simple")
    imagen_gradiente = crear_imagen_sin_rostro()
    resultado1 = probar_login_sin_rostro(url_base, imagen_gradiente)
    print()

    # Prueba 2: Imagen con ruido aleatorio (sin rostro)
    print("Test 2: Imagen con ruido aleatorio")
    imagen_ruido = crear_imagen_con_ruido()
    resultado2 = probar_login_sin_rostro(url_base, imagen_ruido)
    print()

    # Resultado final
    print("📊 RESULTADO FINAL:")
    if resultado1 and resultado2:
        print("✅ TODAS LAS PRUEBAS PASARON: El sistema correctamente rechaza imágenes sin rostro")
        print("🔒 SEGURIDAD FACIAL FUNCIONANDO CORRECTAMENTE")
    else:
        print("❌ ALGUNAS PRUEBAS FALLARON: El sistema permite login sin rostro detectado")
        print("🚨 BRECHA DE SEGURIDAD DETECTADA")

if __name__ == "__main__":
    main()