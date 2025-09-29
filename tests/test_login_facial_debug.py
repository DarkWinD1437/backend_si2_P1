#!/usr/bin/env python
import os
import sys
import django
import base64
import cv2
from io import BytesIO
from PIL import Image

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from backend.apps.modulo_ia.models import RostroRegistrado
from backend.apps.modulo_ia.facial_recognition import FacialRecognitionService

def probar_login_facial_con_imagen_prueba():
    print("=== PRUEBA DE LOGIN FACIAL ===")

    # Crear una imagen de prueba simple (un cuadrado gris que simula un rostro)
    img = Image.new('RGB', (200, 200), color=(128, 128, 128))
    buffer = BytesIO()
    img.save(buffer, format='JPEG')
    imagen_base64 = base64.b64encode(buffer.getvalue()).decode()

    print(f"Imagen de prueba creada: {len(imagen_base64)} caracteres base64")

    try:
        # Decodificar imagen
        image_array = FacialRecognitionService.decode_base64_image(imagen_base64)
        print(f"Imagen decodificada: shape={image_array.shape}")

        # Validar calidad
        is_quality_ok, quality_message = FacialRecognitionService.validate_image_quality(image_array)
        print(f"Validación de calidad: {is_quality_ok} - {quality_message}")

        # Verificar características faciales
        has_face_features = FacialRecognitionService.detect_face_features(image_array)
        print(f"¿Tiene características faciales?: {has_face_features}")

        # Intentar extraer embedding
        print("Intentando extraer embedding...")
        try:
            embedding_data = FacialRecognitionService.extract_face_embedding(image_array)
            print(f"✅ Embedding extraído: modelo={embedding_data['model']}, confianza={embedding_data['confidence']}")
            target_embedding = embedding_data['embedding']
        except Exception as e:
            print(f"❌ Error extrayendo embedding: {e}")
            return

        # Buscar mejor coincidencia
        rostros = RostroRegistrado.objects.filter(activo=True)
        print(f"Buscando entre {rostros.count()} rostros registrados...")

        best_match, best_confidence, best_distance = FacialRecognitionService.find_best_match(
            target_embedding, rostros, min_confidence=0.05
        )

        print(f"Resultado: match={best_match.nombre_identificador if best_match else 'None'}, confianza={best_confidence:.3f}, distancia={best_distance:.3f}")

        # Verificar umbrales
        if best_match and best_confidence >= 0.5:  # Umbral del login
            print("✅ Login debería ser exitoso")
        else:
            print("❌ Login fallaría - confianza insuficiente")

    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()

def probar_con_imagen_real():
    print("\n=== PRUEBA CON IMAGEN REAL (simulada) ===")

    # Crear una imagen con más variación (simulando un rostro real)
    import numpy as np

    # Crear imagen con gradiente y ruido (simula un rostro)
    img_array = np.random.randint(50, 200, (300, 300, 3), dtype=np.uint8)

    # Agregar un "rostro" central más claro
    center_y, center_x = 150, 150
    for y in range(center_y-50, center_y+50):
        for x in range(center_x-50, center_x+50):
            if 0 <= y < 300 and 0 <= x < 300:
                # Crear un gradiente circular
                dist = ((y - center_y)**2 + (x - center_x)**2)**0.5
                if dist < 50:
                    factor = 1 - (dist / 50)
                    img_array[y, x] = np.clip(img_array[y, x] * (0.5 + factor * 0.5), 0, 255).astype(np.uint8)

    img = Image.fromarray(img_array)
    buffer = BytesIO()
    img.save(buffer, format='JPEG')
    imagen_base64 = base64.b64encode(buffer.getvalue()).decode()

    print(f"Imagen simulada de rostro creada: {len(imagen_base64)} caracteres base64")

    try:
        # Decodificar imagen
        image_array = FacialRecognitionService.decode_base64_image(imagen_base64)
        print(f"Imagen decodificada: shape={image_array.shape}")

        # Calcular estadísticas básicas
        gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
        std_dev = gray.std()
        print(f"Desviación estándar: {std_dev:.2f}")

        # Validar calidad
        is_quality_ok, quality_message = FacialRecognitionService.validate_image_quality(image_array)
        print(f"Validación de calidad: {is_quality_ok} - {quality_message}")

        # Verificar características faciales
        has_face_features = FacialRecognitionService.detect_face_features(image_array)
        print(f"¿Tiene características faciales?: {has_face_features}")

        # Intentar extraer embedding
        print("Intentando extraer embedding...")
        try:
            embedding_data = FacialRecognitionService.extract_face_embedding(image_array)
            print(f"✅ Embedding extraído: modelo={embedding_data['model']}, confianza={embedding_data['confidence']}")
            target_embedding = embedding_data['embedding']
        except Exception as e:
            print(f"❌ Error extrayendo embedding: {e}")
            return

        # Buscar mejor coincidencia
        rostros = RostroRegistrado.objects.filter(activo=True)
        print(f"Buscando entre {rostros.count()} rostros registrados...")

        best_match, best_confidence, best_distance = FacialRecognitionService.find_best_match(
            target_embedding, rostros, min_confidence=0.05
        )

        print(f"Resultado: match={best_match.nombre_identificador if best_match else 'None'}, confianza={best_confidence:.3f}, distancia={best_distance:.3f}")

        # Verificar umbrales
        if best_match and best_confidence >= 0.5:  # Umbral del login
            print("✅ Login debería ser exitoso")
        else:
            print("❌ Login fallaría - confianza insuficiente")

    except Exception as e:
        print(f"❌ Error general: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    probar_login_facial_con_imagen_prueba()
    probar_con_imagen_real()