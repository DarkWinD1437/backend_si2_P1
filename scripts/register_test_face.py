#!/usr/bin/env python3
"""
Script para registrar un rostro de prueba
"""

import os
import sys
import django
import numpy as np
import cv2
from PIL import Image
import io
import base64

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from backend.apps.modulo_ia.models import RostroRegistrado
from backend.apps.modulo_ia.facial_recognition import FacialRecognitionService
from django.contrib.auth import get_user_model
from django.utils import timezone

def main():
    # Obtener usuario admin
    User = get_user_model()
    admin_user = User.objects.get(username='admin')

    # Crear imagen de prueba más simple (cara básica)
    image = np.full((400, 400, 3), (200, 180, 160), dtype=np.uint8)  # Color de piel uniforme
    
    # Dibujar un óvalo simple para el rostro
    cv2.ellipse(image, (200, 200), (100, 120), 0, 0, 360, (210, 190, 170), -1)
    
    # Ojos simples
    cv2.circle(image, (170, 180), 10, (255, 255, 255), -1)
    cv2.circle(image, (170, 180), 5, (0, 0, 0), -1)
    cv2.circle(image, (230, 180), 10, (255, 255, 255), -1)
    cv2.circle(image, (230, 180), 5, (0, 0, 0), -1)
    
    # Boca simple
    cv2.ellipse(image, (200, 240), (20, 10), 0, 0, 360, (150, 50, 50), -1)

    pil_image = Image.fromarray(image.astype('uint8'), 'RGB')
    buffer = io.BytesIO()
    pil_image.save(buffer, format='JPEG')
    image_base64 = base64.b64encode(buffer.getvalue()).decode()
    image_base64 = f'data:image/jpeg;base64,{image_base64}'

    # Extraer embedding usando el servicio
    print('Extrayendo embedding...')
    result = FacialRecognitionService.extract_face_embedding(
        FacialRecognitionService.decode_base64_image(image_base64),
        strict_validation=True
    )

    if result['face_detected'] and result['embedding']:
        embedding_data = {
            'vector': result['embedding'],
            'facial_profile': result.get('facial_profile', {}),
            'timestamp': timezone.now().isoformat(),
            'modelo': result['model'],
            'note': f'Face registered using intelligent hybrid system at {timezone.now()}. Model: {result["model"]}',
            'confidence': result['confidence'],
            'biometric_features': {
                'detection_method': result.get('detection_method', 'unknown'),
            }
        }

        # Crear el rostro registrado
        rostro = RostroRegistrado.objects.create(
            usuario=admin_user,
            nombre_identificador='Test Face',
            embedding_ia=embedding_data,
            confianza_minima=0.8
        )

        print(f'Rostro registrado exitosamente: {rostro.nombre_identificador}')
        print(f'Embedding length: {len(embedding_data["vector"])}')
        print(f'Modelo usado: {result["model"]}')
    else:
        print('No se pudo extraer embedding de la imagen')
        print(f'Resultado: {result}')

if __name__ == "__main__":
    main()