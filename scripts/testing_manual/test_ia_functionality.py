#!/usr/bin/env python
"""
Script de prueba para funcionalidades de IA del Módulo de Seguridad
Prueba la integración con OpenAI Vision API
"""

import os
import sys
import django
import base64
from io import BytesIO
from PIL import Image, ImageDraw, ImageFont

# Configurar Django
sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.conf import settings
from backend.apps.modulo_ia.views import _extraer_caracteristicas_faciales_real, _extraer_texto_placa

def crear_imagen_prueba_placa(texto_placa):
    """Crear una imagen simple con texto de placa para pruebas"""
    # Crear imagen blanca
    img = Image.new('RGB', (300, 100), color='white')
    draw = ImageDraw.Draw(img)

    # Intentar usar fuente por defecto
    try:
        font = ImageFont.truetype("arial.ttf", 40)
    except:
        font = ImageFont.load_default()

    # Dibujar texto
    draw.text((50, 30), texto_placa, fill='black', font=font)

    # Convertir a base64
    buffer = BytesIO()
    img.save(buffer, format='JPEG')
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.getvalue()).decode()

    return img_base64

def crear_imagen_prueba_rostro():
    """Crear una imagen simple que simule un rostro para pruebas"""
    # Crear imagen con forma ovalada (simulando rostro)
    img = Image.new('RGB', (200, 200), color='lightblue')
    draw = ImageDraw.Draw(img)

    # Dibujar óvalo para simular rostro
    draw.ellipse([50, 50, 150, 150], fill='peachpuff', outline='black', width=2)

    # Dibujar ojos
    draw.ellipse([70, 80, 90, 100], fill='white')
    draw.ellipse([110, 80, 130, 100], fill='white')
    draw.ellipse([75, 85, 85, 95], fill='black')
    draw.ellipse([115, 85, 125, 95], fill='black')

    # Dibujar boca
    draw.arc([80, 110, 120, 130], start=0, end=180, fill='black', width=2)

    # Convertir a base64
    buffer = BytesIO()
    img.save(buffer, format='JPEG')
    buffer.seek(0)
    img_base64 = base64.b64encode(buffer.getvalue()).decode()

    return img_base64

def probar_ocr_placa():
    """Probar funcionalidad de OCR para placas"""
    print("🧪 Probando OCR de placas vehiculares...")

    # Crear imagen de prueba
    placa_test = "1234ABC"
    img_base64 = crear_imagen_prueba_placa(placa_test)

    print(f"📸 Imagen de placa creada: {placa_test}")

    # Probar extracción
    try:
        texto_extraido = _extraer_texto_placa(img_base64)
        print(f"🤖 Texto extraído por IA: {texto_extraido}")

        if texto_extraido == placa_test:
            print("✅ ¡OCR funcionó correctamente!")
        else:
            print(f"⚠️  OCR funcionó pero extrajo: {texto_extraido}")

    except Exception as e:
        print(f"❌ Error en OCR: {e}")

def probar_reconocimiento_facial():
    """Probar funcionalidad de reconocimiento facial"""
    print("\n🧪 Probando reconocimiento facial...")

    # Crear imagen de prueba
    img_base64 = crear_imagen_prueba_rostro()
    print("📸 Imagen de rostro simulada creada")

    # Probar extracción de características
    try:
        embedding = _extraer_caracteristicas_faciales_real(img_base64)

        if isinstance(embedding, list) and len(embedding) == 512:
            print("✅ ¡Extracción de características faciales exitosa!")
            print(f"📊 Vector de {len(embedding)} dimensiones generado")
            print(f"🔢 Primeros 5 valores: {embedding[:5]}")
        else:
            print(f"⚠️  Extracción completada pero formato inesperado: {type(embedding)}")

    except Exception as e:
        print(f"❌ Error en reconocimiento facial: {e}")

def verificar_configuracion():
    """Verificar configuración de OpenAI"""
    print("🔧 Verificando configuración...")

    if settings.OPENAI_API_KEY:
        print("✅ OPENAI_API_KEY configurada")
        # Mostrar primeros y últimos caracteres por seguridad
        key = settings.OPENAI_API_KEY
        print(f"🔑 API Key: {key[:10]}...{key[-4:] if len(key) > 14 else key}")
    else:
        print("⚠️  OPENAI_API_KEY no configurada - funcionando en modo simulado")
        print("💡 Para usar IA real, agrega OPENAI_API_KEY a tu archivo .env")

def main():
    """Función principal de pruebas"""
    print("🚀 PRUEBA DE FUNCIONALIDADES DE IA - MÓDULO DE SEGURIDAD")
    print("=" * 60)

    verificar_configuracion()
    print()

    probar_ocr_placa()
    probar_reconocimiento_facial()

    print("\n" + "=" * 60)
    print("✅ Pruebas completadas!")

if __name__ == "__main__":
    main()