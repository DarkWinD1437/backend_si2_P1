#!/usr/bin/env python
import cv2
import numpy as np
from PIL import Image
import base64
from io import BytesIO

def test_opencv_face_detection():
    print("=== TEST DE DETECCIÓN DE ROSTROS CON OPENCV ===")

    # Verificar que OpenCV esté disponible
    print(f"OpenCV version: {cv2.__version__}")

    # Verificar clasificadores disponibles
    try:
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        if face_cascade.empty():
            print("❌ Error: No se pudo cargar el clasificador Haar para rostros")
            return
        else:
            print("✅ Clasificador Haar cargado correctamente")
    except Exception as e:
        print(f"❌ Error cargando clasificador: {e}")
        return

    # Crear una imagen de prueba con un "rostro" simple (círculo blanco en fondo negro)
    img = np.zeros((300, 300, 3), dtype=np.uint8)

    # Dibujar un círculo blanco que simule un rostro
    center = (150, 150)
    radius = 80
    cv2.circle(img, center, radius, (255, 255, 255), -1)

    # Agregar algunos detalles para simular rasgos faciales
    cv2.circle(img, (130, 130), 10, (0, 0, 0), -1)  # Ojo izquierdo
    cv2.circle(img, (170, 130), 10, (0, 0, 0), -1)  # Ojo derecho
    cv2.rectangle(img, (140, 160), (160, 170), (0, 0, 0), -1)  # Boca

    print("Imagen de prueba creada con rostro simulado")

    # Convertir a escala de grises
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # Detectar rostros
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    print(f"Rostros detectados: {len(faces)}")
    for (x, y, w, h) in faces:
        print(f"  - Rostro en ({x}, {y}) tamaño {w}x{h}")

    if len(faces) == 0:
        print("❌ OpenCV no detectó rostros en la imagen de prueba")
        print("Esto explica por qué el login facial falla")

        # Probar con parámetros más relajados
        print("\nProbando con parámetros más relajados...")
        faces_relaxed = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=3, minSize=(20, 20))
        print(f"Rostros detectados con parámetros relajados: {len(faces_relaxed)}")

        # Mostrar información de debug
        print(f"Imagen shape: {gray.shape}")
        print(f"Imagen dtype: {gray.dtype}")
        print(f"Valores min/max: {gray.min()}/{gray.max()}")

    else:
        print("✅ OpenCV detectó rostros correctamente")

def test_with_real_image():
    print("\n=== TEST CON IMAGEN MÁS REALISTA ===")

    # Crear una imagen más realista con gradientes y texturas
    img = np.random.randint(100, 200, (400, 400, 3), dtype=np.uint8)

    # Crear un "rostro" ovalado con gradientes
    center_y, center_x = 200, 200
    for y in range(400):
        for x in range(400):
            dist = ((y - center_y)**2 + (x - center_x)**2)**0.5
            if dist < 120:  # Radio del rostro
                # Gradiente desde el centro hacia afuera
                factor = 1 - (dist / 120)
                brightness = int(180 + factor * 75)  # Más brillante en el centro
                img[y, x] = [brightness, brightness, brightness]

    # Agregar ojos
    cv2.circle(img, (170, 180), 15, (50, 50, 50), -1)
    cv2.circle(img, (230, 180), 15, (50, 50, 50), -1)

    # Agregar boca
    cv2.ellipse(img, (200, 240), (30, 15), 0, 0, 180, (50, 50, 50), -1)

    print("Imagen realista creada")

    # Convertir a escala de grises y detectar
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))

    print(f"Rostros detectados en imagen realista: {len(faces)}")
    for (x, y, w, h) in faces:
        print(f"  - Rostro en ({x}, {y}) tamaño {w}x{h}")

if __name__ == "__main__":
    test_opencv_face_detection()
    test_with_real_image()