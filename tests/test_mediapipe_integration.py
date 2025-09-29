#!/usr/bin/env python3
"""
Script de prueba para validar el sistema avanzado de reconocimiento facial con MediaPipe
"""

import sys
import os
import base64
from PIL import Image
import numpy as np

# Agregar el directorio del proyecto al path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.apps.modulo_ia.advanced_facial_recognition import AdvancedFacialRecognition

def test_mediapipe_integration():
    """Probar la integración de MediaPipe en el sistema avanzado"""
    print("🧪 Probando integración de MediaPipe en el sistema de reconocimiento facial...")

    try:
        # Inicializar sistema avanzado
        system = AdvancedFacialRecognition()

        # Crear una imagen de prueba simple (cara básica)
        test_image = np.zeros((200, 200, 3), dtype=np.uint8)
        # Dibujar un óvalo simple para simular un rostro
        cv2 = __import__('cv2')
        center = (100, 100)
        axes = (40, 60)
        cv2.ellipse(test_image, center, axes, 0, 0, 360, (200, 180, 150), -1)

        # Agregar algunos detalles
        cv2.circle(test_image, (85, 90), 5, (0, 0, 0), -1)  # Ojo izquierdo
        cv2.circle(test_image, (115, 90), 5, (0, 0, 0), -1)  # Ojo derecho
        cv2.ellipse(test_image, (100, 120), (10, 5), 0, 0, 360, (150, 50, 50), -1)  # Boca

        print("📸 Imagen de prueba creada")

        # Probar procesamiento
        result = system.process_single_frame(test_image)

        print(f"✅ Resultado del procesamiento: {result['success']}")
        print(f"🔍 Rostro detectado: {result['face_detected']}")
        print(f"📍 Método de detección: {result.get('detection_method', 'unknown')}")
        print(f"📊 Score de calidad: {result['quality_score']:.3f}")

        if result['success'] and result['face_crop'] is not None:
            # Probar creación de embedding
            embedding = system.create_embedding_from_crop(result['face_crop'])
            print(f"🧬 Embedding creado con {len(embedding)} dimensiones")

            # Probar comparación consigo mismo
            comparison = system.compare_embeddings(embedding, embedding)
            print(f"🔄 Comparación consigo mismo: confianza={comparison['confidence']:.3f}")

            return True
        else:
            print(f"❌ Error: {result.get('error', 'Error desconocido')}")
            return False

    except Exception as e:
        print(f"❌ Error en la prueba: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_image_quality_validation():
    """Probar validación de calidad de imagen"""
    print("\n🧪 Probando validación de calidad de imagen...")

    try:
        system = AdvancedFacialRecognition()

        # Imagen válida
        good_image = np.full((200, 200, 3), 128, dtype=np.uint8)
        valid, msg = system.validate_image_quality(good_image)
        print(f"✅ Imagen válida: {valid} - {msg}")

        # Imagen demasiado pequeña
        small_image = np.full((50, 50, 3), 128, dtype=np.uint8)
        valid, msg = system.validate_image_quality(small_image)
        print(f"❌ Imagen pequeña: {valid} - {msg}")

        # Imagen uniforme
        uniform_image = np.full((200, 200, 3), 0, dtype=np.uint8)
        valid, msg = system.validate_image_quality(uniform_image)
        print(f"❌ Imagen uniforme: {valid} - {msg}")

        return True

    except Exception as e:
        print(f"❌ Error en validación de calidad: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Iniciando pruebas del sistema avanzado de reconocimiento facial con MediaPipe")
    print("=" * 70)

    success1 = test_mediapipe_integration()
    success2 = test_image_quality_validation()

    print("\n" + "=" * 70)
    if success1 and success2:
        print("🎉 Todas las pruebas pasaron exitosamente!")
        print("✅ MediaPipe está integrado correctamente en el sistema")
    else:
        print("⚠️ Algunas pruebas fallaron. Revisa los logs anteriores.")
        sys.exit(1)