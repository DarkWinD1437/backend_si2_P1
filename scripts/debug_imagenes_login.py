#!/usr/bin/env python
import os
import sys
import django
import cv2
import numpy as np
from PIL import Image
import base64
from io import BytesIO
from datetime import datetime

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

def guardar_imagen_debug(imagen_base64, tipo="login"):
    """Guardar imagen para debugging"""
    try:
        # Crear directorio si no existe
        debug_dir = os.path.join(os.path.dirname(__file__), 'debug_images')
        os.makedirs(debug_dir, exist_ok=True)

        # Decodificar imagen
        image_data = base64.b64decode(imagen_base64)
        image = Image.open(BytesIO(image_data))

        # Generar nombre de archivo con timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{tipo}_{timestamp}.jpg"
        filepath = os.path.join(debug_dir, filename)

        # Guardar imagen
        image.save(filepath, 'JPEG')
        print(f"🖼️ Imagen guardada para debug: {filepath}")

        # También guardar como numpy array para análisis
        image_array = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        npy_filepath = os.path.join(debug_dir, f"{tipo}_{timestamp}.npy")
        np.save(npy_filepath, image_array)
        print(f"💾 Array numpy guardado: {npy_filepath}")

        return filepath

    except Exception as e:
        print(f"❌ Error guardando imagen debug: {e}")
        return None

def analizar_imagen_guardada(filepath):
    """Analizar una imagen guardada"""
    try:
        # Cargar imagen
        image_array = np.load(filepath.replace('.jpg', '.npy'))
        print(f"\n🔍 Analizando imagen: {os.path.basename(filepath)}")
        print(f"   Dimensiones: {image_array.shape}")

        # Mostrar preview
        gray = cv2.cvtColor(image_array, cv2.COLOR_BGR2GRAY)
        print(f"   Intensidad media: {gray.mean():.1f}")
        print(f"   Desviación estándar: {gray.std():.1f}")

        # Intentar detectar rostros con diferentes parámetros
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

        print("   Intentando detección de rostros:")

        # Parámetros más agresivos para debugging
        for scale_factor in [1.05, 1.1, 1.2]:
            for min_neighbors in [2, 3, 4, 5]:
                for min_size in [(20, 20), (30, 30), (40, 40)]:
                    faces = face_cascade.detectMultiScale(
                        gray,
                        scaleFactor=scale_factor,
                        minNeighbors=min_neighbors,
                        minSize=min_size,
                        flags=cv2.CASCADE_SCALE_IMAGE
                    )

                    if len(faces) > 0:
                        print(f"   ✅ ¡DETECCIÓN! scale={scale_factor}, neighbors={min_neighbors}, min_size={min_size}: {len(faces)} rostros")
                        for (x, y, w, h) in faces:
                            print(f"      - Posición: ({x}, {y}) Tamaño: {w}x{h}")
                        return True

        print("   ❌ No se detectaron rostros con ningún parámetro")
        return False

    except Exception as e:
        print(f"❌ Error analizando imagen: {e}")
        return False

def procesar_imagenes_debug():
    """Procesar todas las imágenes de debug guardadas"""
    debug_dir = os.path.join(os.path.dirname(__file__), 'debug_images')

    if not os.path.exists(debug_dir):
        print("No hay imágenes de debug guardadas")
        return

    archivos = [f for f in os.listdir(debug_dir) if f.endswith('.npy')]
    archivos.sort(reverse=True)  # Más recientes primero

    print(f"📁 Encontradas {len(archivos)} imágenes de debug")

    for archivo in archivos[:5]:  # Analizar las 5 más recientes
        filepath = os.path.join(debug_dir, archivo)
        analizar_imagen_guardada(filepath)

if __name__ == "__main__":
    procesar_imagenes_debug()