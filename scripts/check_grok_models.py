#!/usr/bin/env python3
"""
Script para verificar modelos disponibles en OpenRouter
"""
import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from openai import OpenAI

def check_available_models():
    """Verificar modelos disponibles en OpenRouter"""
    print("🔍 VERIFICANDO MODELOS DISPONIBLES EN OPENROUTER\n")

    # Simular API key para listar modelos
    client = OpenAI(
        api_key="sk-or-v1-simulated-key-for-listing",
        base_url="https://openrouter.ai/api/v1"
    )

    try:
        # Intentar listar modelos
        response = client.models.list()
        print("✅ Modelos disponibles:")

        grok_models = []
        vision_models = []

        for model in response.data:
            model_id = model.id.lower()

            # Buscar modelos de Grok
            if 'grok' in model_id:
                grok_models.append(model.id)

            # Buscar modelos con capacidades de visión
            if hasattr(model, 'description') and model.description:
                desc = model.description.lower()
                if 'vision' in desc or 'image' in desc or 'visual' in desc:
                    vision_models.append(model.id)

        print(f"\n🤖 MODELOS DE GROK ENCONTRADOS ({len(grok_models)}):")
        for model in grok_models:
            print(f"   • {model}")

        print(f"\n👁️ MODELOS CON CAPACIDADES DE VISIÓN ({len(vision_models)}):")
        for model in vision_models:
            print(f"   • {model}")

        # Verificar específicamente Grok 4 Fast
        grok_fast_found = any('grok-4-fast' in model.lower() for model in grok_models)
        print(f"\n🎯 GROK 4 FAST: {'✅ ENCONTRADO' if grok_fast_found else '❌ NO ENCONTRADO'}")

        # Verificar si tiene visión
        grok_vision_found = any('grok' in model.lower() and ('vision' in model.lower() or 'beta' in model.lower()) for model in vision_models)
        print(f"🎯 GROK CON VISIÓN: {'✅ DISPONIBLE' if grok_vision_found else '❌ NO DISPONIBLE'}")

        return grok_models, vision_models

    except Exception as e:
        print(f"❌ Error consultando modelos: {e}")
        print("\n💡 Posibles causas:")
        print("   • API key inválida (pero para listar modelos no debería importar)")
        print("   • Problemas de conexión")
        print("   • OpenRouter API cambió")

        return [], []

def show_grok_models_info():
    """Mostrar información sobre modelos de Grok"""
    print("\n" + "="*60)
    print("📚 INFORMACIÓN SOBRE MODELOS DE GROK:")
    print("="*60)

    models_info = {
        "x-ai/grok-4-fast:free": {
            "vision": False,
            "costo": "Gratis (limitado)",
            "notas": "Modelo de texto, NO tiene capacidades de visión"
        },
        "x-ai/grok-4o": {
            "vision": True,
            "costo": "~$0.001 por imagen",
            "notas": "Modelo con capacidades de visión (recomendado)"
        },
        "x-ai/grok-vision-beta": {
            "vision": True,
            "costo": "~$0.001 por imagen",
            "notas": "Versión beta con visión (puede no estar disponible)"
        }
    }

    for model, info in models_info.items():
        vision_icon = "👁️" if info["vision"] else "📝"
        print(f"\n{model}:")
        print(f"   {vision_icon} Visión: {'SÍ' if info['vision'] else 'NO'}")
        print(f"   💰 Costo: {info['costo']}")
        print(f"   📝 Notas: {info['notas']}")

def main():
    grok_models, vision_models = check_available_models()
    show_grok_models_info()

    print("\n" + "="*60)
    print("🎯 CONCLUSIONES:")
    print("="*60)

    if any('grok-4-fast' in model.lower() for model in grok_models):
        print("✅ Grok 4 Fast está disponible en OpenRouter")
        print("❌ PERO: Grok 4 Fast NO tiene capacidades de visión")
        print("💡 Para reconocimiento facial necesitas un modelo con visión")
    else:
        print("❌ Grok 4 Fast no encontrado en OpenRouter")

    print("\n🔄 RECOMENDACIONES:")
    print("1️⃣ Para visión: Usa 'x-ai/grok-4o' o Claude 3 Haiku")
    print("2️⃣ Para texto: Usa 'x-ai/grok-4-fast:free'")
    print("3️⃣ Costo típico: $0.00025-0.001 por análisis facial")

if __name__ == '__main__':
    main()