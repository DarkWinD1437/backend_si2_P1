#!/usr/bin/env python
import os
import sys
import django
import cv2
import numpy as np
from PIL import Image
import base64
from io import BytesIO

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from backend.apps.modulo_ia.models import RostroRegistrado
from backend.apps.modulo_ia.facial_recognition import FacialRecognitionService

def analizar_imagen_login(imagen_base64):
    """Analizar exactamente la misma imagen que llega al login facial"""
    print("=== ANÁLISIS DETALLADO DE IMAGEN DE LOGIN ===")

    try:
        # 1. Decodificar imagen (exactamente como lo hace el sistema)
        print("1. Decodificando imagen base64...")
        image_array = FacialRecognitionService.decode_base64_image(imagen_base64)
        print(f"   ✅ Imagen decodificada: shape={image_array.shape}, dtype={image_array.dtype}")

        # 2. Validar calidad básica
        print("\n2. Validando calidad básica...")
        is_quality_ok, quality_message = FacialRecognitionService.validate_image_quality(image_array)
        print(f"   Resultado: {'✅ PASA' if is_quality_ok else '❌ FALLA'} - {quality_message}")

        if not is_quality_ok:
            print("   ❌ IMAGEN RECHAZADA POR CALIDAD")
            return False

        # 3. Convertir a escala de grises y analizar estadísticas
        print("\n3. Analizando estadísticas de imagen...")
        gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
        mean_intensity = gray.mean()
        std_intensity = gray.std()
        min_intensity = gray.min()
        max_intensity = gray.max()

        print(f"   Intensidad - Media: {mean_intensity:.1f}, Desv: {std_intensity:.1f}, Min: {min_intensity}, Max: {max_intensity}")

        # 4. Verificar si tiene características faciales tradicionales
        print("\n4. Verificando características faciales tradicionales...")
        has_face_features = FacialRecognitionService.detect_face_features_traditional(image_array)
        print(f"   ¿Tiene características faciales?: {has_face_features}")

        # 5. Intentar detección con OpenCV directamente
        print("\n5. Intentando detección OpenCV directa...")
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        # Probar diferentes parámetros
        for scale_factor in [1.1, 1.2, 1.3]:
            for min_neighbors in [3, 5, 7]:
                faces = face_cascade.detectMultiScale(
                    gray,
                    scaleFactor=scale_factor,
                    minNeighbors=min_neighbors,
                    minSize=(20, 20),
                    flags=cv2.CASCADE_SCALE_IMAGE
                )
                print(f"   Parámetros scale={scale_factor}, neighbors={min_neighbors}: {len(faces)} rostros detectados")
                if len(faces) > 0:
                    for (x, y, w, h) in faces:
                        print(f"     - Rostro en ({x}, {y}) tamaño {w}x{h}")

        # 6. Verificar si la imagen tiene suficiente contraste/variación
        print("\n6. Verificando contraste y variación...")
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        hist = hist.flatten()

        # Calcular entropía de la imagen
        hist_norm = hist / hist.sum()
        entropy = -np.sum(hist_norm * np.log2(hist_norm + 1e-10))
        print(f"   Entropía: {entropy:.2f} (valores altos indican más información/variación)")

        # 7. Verificar si es una imagen uniforme (problema común)
        print("\n7. Verificando si es imagen uniforme...")
        if std_intensity < 10:
            print("   ❌ IMAGEN MUY UNIFORME - Probablemente negra/blanca/vacía")
            return False

        # 8. Mostrar información de debug adicional
        print("\n8. Información adicional de debug:")
        print(f"   Dimensiones: {image_array.shape}")
        print(f"   Canales: {image_array.shape[2] if len(image_array.shape) > 2 else 1}")
        print(f"   Rango de valores RGB: R({image_array[:,:,0].min()}-{image_array[:,:,0].max()}), G({image_array[:,:,1].min()}-{image_array[:,:,1].max()}), B({image_array[:,:,2].min()}-{image_array[:,:,2].max()})")

        # 9. Intentar el proceso completo de extracción de embedding
        print("\n9. Intentando extracción completa de embedding...")
        try:
            embedding_data = FacialRecognitionService.extract_face_embedding(image_array)
            print(f"   ✅ Embedding extraído: modelo={embedding_data['model']}, confianza={embedding_data['confidence']}")
            target_embedding = embedding_data['embedding']

            # 10. Comparar con rostros registrados
            print("\n10. Comparando con rostros registrados...")
            rostros = RostroRegistrado.objects.filter(activo=True)
            print(f"    Rostros registrados: {rostros.count()}")

            best_match, best_confidence, best_distance = FacialRecognitionService.find_best_match(
                target_embedding, rostros, min_confidence=0.05
            )

            print(f"    Mejor coincidencia: {best_match.nombre_identificador if best_match else 'Ninguna'}")
            print(f"    Confianza: {best_confidence:.3f}, Distancia: {best_distance:.3f}")

            if best_match and best_confidence >= 0.5:
                print("    ✅ LOGIN DEBERÍA SER EXITOSO")
                return True
            else:
                print("    ❌ LOGIN FALLARÍA - Confianza insuficiente")
                return False

        except Exception as e:
            print(f"   ❌ Error en extracción de embedding: {e}")
            return False

    except Exception as e:
        print(f"❌ Error general analizando imagen: {e}")
        import traceback
        traceback.print_exc()
        return False

def crear_imagen_test_realista():
    """Crear una imagen más realista que simule una captura de webcam"""
    print("\n=== CREANDO IMAGEN DE PRUEBA REALISTA ===")

    # Crear imagen con fondo y rostro simulado
    img = np.random.randint(180, 220, (480, 640, 3), dtype=np.uint8)  # Fondo claro

    # Agregar ruido para simular webcam
    noise = np.random.normal(0, 10, img.shape).astype(np.uint8)
    img = cv2.add(img, noise)

    # Crear un "rostro" ovalado más realista
    center_y, center_x = 240, 320
    face_size = 120

    # Crear máscara ovalada para el rostro
    mask = np.zeros((480, 640), dtype=np.uint8)
    cv2.ellipse(mask, (center_x, center_y), (face_size, face_size), 0, 0, 360, 255, -1)

    # Aplicar tono de piel al rostro
    skin_tone = np.random.randint(200, 240, (480, 640, 3), dtype=np.uint8)
    skin_tone = cv2.add(skin_tone, np.random.normal(0, 15, (480, 640, 3)).astype(np.uint8))

    # Combinar fondo y rostro
    img = np.where(mask[:, :, np.newaxis] > 0, skin_tone, img)

    # Agregar rasgos faciales
    # Ojos
    cv2.circle(img, (center_x-30, center_y-20), 8, (0, 0, 0), -1)
    cv2.circle(img, (center_x+30, center_y-20), 8, (0, 0, 0), -1)

    # Boca
    cv2.ellipse(img, (center_x, center_y+30), (20, 10), 0, 0, 180, (0, 0, 0), -1)

    # Convertir a base64
    pil_img = Image.fromarray(img)
    buffer = BytesIO()
    pil_img.save(buffer, format='JPEG', quality=85)  # Calidad típica de webcam
    imagen_base64 = base64.b64encode(buffer.getvalue()).decode()

    print(f"Imagen realista creada: {len(imagen_base64)} caracteres base64")

    # Analizar esta imagen
    return analizar_imagen_login(imagen_base64)

if __name__ == "__main__":
    # Probar con imagen realista
    crear_imagen_test_realista()