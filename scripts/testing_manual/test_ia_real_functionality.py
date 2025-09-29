#!/usr/bin/env python
"""
Script de prueba para el módulo de seguridad con IA
Prueba el registro y autenticación facial usando Grok Vision API de xAI
Usuario: admin / clave123
"""

import os
import sys
import django
import base64
import requests
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

def crear_imagen_prueba_base64():
    """Crear una imagen de prueba simple y convertirla a base64"""
    try:
        # Crear una imagen simple de 100x100 píxeles
        img = Image.new('RGB', (100, 100), color='red')
        buffer = BytesIO()
        img.save(buffer, format='JPEG')
        buffer.seek(0)

        # Convertir a base64
        imagen_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        return imagen_base64
    except Exception as e:
        print(f"❌ Error creando imagen de prueba: {e}")
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
        'nombre_identificador': 'Prueba Admin',
        'confianza_minima': 0.7
    }

    print("\n🤖 Smart Condominium AI: Iniciando prueba de registro facial...")
    print("📸 Enviando imagen para registro...")

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
        'ubicacion': 'Puerta Principal - Prueba'
    }

    print("\n🤖 Smart Condominium AI: Iniciando prueba de autenticación facial...")
    print("📸 Enviando imagen para autenticación...")

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

def probar_lectura_placa(token, imagen_base64):
    """Probar la lectura de placa usando la API"""
    headers = {
        'Authorization': f'Token {token}',
        'Content-Type': 'application/json'
    }

    url = 'http://127.0.0.1:8000/api/security/lectura-placa/'
    data = {
        'imagen_base64': imagen_base64,
        'ubicacion': 'Entrada Vehicular - Prueba'
    }

    print("\n🤖 Smart Condominium AI: Iniciando prueba de lectura de placa...")
    print("🚗 Enviando imagen de placa para análisis...")

    try:
        response = requests.post(url, json=data, headers=headers)
        print(f"📊 Status Code: {response.status_code}")

        if response.status_code == 200:
            response_data = response.json()
            if response_data.get('acceso_permitido'):
                print("✅ Placa reconocida exitosamente!")
                print(f"🔢 Placa: {response_data.get('placa')}")
                print(f"🚙 Vehículo: {response_data.get('vehiculo')}")
                print(f"👤 Propietario: {response_data.get('usuario')}")
            else:
                print("❌ Placa no reconocida!")
                print(f"📝 Mensaje: {response_data.get('mensaje')}")
                if 'placa_detectada' in response_data:
                    print(f"🔍 Placa detectada: {response_data['placa_detectada']}")

            if 'mensaje_ia' in response_data:
                print(f"🤖 {response_data['mensaje_ia']}")
            return response_data.get('acceso_permitido', False)
        else:
            print("❌ Error en lectura de placa:")
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
    """Función principal para ejecutar todas las pruebas"""
    print("🚀 Iniciando pruebas del Módulo de Seguridad con IA")
    print("=" * 60)

    # Verificar que el servidor esté corriendo
    try:
        response = requests.get('http://127.0.0.1:8000/admin/login/', timeout=5)
        # Si llega aquí, el servidor está corriendo (aunque admin/login/ pueda requerir auth)
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se puede conectar al servidor Django")
        print("💡 Asegúrate de que el servidor esté corriendo: python manage.py runserver")
        return
    except:
        # Si hay otro error (como 404), asumimos que el servidor está corriendo
        pass

    # Obtener token de admin
    print("\n🔐 Obteniendo token de autenticación para admin...")
    token = obtener_token_admin()
    if not token:
        print("❌ No se pudo obtener el token de admin. Verifica las credenciales.")
        return

    print(f"✅ Token obtenido: {token[:10]}...")

    # Crear imagen de prueba
    print("\n🖼️ Creando imagen de prueba...")
    imagen_base64 = crear_imagen_prueba_base64()
    if not imagen_base64:
        print("❌ No se pudo crear la imagen de prueba")
        return

    print(f"✅ Imagen creada (base64 length: {len(imagen_base64)})")

    # Ejecutar pruebas
    print("\n" + "=" * 60)
    print("🧪 EJECUTANDO PRUEBAS")
    print("=" * 60)

    # Prueba 1: Registro facial
    registro_exitoso = probar_registro_facial(token, imagen_base64)

    # Prueba 2: Autenticación facial
    autenticacion_exitosa = probar_autenticacion_facial(token, imagen_base64)

    # Prueba 3: Lectura de placa
    placa_exitosa = probar_lectura_placa(token, imagen_base64)

    # Resultados finales
    print("\n" + "=" * 60)
    print("📊 RESULTADOS FINALES")
    print("=" * 60)
    print(f"📝 Registro facial: {'✅ Exitoso' if registro_exitoso else '❌ Fallido'}")
    print(f"🔍 Autenticación facial: {'✅ Exitosa' if autenticacion_exitosa else '❌ Fallida'}")
    print(f"🚗 Lectura de placa: {'✅ Exitosa' if placa_exitosa else '❌ Fallida'}")

    if registro_exitoso and autenticacion_exitosa:
        print("\n🎉 ¡Todas las pruebas de IA pasaron exitosamente!")
        print("🤖 Smart Condominium AI está funcionando correctamente con Grok Vision API de xAI")
    else:
        print("\n⚠️ Algunas pruebas fallaron. Revisa los logs para más detalles.")
        print("💡 Asegúrate de que:")
        print("   - La API key de Grok esté configurada correctamente")
        print("   - El servidor Django esté corriendo")
        print("   - Las dependencias estén instaladas")

if __name__ == '__main__':
    main()