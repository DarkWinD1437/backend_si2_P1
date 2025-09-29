#!/usr/bin/env python3
"""
Script para probar login facial con una imagen que contiene un rostro real
"""
import base64
import requests
import json
import cv2
import numpy as np
from PIL import Image
import io

def crear_imagen_con_rostro_simple():
    """Crear una imagen simple que simule contener un rostro (para testing)"""
    # Crear una imagen básica con algunas características que podrían parecer un rostro
    img = np.zeros((240, 320, 3), dtype=np.uint8)

    # Crear un óvalo claro en el centro (simulando un rostro)
    center_x, center_y = 160, 120
    for i in range(240):
        for j in range(320):
            # Distancia al centro
            dist = np.sqrt((i - center_y)**2 + (j - center_x)**2)
            # Crear un gradiente que simule iluminación facial
            if dist < 80:
                # Interior del "rostro" - tono de piel
                intensity = 200 - (dist / 80) * 50
                img[i, j] = [int(intensity * 0.9), int(intensity * 0.8), int(intensity)]  # Tono de piel
            else:
                # Fondo
                img[i, j] = [50, 100, 150]  # Azul claro

    # Agregar algunos "rasgos" simples
    # "Ojos"
    cv2.circle(img, (140, 100), 8, (0, 0, 0), -1)  # Ojo izquierdo
    cv2.circle(img, (180, 100), 8, (0, 0, 0), -1)  # Ojo derecho

    # "Nariz"
    cv2.ellipse(img, (160, 130), (5, 15), 0, 0, 360, (0, 0, 0), -1)

    # "Boca"
    cv2.ellipse(img, (160, 160), (20, 8), 0, 0, 360, (0, 0, 0), -1)

    # Convertir a base64
    pil_img = Image.fromarray(img)
    buffer = io.BytesIO()
    pil_img.save(buffer, format='JPEG')
    img_base64 = base64.b64encode(buffer.getvalue()).decode()

    return f"data:image/jpeg;base64,{img_base64}"

def probar_login_con_rostro(url_base, imagen_base64):
    """Probar login facial con imagen que contiene un rostro simulado"""
    print("🧪 Probando login facial con imagen CON rostro simulado...")

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
                print("✅ LOGIN EXITOSO: El sistema reconoció el rostro correctamente")
                print(f"   Usuario: {data.get('usuario', {}).get('username', 'N/A')}")
                print(f"   Confianza: {data.get('confianza', 'N/A')}")
                return True
            else:
                print("⚠️  LOGIN FALLIDO: El sistema no reconoció el rostro")
                print(f"   Mensaje: {data.get('mensaje', 'N/A')}")
                return False
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

    print("🚀 Probando login facial con rostro simulado...")
    print(f"📍 URL del servidor: {url_base}")
    print()

    # Probar con imagen que contiene un rostro simulado
    print("Test: Imagen con rostro simulado")
    imagen_con_rostro = crear_imagen_con_rostro_simple()
    resultado = probar_login_con_rostro(url_base, imagen_con_rostro)
    print()

    # Resultado final
    print("📊 RESULTADO FINAL:")
    if resultado:
        print("✅ LOGIN FUNCIONANDO: El sistema puede reconocer rostros")
        print("🎉 RECONOCIMIENTO FACIAL OPERATIVO")
    else:
        print("❌ LOGIN NO FUNCIONA: El sistema no puede reconocer rostros")
        print("🔧 REVISAR CONFIGURACIÓN DEL SISTEMA")

if __name__ == "__main__":
    main()