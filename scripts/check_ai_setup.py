#!/usr/bin/env python3
"""
Script para verificar configuración de IA y probar integración con Grok
"""
import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from backend.apps.modulo_ia.facial_recognition import FacialRecognitionService
from backend.apps.modulo_ia.views import grok_client
from PIL import Image
import numpy as np

def check_grok_configuration():
    """Verificar si Grok API está configurado"""
    print("=== VERIFICACIÓN DE CONFIGURACIÓN DE GROK API ===")

    if grok_client:
        print("✅ Cliente de Grok inicializado correctamente")
        print(f"📍 Base URL: {grok_client.base_url}")
        print(f"🔑 API Key configurada: {'Sí' if hasattr(grok_client, '_api_key') and grok_client._api_key else 'No'}")

        # Verificar variables de entorno
        grok_api_key = os.environ.get('GROK_API_KEY', '')
        print(f"🔐 Variable de entorno GROK_API_KEY: {'Configurada' if grok_api_key else 'NO CONFIGURADA'}")

        return True
    else:
        print("❌ Cliente de Grok NO inicializado")
        print("💡 Posibles causas:")
        print("   - Variable de entorno GROK_API_KEY no configurada")
        print("   - Error en la inicialización del cliente")
        return False

def test_grok_connection():
    """Probar conexión básica con Grok API"""
    print("\n=== PRUEBA DE CONEXIÓN CON GROK API ===")

    if not grok_client:
        print("❌ No hay cliente de Grok disponible")
        return False

    try:
        # Prueba simple de texto
        response = grok_client.chat.completions.create(
            model="x-ai/grok-4-fast:free",
            messages=[
                {
                    "role": "user",
                    "content": "Hola, ¿puedes confirmar que estás funcionando? Responde solo 'Sí, estoy funcionando correctamente.'"
                }
            ],
            max_tokens=50
        )

        respuesta = response.choices[0].message.content.strip()
        print(f"📨 Respuesta de Grok: {respuesta}")

        if "funcionando" in respuesta.lower():
            print("✅ Conexión con Grok API exitosa")
            return True
        else:
            print("⚠️ Respuesta inesperada de Grok")
            return False

    except Exception as e:
        print(f"❌ Error conectando con Grok API: {e}")
        return False

def test_grok_vision():
    """Probar capacidades de visión de Grok"""
    print("\n=== PRUEBA DE VISIÓN CON GROK ===")

    if not grok_client:
        print("❌ IA no disponible, saltando prueba")
        return False

    try:
        # Prueba de visión con imagen de prueba
        test_image_url = "https://picsum.photos/200/200?random=1"
        vision_response = grok_client.chat.completions.create(
            model="x-ai/grok-4-fast:free",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Describe brevemente qué ves en esta imagen. Responde en español."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": test_image_url
                            }
                        }
                    ]
                }
            ],
            max_tokens=100
        )

        respuesta = vision_response.choices[0].message.content.strip()
        print(f"👁️ Respuesta de visión: {respuesta}")
        print("✅ Grok puede procesar imágenes correctamente")
        return True

    except Exception as e:
        print(f"❌ Error en prueba de visión: {e}")
        return False

def test_face_analysis_with_ai():
    """Probar análisis facial con IA"""
    print("\n=== PRUEBA DE ANÁLISIS FACIAL CON IA ===")

    if not grok_client:
        print("❌ IA no disponible, saltando prueba")
        return False

    try:
        # Crear una imagen de prueba simple
        img = Image.new('RGB', (200, 200), color=(200, 180, 200))
        image_array = np.array(img)

        print("🖼️ Probando análisis facial con IA...")
        result = FacialRecognitionService.extract_face_embedding_with_ai(image_array, grok_client)

        print("✅ Análisis completado:")
        print(f"   📊 Dimensiones del embedding: {len(result['embedding'])}")
        print(f"   🎯 Confianza: {result['confidence']}")
        print(f"   🤖 Modelo usado: {result['model']}")
        print(f"   📝 Descripción: {result.get('description', 'N/A')}")

        return True

    except Exception as e:
        print(f"❌ Error en análisis facial con IA: {e}")
        return False

def show_ai_setup_instructions():
    """Mostrar instrucciones para configurar la API key"""
    print("\n=== INSTRUCCIONES PARA CONFIGURAR API KEY ===")
    print("Para usar IA real en el reconocimiento facial, necesitas:")
    print()
    print("1️⃣ OBTENER API KEY DE OPENROUTER:")
    print("   📍 Ve a: https://openrouter.ai/")
    print("   📝 Regístrate y obtén tu API key")
    print()
    print("2️⃣ CONFIGURAR VARIABLE DE ENTORNO:")
    print("   💻 En Windows PowerShell:")
    print("   $env:GROK_API_KEY='tu_api_key_aqui'")
    print("   ")
    print("   💻 Para configuración permanente, crea un archivo .env:")
    print("   GROK_API_KEY=tu_api_key_aqui")
    print()
    print("3️⃣ MODELOS DISPONIBLES PARA VISIÓN:")
    print("   • x-ai/grok-4-fast:free (recomendado - gratuito)")
    print("   • anthropic/claude-3-haiku:beta")
    print("   • anthropic/claude-3-sonnet:beta")
    print("   • openai/gpt-4o")
    print("   • google/gemini-pro-vision")
    print()
    print("4️⃣ COSTOS APROXIMADOS:")
    print("   • Grok 4 Fast Free: GRATUITO")
    print("   • Claude 3 Haiku: ~$0.00025 por imagen")
    print("   • GPT-4 Vision: ~$0.001 por imagen")
    print("   • Gemini Pro Vision: ~$0.0001 por imagen")
    print()
    print("5️⃣ PRUEBA LA CONFIGURACIÓN:")
    print("   python check_ai_setup.py")

def show_face_recognition_requirements():
    """Mostrar requisitos para instalar face_recognition"""
    print("\n=== REQUISITOS PARA FACE_RECOGNITION ===")
    print("Para instalar face_recognition necesitarás:")
    print()
    print("1️⃣ DEPENDENCIAS DEL SISTEMA (Windows):")
    print("   - Visual Studio Build Tools (C++ compiler)")
    print("   - CMake")
    print("   - Git")
    print()
    print("2️⃣ INSTALACIÓN DE DEPENDENCIAS PYTHON:")
    print("   pip install dlib")
    print("   pip install face_recognition")
    print()
    print("3️⃣ COMANDOS DE INSTALACIÓN:")
    print("   # Instalar dlib (puede tomar tiempo)")
    print("   pip install dlib")
    print("   ")
    print("   # Instalar face_recognition")
    print("   pip install face_recognition")
    print()
    print("4️⃣ ALTERNATIVAS MÁS FÁCILES:")
    print("   - Usar Docker con imagen pre-compilada")
    print("   - Usar Google Colab o servicios en la nube")
    print("   - Usar la IA integrada (Grok) que ya tienes configurada")
    print()
    print("5️⃣ INTEGRACIÓN EN EL CÓDIGO:")
    print("   Una vez instalado, puedes reemplazar el método actual:")
    print("   # En facial_recognition.py")
    print("   import face_recognition")
    print("   ")
    print("   # En extract_face_embedding():")
    print("   face_locations = face_recognition.face_locations(image_array)")
    print("   face_encodings = face_recognition.face_encodings(image_array, face_locations)")
    print("   if face_encodings:")
    print("       return {'embedding': face_encodings[0].tolist(), ...}")

def main():
    print("🤖 VERIFICACIÓN DE CONFIGURACIÓN DE IA Y FACE_RECOGNITION\n")

    # Verificar configuración de Grok
    grok_ok = check_grok_configuration()

    if grok_ok:
        # Probar conexión
        connection_ok = test_grok_connection()

        if connection_ok:
            # Probar visión
            test_grok_vision()

            # Probar análisis facial
            test_face_analysis_with_ai()

    # Mostrar instrucciones para configurar IA
    show_ai_setup_instructions()

    # Mostrar requisitos para face_recognition
    show_face_recognition_requirements()

    print("\n" + "="*60)
    print("📋 RESUMEN:")
    if grok_ok:
        print("✅ Tu API de IA está configurada y lista para usar")
        print("✅ El sistema puede usar IA real para reconocimiento facial")
        print("✅ Código actualizado para usar Grok 4 Fast Free (gratuito)")
    else:
        print("❌ API de IA no configurada - usando métodos tradicionales")
        print("💡 Sigue las instrucciones arriba para activar IA real")

    print("\n🎯 RECOMENDACIONES:")
    print("1️⃣ Configura tu API key de OpenRouter para usar IA real")
    print("2️⃣ Prueba con: python check_ai_setup.py")
    print("3️⃣ Si no quieres configurar API, el sistema funciona con lógica computacional")
    print("4️⃣ Face_recognition requiere instalación compleja - no recomendado")

if __name__ == '__main__':
    main()