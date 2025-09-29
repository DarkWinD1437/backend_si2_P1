#!/usr/bin/env python
"""
Script de debug para probar comparación de embeddings
"""

import os
import sys
import django
import base64
import cv2
import numpy as np
from io import BytesIO
from PIL import Image

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from backend.apps.modulo_ia.models import RostroRegistrado
from backend.apps.modulo_ia.facial_recognition import FacialRecognitionService
from django.contrib.auth import get_user_model

def crear_imagen_facial_realista():
    """Crear la misma imagen de prueba que usamos antes"""
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

def debug_embedding_comparison():
    """Debug detallado de comparación de embeddings"""
    print("🔍 DEBUG: Comparación de Embeddings")
    print("=" * 50)

    # Obtener el rostro registrado más reciente
    try:
        rostro_registrado = RostroRegistrado.objects.filter(
            nombre_identificador='Prueba Admin Realista',
            activo=True
        ).first()

        if not rostro_registrado:
            print("❌ No se encontró el rostro registrado 'Prueba Admin Realista'")
            return

        print(f"✅ Rostro encontrado: {rostro_registrado.nombre_identificador}")
        print(f"   ID: {rostro_registrado.id}")
        print(f"   Modelo guardado: {rostro_registrado.embedding_ia.get('modelo', 'N/A')}")

        stored_embedding = rostro_registrado.embedding_ia.get('vector', [])
        print(f"   Embedding guardado: {len(stored_embedding)} dimensiones")
        if stored_embedding:
            print(f"   Primeros 5 valores: {stored_embedding[:5]}")
            print(f"   Rango: {min(stored_embedding):.3f} a {max(stored_embedding):.3f}")

        # Crear la misma imagen de prueba
        print("\n🖼️ Generando imagen de prueba idéntica...")
        imagen_base64 = crear_imagen_facial_realista()
        if not imagen_base64:
            return

        print(f"✅ Imagen generada: {len(imagen_base64)} caracteres base64")

        # Extraer embedding de la imagen de prueba usando el mismo método que en login
        print("\n🧠 Extrayendo embedding de imagen de prueba...")
        try:
            image_array = FacialRecognitionService.decode_base64_image(imagen_base64)
            print(f"   Imagen decodificada: {image_array.shape}")

            # Usar el mismo método que se usa en login
            embedding_data = FacialRecognitionService.extract_face_embedding(image_array)
            target_embedding = embedding_data['embedding']

            print(f"   Embedding extraído: {len(target_embedding)} dimensiones")
            print(f"   Modelo usado: {embedding_data.get('model', 'N/A')}")
            print(f"   Confianza: {embedding_data.get('confidence', 'N/A')}")
            print(f"   Primeros 5 valores: {target_embedding[:5]}")
            print(f"   Rango: {min(target_embedding):.3f} a {max(target_embedding):.3f}")

        except Exception as e:
            print(f"❌ Error extrayendo embedding: {e}")
            return

        # Comparar embeddings
        print("\n⚖️ Comparando embeddings...")
        try:
            comparison = FacialRecognitionService.compare_faces(target_embedding, stored_embedding)
            print(f"   Resultado comparación:")
            print(f"   - Match: {comparison['match']}")
            print(f"   - Confianza: {comparison['confidence']:.4f}")
            print(f"   - Similitud: {comparison['similarity']:.4f}")
            print(f"   - Distancia: {comparison['distance']:.4f}")

            # Comparación detallada
            print("\n📊 Análisis detallado:")
            print(f"   - Confianza requerida para login: 0.75")
            print(f"   - Confianza obtenida: {comparison['confidence']:.4f}")
            print(f"   - ¿Pasa umbral?: {'✅ SÍ' if comparison['confidence'] >= 0.75 else '❌ NO'}")

        except Exception as e:
            print(f"❌ Error en comparación: {e}")
            import traceback
            traceback.print_exc()

    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()

def main():
    debug_embedding_comparison()

if __name__ == '__main__':
    main()