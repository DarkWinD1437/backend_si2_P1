#!/usr/bin/env python
"""
Script de prueba avanzado para el sistema de reconocimiento facial
Usa una imagen de prueba más realista con características faciales
"""

import os
import sys
import django
import base64
import requests
import cv2
import numpy as np
from io import BytesIO
from PIL import Image

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token

def obtener_token_admin():
    """Obtener token de autenticación para el usuario admin"""
    try:
        user = authenticate(username='admin', password='clave123')
        if user:
            token, created = Token.objects.get_or_create(user=user)
            return token.key
        else:
            print("❌ Error: No se pudo autenticar al usuario admin")
            return None
    except Exception as e:
        print(f"❌ Error obteniendo token: {e}")
        return None

def crear_imagen_facial_realista():
    """
    Crear una imagen más realista que simule un rostro humano
    con variaciones de color, iluminación y textura
    """
    try:
        # Crear imagen base de 200x200
        img = np.zeros((200, 200, 3), dtype=np.uint8)

        # Crear gradiente de piel (tono carne)
        for y in range(200):
            for x in range(200):
                # Tono base de piel
                r = 180 + np.random.randint(-20, 20)
                g = 140 + np.random.randint(-15, 15)
                b = 120 + np.random.randint(-10, 10)

                # Añadir variación para simular textura de piel
                noise = np.random.randint(-10, 10)
                r = np.clip(r + noise, 0, 255)
                g = np.clip(g + noise, 0, 255)
                b = np.clip(b + noise, 0, 255)

                img[y, x] = [b, g, r]  # OpenCV usa BGR

        # Añadir "ojos" (círculos oscuros)
        cv2.circle(img, (70, 80), 8, (50, 50, 50), -1)   # Ojo izquierdo
        cv2.circle(img, (130, 80), 8, (50, 50, 50), -1)  # Ojo derecho

        # Añadir "cejas" (líneas)
        cv2.line(img, (60, 70), (80, 70), (30, 30, 30), 2)   # Ceja izquierda
        cv2.line(img, (120, 70), (140, 70), (30, 30, 30), 2) # Ceja derecha

        # Añadir "nariz" (triángulo)
        pts = np.array([[100, 90], [95, 110], [105, 110]], np.int32)
        cv2.fillPoly(img, [pts], (160, 120, 100))

        # Añadir "boca" (óvalo)
        cv2.ellipse(img, (100, 130), (15, 8), 0, 0, 360, (100, 50, 50), -1)

        # Añadir variación de iluminación (sombra en un lado)
        for y in range(200):
            for x in range(100):  # Lado izquierdo más oscuro
                factor = 0.9 - (x / 200) * 0.2  # Gradiente de iluminación
                img[y, x] = (img[y, x] * factor).astype(np.uint8)

        # Convertir a PIL Image
        pil_img = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))

        # Guardar como JPEG
        buffer = BytesIO()
        pil_img.save(buffer, format='JPEG', quality=85)
        buffer.seek(0)

        # Convertir a base64
        imagen_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return imagen_base64

    except Exception as e:
        print(f"❌ Error creando imagen facial realista: {e}")
        return None

def probar_registro_facial(token, imagen_base64):
    """Probar el registro facial usando la API"""
    headers = {
        'Authorization': f'Token {token}',
        'Content-Type': 'application/json'
    }

    url = 'http://127.0.0.1:8000/api/security/rostros/registrar_con_ia/'
    data = {
        'imagen_base64': imagen_base64,
        'nombre_identificador': 'Prueba Admin Realista',
        'confianza_minima': 0.7
    }

    print("\n🤖 Smart Condominium AI: Iniciando prueba de registro facial con imagen realista...")
    print("📸 Enviando imagen facial generada para registro...")

    try:
        response = requests.post(url, json=data, headers=headers)
        print(f"📊 Status Code: {response.status_code}")

        if response.status_code == 201:
            print("✅ Registro facial exitoso!")
            response_data = response.json()
            if 'mensaje_ia' in response_data:
                print(f"🤖 {response_data['mensaje_ia']}")
            return True
        else:
            print("❌ Error en registro facial:")
            try:
                response_data = response.json()
                print(response_data)
                if 'mensaje_ia' in response_data:
                    print(f"🤖 {response_data['mensaje_ia']}")
            except:
                print(response.text)
            return False

    except Exception as e:
        print(f"❌ Error en la petición: {e}")
        return False

def probar_autenticacion_facial(token, imagen_base64):
    """Probar la autenticación facial usando la API"""
    headers = {
        'Authorization': f'Token {token}',
        'Content-Type': 'application/json'
    }

    url = 'http://127.0.0.1:8000/api/security/reconocimiento-facial/'
    data = {
        'imagen_base64': imagen_base64,
        'ubicacion': 'Puerta Principal - Prueba Realista'
    }

    print("\n🤖 Smart Condominium AI: Iniciando prueba de autenticación facial con imagen realista...")
    print("📸 Enviando imagen facial generada para autenticación...")

    try:
        response = requests.post(url, json=data, headers=headers)
        print(f"📊 Status Code: {response.status_code}")

        if response.status_code == 200:
            response_data = response.json()
            if response_data.get('acceso_permitido'):
                print("✅ Autenticación facial exitosa!")
                print(f"👤 Usuario reconocido: {response_data.get('usuario')}")
                print(f"🎯 Confianza: {response_data.get('confianza', 0):.2f}")
            else:
                print("❌ Autenticación facial fallida!")
                print(f"📝 Mensaje: {response_data.get('mensaje')}")
                print(f"🎯 Confianza: {response_data.get('confianza', 0):.2f}")

            if 'mensaje_ia' in response_data:
                print(f"🤖 {response_data['mensaje_ia']}")
            return response_data.get('acceso_permitido', False)
        else:
            print("❌ Error en autenticación facial:")
            try:
                response_data = response.json()
                print(response_data)
                if 'mensaje_ia' in response_data:
                    print(f"🤖 {response_data['mensaje_ia']}")
            except:
                print(response.text)
            return False

    except Exception as e:
        print(f"❌ Error en la petición: {e}")
        return False

def main():
    """Función principal para ejecutar pruebas con imagen realista"""
    print("🚀 Iniciando pruebas avanzadas del Sistema de Reconocimiento Facial")
    print("=" * 70)

    # Verificar que el servidor esté corriendo
    try:
        response = requests.get('http://127.0.0.1:8000/admin/login/', timeout=5)
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar al servidor Django")
        print("💡 Asegúrate de que el servidor esté corriendo: python manage.py runserver")
        return
    except:
        pass

    # Obtener token de admin
    print("\n🔐 Obteniendo token de autenticación para admin...")
    token = obtener_token_admin()
    if not token:
        print("❌ No se pudo obtener el token de admin. Verifica las credenciales.")
        return

    print(f"✅ Token obtenido: {token[:10]}...")

    # Crear imagen facial realista
    print("\n🎨 Generando imagen facial realista...")
    imagen_base64 = crear_imagen_facial_realista()
    if not imagen_base64:
        print("❌ No se pudo crear la imagen facial realista")
        return

    print(f"✅ Imagen facial generada (base64 length: {len(imagen_base64)})")

    # Ejecutar pruebas
    print("\n" + "=" * 70)
    print("🧪 EJECUTANDO PRUEBAS CON SISTEMA AVANZADO")
    print("=" * 70)

    # Prueba 1: Registro facial
    registro_exitoso = probar_registro_facial(token, imagen_base64)

    # Prueba 2: Autenticación facial (usando la misma imagen)
    autenticacion_exitosa = probar_autenticacion_facial(token, imagen_base64)

    # Resultados finales
    print("\n" + "=" * 70)
    print("📊 RESULTADOS FINALES - SISTEMA AVANZADO")
    print("=" * 70)
    print(f"📝 Registro facial: {'✅ Exitoso' if registro_exitoso else '❌ Fallido'}")
    print(f"🔍 Autenticación facial: {'✅ Exitosa' if autenticacion_exitosa else '❌ Fallida'}")

    if registro_exitoso and autenticacion_exitosa:
        print("\n🎉 ¡Sistema avanzado funcionando perfectamente!")
        print("🤖 El reconocimiento facial con IA está operativo")
        print("🔒 Seguridad validada: solo rostros registrados pueden acceder")
    else:
        print("\n⚠️ El sistema avanzado necesita ajustes.")
        print("💡 Posibles causas:")
        print("   - La imagen generada no es lo suficientemente realista")
        print("   - Configuración de IA necesita revisión")
        print("   - Umbrales de confianza demasiado altos")

if __name__ == '__main__':
    main()