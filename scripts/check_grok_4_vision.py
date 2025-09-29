#!/usr/bin/env python3
"""
Script para verificar si el modelo Grok 4 tiene capacidades de visión
y probar la integración con OpenRouter
"""

import os
import sys
import requests
import json
from pathlib import Path

# Agregar el directorio del proyecto al path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def check_grok_4_vision():
    """Verificar si Grok 4 tiene capacidades de visión"""
    api_key = os.getenv('OPENROUTER_API_KEY')

    if not api_key:
        print("❌ No se encontró OPENROUTER_API_KEY en las variables de entorno")
        return False

    try:
        # Verificar modelos disponibles
        models_url = "https://openrouter.ai/api/v1/models"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        print("🔍 Consultando modelos disponibles en OpenRouter...")
        response = requests.get(models_url, headers=headers)

        if response.status_code != 200:
            print(f"❌ Error consultando modelos: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return False

        models_data = response.json()
        models = models_data.get('data', [])

        # Buscar modelos de Grok
        grok_models = [model for model in models if 'grok' in model['id'].lower()]

        print(f"\n🤖 Modelos de Grok encontrados: {len(grok_models)}")
        for model in grok_models:
            model_id = model['id']
            supports_vision = 'vision' in str(model.get('modalities', [])).lower() or 'image' in str(model.get('description', '')).lower()
            print(f"  - {model_id}: {'✅ Visión soportada' if supports_vision else '❌ Solo texto'}")

        # Verificar específicamente Grok 4
        grok_4_model = next((model for model in grok_models if 'grok-4' in model['id']), None)

        if grok_4_model:
            print(f"\n🎯 Modelo Grok 4 encontrado: {grok_4_model['id']}")
            modalities = grok_4_model.get('modalities', [])
            description = grok_4_model.get('description', '')

            has_vision = 'vision' in modalities or 'image' in modalities
            print(f"  - Modalidades: {modalities}")
            print(f"  - Descripción: {description[:100]}...")
            print(f"  - ¿Soporta visión?: {'✅ SÍ' if has_vision else '❌ NO'}")

            if has_vision:
                print("\n✅ ¡Excelente! Grok 4 tiene capacidades de visión.")
                print("El sistema puede usar IA real para reconocimiento facial.")
                return True
            else:
                print("\n⚠️  Grok 4 NO tiene capacidades de visión.")
                print("Necesitas usar un modelo diferente como:")
                vision_models = [model for model in models if 'vision' in str(model.get('modalities', [])).lower()]
                for model in vision_models[:5]:  # Mostrar primeros 5
                    print(f"  - {model['id']}")
                return False
        else:
            print("\n❌ No se encontró el modelo Grok 4")
            return False

    except Exception as e:
        print(f"❌ Error verificando capacidades de visión: {e}")
        return False

def test_grok_4_vision():
    """Probar una llamada simple a Grok 4 con imagen"""
    api_key = os.getenv('OPENROUTER_API_KEY')

    if not api_key:
        print("❌ No se encontró OPENROUTER_API_KEY")
        return

    try:
        # Crear una imagen de prueba simple (un cuadrado rojo)
        from PIL import Image, ImageDraw
        import base64
        import io

        # Crear imagen de prueba
        img = Image.new('RGB', (100, 100), color='red')
        draw = ImageDraw.Draw(img)
        draw.rectangle([25, 25, 75, 75], fill='blue')

        # Convertir a base64
        buffer = io.BytesIO()
        img.save(buffer, format='JPEG')
        img_base64 = base64.b64encode(buffer.getvalue()).decode()

        # Hacer llamada de prueba
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "x-ai/grok-4",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Describe esta imagen en una sola oración."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{img_base64}"
                            }
                        }
                    ]
                }
            ],
            "max_tokens": 100
        }

        print("\n🧪 Probando llamada a Grok 4 con imagen...")
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            print("✅ Respuesta exitosa:"            print(f"   {content}")
            return True
        else:
            print(f"❌ Error en la llamada: {response.status_code}")
            print(f"Respuesta: {response.text}")
            return False

    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Verificando capacidades de visión de Grok 4\n")

    # Verificar capacidades
    has_vision = check_grok_4_vision()

    if has_vision:
        # Probar llamada
        test_grok_4_vision()
    else:
        print("\n💡 Recomendaciones:")
        print("1. Usa un modelo con visión como 'anthropic/claude-3-haiku:beta'")
        print("2. O instala face_recognition: pip install face-recognition")
        print("3. Verifica tu API key y créditos en OpenRouter")

    print("\n✨ Verificación completada.")