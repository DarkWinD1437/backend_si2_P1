#!/usr/bin/env python3
"""
Script completo para probar registro y login facial con MediaPipe
"""

import sys
import os
import base64
import json
import requests
from PIL import Image
import numpy as np
import cv2
import io

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def create_test_image():
    """Crear una imagen de prueba simple que sea detectada por face_recognition"""
    print("📸 Creando imagen de prueba simple...")

    # Crear imagen base
    image = np.full((400, 400, 3), (200, 180, 160), dtype=np.uint8)  # Color de piel uniforme
    
    # Dibujar un óvalo simple para el rostro
    cv2.ellipse(image, (200, 200), (100, 120), 0, 0, 360, (210, 190, 170), -1)
    
    # Ojos simples
    cv2.circle(image, (170, 180), 10, (255, 255, 255), -1)
    cv2.circle(image, (170, 180), 5, (0, 0, 0), -1)
    cv2.circle(image, (230, 180), 10, (255, 255, 255), -1)
    cv2.circle(image, (230, 180), 5, (0, 0, 0), -1)
    
    # Boca simple
    cv2.ellipse(image, (200, 240), (20, 10), 0, 0, 360, (150, 50, 50), -1)

    # Convertir a formato PIL y luego a base64
    pil_image = Image.fromarray(image.astype('uint8'), 'RGB')
    buffer = io.BytesIO()
    pil_image.save(buffer, format='JPEG')
    image_base64 = base64.b64encode(buffer.getvalue()).decode()

    return f"data:image/jpeg;base64,{image_base64}"

def test_registration(base64_image, user_id="admin"):
    """Probar registro facial"""
    print(f"📝 Registrando rostro para usuario: {user_id}")

    try:
        # URL del endpoint de registro facial
        url = "http://localhost:8000/api/security/rostros/registrar_con_ia/"

        # Necesitamos autenticación - usar token de admin
        headers = {
            'Authorization': 'Token 50d2a230697b759381ad7843c297b990c0016ce9',
            'Content-Type': 'application/json'
        }

        payload = {
            "imagen_base64": base64_image,
            "nombre_identificador": f"Test Face {user_id}",
            "confianza_minima": 0.8
        }

        response = requests.post(url, json=payload, headers=headers, timeout=30)

        print(f"📡 Respuesta del registro: {response.status_code}")

        if response.status_code == 201:
            result = response.json()
            print("✅ Registro exitoso!")
            print(f"   ID del rostro: {result.get('data', {}).get('id', 'N/A')}")
            return True, result
        else:
            print(f"❌ Error en registro: {response.text}")
            # Si ya existe, considerarlo como éxito
            if "ya existe" in response.text.lower():
                print("ℹ️ Rostro ya registrado, continuando...")
                return True, {"message": "Already registered"}
            return False, None

    except Exception as e:
        print(f"❌ Error de conexión en registro: {e}")
        return False, None

def test_login(base64_image, user_id="admin"):
    """Probar login facial"""
    print(f"🔐 Probando login facial para usuario: {user_id}")

    try:
        # URL del endpoint de login facial
        url = "http://localhost:8000/api/security/login-facial/"

        payload = {
            "imagen_base64": base64_image
        }

        response = requests.post(url, json=payload, timeout=30)

        print(f"📡 Respuesta del servidor: {response.status_code}")

        if response.status_code == 200:
            result = response.json()
            if result.get('login_exitoso', False):
                print("✅ Login exitoso!")
                print(f"   Usuario autenticado: {result.get('usuario', {}).get('username', 'N/A')}")
                print(f"   Confianza: {result.get('confianza', 0):.3f}")
                print(f"   Token generado: {result.get('token', 'N/A')[:20]}...")
                return True, result
            else:
                print(f"❌ Login fallido: {result.get('mensaje', 'Rostro no reconocido')}")
                return False, result
        else:
            print(f"❌ Error en login: {response.text}")
            return False, None

    except Exception as e:
        print(f"❌ Error de conexión en login: {e}")
        return False, None

def check_server_status():
    """Verificar que el servidor esté corriendo"""
    print("🔍 Verificando estado del servidor...")

    try:
        # Probar endpoint de login facial que no requiere auth
        response = requests.post("http://localhost:8000/api/security/login-facial/", 
                               json={"imagen_base64": "data:image/jpeg;base64,test"}, 
                               timeout=5)
        # El servidor está corriendo si responde (incluso con error de validación)
        print("✅ Servidor corriendo correctamente")
        return True
    except Exception as e:
        print(f"❌ Servidor no disponible: {e}")
        return False

def main():
    print("🚀 Iniciando prueba completa de registro y login facial con MediaPipe")
    print("=" * 80)

    # Verificar servidor
    if not check_server_status():
        print("❌ El servidor no está disponible. Asegúrate de que esté corriendo.")
        return

    # Crear imagen de prueba similar al rostro registrado
    test_image_base64 = create_test_image()
    print("✅ Imagen de prueba creada")

    # Registrar el rostro primero
    print("\n" + "-" * 50)
    success_reg, reg_result = test_registration(test_image_base64, "admin")

    # Esperar un momento
    import time
    print("⏳ Esperando 2 segundos...")
    time.sleep(2)

    # Probar login con imagen similar (debería funcionar)
    print("\n" + "-" * 50)
    success_login, login_result = test_login(test_image_base64, "admin")

    # Probar login con imagen completamente diferente (debería fallar)
    print("\n" + "-" * 50)
    print("🔄 Probando seguridad - login con imagen diferente...")

    # Crear imagen completamente diferente (no rostro)
    different_image = np.full((400, 400, 3), (100, 150, 200), dtype=np.uint8)  # Color azul sólido
    pil_image = Image.fromarray(different_image.astype('uint8'), 'RGB')
    buffer = io.BytesIO()
    pil_image.save(buffer, format='JPEG')
    different_image_base64 = base64.b64encode(buffer.getvalue()).decode()
    different_image_base64 = f"data:image/jpeg;base64,{different_image_base64}"

    success_login2, login_result2 = test_login(different_image_base64, "admin")

    print("\n" + "=" * 80)
    if success_reg and success_login and not success_login2:
        print("🎉 ¡Prueba completa exitosa!")
        print("✅ MediaPipe está funcionando correctamente")
        print("✅ El sistema reconoce rostros registrados")
        print("✅ El sistema rechaza imágenes sin rostros (seguridad)")
        print("✅ Sistema de reconocimiento facial completamente operativo")
    else:
        print("⚠️ La prueba no fue completamente exitosa")
        if not success_reg:
            print("  - Falló el registro")
        if not success_login:
            print("  - Falló el login con rostro válido")
        if success_login2:
            print("  - Error de seguridad: login exitoso con imagen inválida")

if __name__ == "__main__":
    main()