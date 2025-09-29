"""
Sistema Avanzado de Reconocimiento Facial - Smart Condominium
Versión compatible con Python 3.13 - Usa MediaPipe y OpenCV como fallback
"""

import cv2
import numpy as np
from typing import List, Tuple, Optional, Dict, Any
import math

# Intentar importar MediaPipe
try:
    import mediapipe as mp
    MEDIAPIPE_AVAILABLE = True
    print("✅ MediaPipe disponible para reconocimiento facial avanzado")
except ImportError:
    MEDIAPIPE_AVAILABLE = False
    print("⚠️ MediaPipe no disponible, usando OpenCV como fallback")

class AdvancedFacialRecognition:
    """
    Sistema avanzado de reconocimiento facial compatible con Python 3.13
    Usa MediaPipe cuando está disponible, OpenCV como fallback
    """

    def __init__(self):
        # Configurar MediaPipe si está disponible
        if MEDIAPIPE_AVAILABLE:
            self.mp_face_detection = mp.solutions.face_detection
            self.mp_face_mesh = mp.solutions.face_mesh
            self.face_detection = self.mp_face_detection.FaceDetection(
                model_selection=1,  # Modelo más preciso
                min_detection_confidence=0.5
            )
            self.face_mesh = self.mp_face_mesh.FaceMesh(
                static_image_mode=True,
                max_num_faces=1,
                min_detection_confidence=0.5,
                min_tracking_confidence=0.5
            )
            print("🎯 MediaPipe inicializado correctamente")
        else:
            self.mp_face_detection = None
            self.face_detection = None
            self.face_mesh = None

        # Configurar Haar Cascade como fallback
        cascade_path = cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        self.face_cascade = cv2.CascadeClassifier(cascade_path)

        # Variables para procesamiento de frames múltiples
        self.frame_buffer = []
        self.max_frames = 5  # Procesar 5 frames para mayor precisión

        # Umbrales de calidad
        self.min_face_size_ratio = 0.1
        self.max_face_size_ratio = 0.8
        self.center_tolerance = 0.2  # Tolerancia para centrado (20%)

    def validate_image_quality(self, image: np.ndarray) -> Tuple[bool, str]:
        """
        Validar calidad avanzada de imagen para reconocimiento facial
        """
        try:
            height, width = image.shape[:2]

            # Verificar tamaño mínimo
            if width < 80 or height < 80:
                return False, "Imagen demasiado pequeña (mínimo 80x80)"

            # Verificar que no esté completamente negra o blanca
            gray = cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)
            mean_intensity = gray.mean()
            std_intensity = gray.std()

            if std_intensity < 8:
                return False, "Imagen uniforme (posiblemente negra/blanca)"

            if mean_intensity < 15 or mean_intensity > 240:
                return False, "Imagen demasiado oscura o clara"

            # Verificar que tenga suficiente variación
            if std_intensity < 20:
                return False, "Imagen con poca variación (baja calidad)"

            return True, "Imagen de calidad aceptable"

        except Exception as e:
            return False, f"Error en validación: {str(e)}"

    def detect_face_mediapipe(self, image: np.ndarray) -> Tuple[bool, Optional[List], Optional[np.ndarray]]:
        """
        Detectar rostro usando MediaPipe Face Detection
        """
        if not MEDIAPIPE_AVAILABLE or not self.face_detection:
            return False, None, image

        try:
            # MediaPipe espera RGB
            if image.shape[2] == 3:  # RGB/BGR
                rgb_image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            else:
                rgb_image = image

            # Procesar con MediaPipe
            results = self.face_detection.process(rgb_image)

            if not results.detections or len(results.detections) == 0:
                return False, None, image

            # Usar la primera detección (más confiable)
            detection = results.detections[0]

            # Extraer bounding box
            bboxC = detection.location_data.relative_bounding_box
            ih, iw, _ = rgb_image.shape

            x1 = int(bboxC.xmin * iw)
            y1 = int(bboxC.ymin * ih)
            w = int(bboxC.width * iw)
            h = int(bboxC.height * ih)
            x2 = x1 + w
            y2 = y1 + h

            bbox = [x1, y1, x2, y2]

            # Validar tamaño del rostro
            face_area_ratio = (w * h) / (iw * ih)

            if not (self.min_face_size_ratio <= face_area_ratio <= self.max_face_size_ratio):
                return False, None, image

            return True, [bbox], image

        except Exception as e:
            print(f"Error en detección MediaPipe: {e}")
            return False, None, image

    def detect_face_opencv(self, image: np.ndarray) -> Tuple[bool, Optional[List], Optional[np.ndarray]]:
        """
        Detectar rostro usando OpenCV Haar Cascade - versión mejorada con parámetros más estrictos
        """
        try:
            # Convertir a escala de grises si es necesario
            if len(image.shape) == 3:
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            else:
                gray = image

            # Aplicar suavizado para reducir ruido
            gray = cv2.GaussianBlur(gray, (3, 3), 0)

            # Ecualizar histograma para mejorar contraste
            gray = cv2.equalizeHist(gray)

            # Detectar rostros con parámetros más estrictos para evitar falsos positivos
            faces = self.face_cascade.detectMultiScale(
                gray,
                scaleFactor=1.1,    # Menos permisivo
                minNeighbors=4,     # Más estricto para reducir falsos positivos
                minSize=(40, 40),   # Tamaño mínimo más razonable
                maxSize=(400, 400), # Máximo más conservador
                flags=cv2.CASCADE_SCALE_IMAGE
            )

            if len(faces) == 0:
                # Intentar con parámetros ligeramente más permisivos solo si es necesario
                print("🔄 Primera detección falló, intentando con parámetros moderados...")

                # Mejorar contraste antes de detectar
                clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
                gray_enhanced = clahe.apply(gray)

                faces = self.face_cascade.detectMultiScale(
                    gray_enhanced,
                    scaleFactor=1.05,  # Moderadamente permisivo
                    minNeighbors=3,    # Mínimo 3 para confiabilidad
                    minSize=(35, 35),  # Tamaño mínimo razonable
                    maxSize=(400, 400),
                    flags=cv2.CASCADE_SCALE_IMAGE
                )

                if len(faces) == 0:
                    # Último intento con parámetros conservadores
                    faces = self.face_cascade.detectMultiScale(
                        gray_enhanced,
                        scaleFactor=1.08,
                        minNeighbors=3,
                        minSize=(50, 50),  # Tamaño mínimo más grande
                        flags=cv2.CASCADE_DO_CANNY_PRUNING
                    )

            if len(faces) == 0:
                print("❌ OpenCV no detectó rostros con parámetros estrictos")
                return False, None, image

            # Filtrar rostros por validación adicional
            valid_faces = []
            for (x, y, w, h) in faces:
                if self._validate_face_region(gray, x, y, w, h):
                    valid_faces.append((x, y, w, h))

            if not valid_faces:
                print("❌ Ningún rostro pasó la validación adicional")
                return False, None, image

            # Usar el rostro más grande y validado (más confiable)
            valid_faces = sorted(valid_faces, key=lambda x: x[2] * x[3], reverse=True)
            x, y, w, h = valid_faces[0]

            print(f"✅ OpenCV detectó rostro válido: posición ({x}, {y}) tamaño {w}x{h}")

            bbox = [x, y, x + w, y + h]

            # Validar tamaño del rostro (más estricto)
            ih, iw = gray.shape
            face_area_ratio = (w * h) / (iw * ih)

            # Ser más estricto con el tamaño
            if face_area_ratio < 0.01:  # Al menos 1% de la imagen
                print(f"⚠️ Rostro demasiado pequeño: {face_area_ratio:.3f} (< 0.01)")
                return False, None, image

            if face_area_ratio > 0.8:  # Máximo 80% de la imagen
                print(f"⚠️ Rostro demasiado grande: {face_area_ratio:.3f} (> 0.8)")
                return False, None, image

            return True, [bbox], image

        except Exception as e:
            print(f"Error en detección OpenCV mejorada: {e}")
            return False, None, image

    def check_face_center_simple(self, bbox: List[int], image_shape: Tuple[int, int]) -> bool:
        """
        Verificar que el rostro esté centrado usando bounding box
        """
        try:
            x1, y1, x2, y2 = bbox

            # Centro del rostro
            face_center_x = (x1 + x2) / 2
            face_center_y = (y1 + y2) / 2

            # Centro de la imagen
            image_center_x = image_shape[1] / 2
            image_center_y = image_shape[0] / 2

            # Calcular distancia relativa al centro
            distance_x = abs(face_center_x - image_center_x) / image_shape[1]
            distance_y = abs(face_center_y - image_center_y) / image_shape[0]

            # Verificar si está dentro de la tolerancia
            return distance_x <= self.center_tolerance and distance_y <= self.center_tolerance

        except Exception as e:
            print(f"Error verificando centrado: {e}")
            return False

    def extract_face_crop(self, image: np.ndarray, bbox: List[int]) -> np.ndarray:
        """
        Extraer y mejorar el crop del rostro
        """
        try:
            x1, y1, x2, y2 = bbox

            # Agregar padding inteligente
            height, width = image.shape[:2]
            padding_x = int((x2 - x1) * 0.1)
            padding_y = int((y2 - y1) * 0.1)

            x1 = max(0, x1 - padding_x)
            y1 = max(0, y1 - padding_y * 2)  # Más padding arriba
            x2 = min(width, x2 + padding_x)
            y2 = min(height, y2 + padding_y)

            # Extraer crop
            face_crop = image[y1:y2, x1:x2]

            # Mejorar calidad del crop
            face_crop = self._enhance_face_crop(face_crop)

            return face_crop

        except Exception as e:
            print(f"Error extrayendo crop facial: {e}")
            return image

    def _enhance_face_crop(self, face_crop: np.ndarray) -> np.ndarray:
        """
        Mejorar la calidad del crop facial
        """
        try:
            # Ecualización de histograma adaptativa
            lab = cv2.cvtColor(face_crop, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)

            clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8,8))
            l = clahe.apply(l)

            lab = cv2.merge((l,a,b))
            enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)

            # Suavizado ligero para reducir ruido
            enhanced = cv2.bilateralFilter(enhanced, 9, 75, 75)

            return enhanced

        except Exception as e:
            return face_crop

    def process_single_frame(self, image: np.ndarray) -> Dict[str, Any]:
        """
        Procesar un frame individual para extracción de características
        Usa MediaPipe primero, luego OpenCV como fallback
        """
        result = {
            'success': False,
            'face_detected': False,
            'face_centered': False,
            'face_crop': None,
            'quality_score': 0.0,
            'detection_method': 'none',
            'error': None
        }

        try:
            print("🔬 INICIANDO PROCESAMIENTO AVANZADO DE FRAME...")
            print(f"📷 Dimensiones de imagen: {image.shape}")

            # Validar calidad básica
            print("🔍 Validando calidad básica de imagen...")
            quality_ok, quality_msg = self.validate_image_quality(image)
            print(f"📊 Resultado validación calidad: {'✅ PASA' if quality_ok else '❌ FALLA'} - {quality_msg}")
            if not quality_ok:
                result['error'] = quality_msg
                return result

            # Intentar MediaPipe primero
            if MEDIAPIPE_AVAILABLE:
                print("🎯 Intentando detección con MediaPipe...")
                face_detected, bboxes, processed_image = self.detect_face_mediapipe(image)
                detection_method = 'mediapipe' if face_detected else 'none'
                print(f"📋 MediaPipe resultado: {'✅ Rostro detectado' if face_detected else '❌ No detectado'}")
            else:
                print("⚠️ MediaPipe no disponible, usando OpenCV")
                face_detected = False
                bboxes = None
                processed_image = image
                detection_method = 'none'

            # Fallback a OpenCV si MediaPipe falló
            if not face_detected:
                print("🔄 MediaPipe falló, intentando con OpenCV...")
                face_detected, bboxes, processed_image = self.detect_face_opencv(image)
                detection_method = 'opencv' if face_detected else 'none'
                print(f"📋 OpenCV resultado: {'✅ Rostro detectado' if face_detected else '❌ No detectado'}")

            if not face_detected or not bboxes:
                result['error'] = "No se detectó rostro en la imagen con ningún método"
                print("❌ NINGÚN MÉTODO DETECTÓ ROSTRO")
                return result

            result['face_detected'] = True
            result['detection_method'] = detection_method
            print(f"✅ ROSTRO DETECTADO usando {detection_method.upper()}")

            # Verificar centrado
            print("📍 Verificando centrado del rostro...")
            centered = self.check_face_center_simple(bboxes[0], image.shape[:2])
            result['face_centered'] = centered
            print(f"📊 Centrado: {'✅ Centrado correctamente' if centered else '⚠️ No centrado'}")

            # Extraer crop del rostro
            print("✂️ Extrayendo crop del rostro...")
            face_crop = self.extract_face_crop(image, bboxes[0])
            result['face_crop'] = face_crop
            print(f"🖼️ Crop extraído: {face_crop.shape if face_crop is not None else 'None'}")

            # Calcular score de calidad basado en el método usado
            print("📈 Calculando score de calidad...")
            if detection_method == 'mediapipe':
                quality_score = self._calculate_quality_score_mediapipe(image, bboxes[0], centered)
                print(f"🎯 Score calidad MediaPipe: {quality_score:.3f}")
            else:
                quality_score = self._calculate_quality_score_opencv(image, bboxes[0], centered)
                print(f"🎯 Score calidad OpenCV: {quality_score:.3f}")

            result['quality_score'] = quality_score

            # Verificación adicional: asegurar que el score sea razonable
            if quality_score < 0.3:
                print(f"⚠️ ADVERTENCIA: Score de calidad bajo ({quality_score:.3f})")
                result['error'] = f"Calidad de imagen insuficiente (score: {quality_score:.3f})"
                result['success'] = False
                return result

            result['success'] = True
            print("🎉 PROCESAMIENTO DE FRAME COMPLETADO EXITOSAMENTE")
            return result

        except Exception as e:
            result['error'] = f"Error procesando frame: {str(e)}"
            print(f"❌ ERROR PROCESANDO FRAME: {e}")
            return result

    def _calculate_quality_score_mediapipe(self, image: np.ndarray, bbox: List[int], centered: bool) -> float:
        """
        Calcular score de calidad del rostro detectado usando MediaPipe
        """
        try:
            score = 0.0

            # 1. Tamaño del rostro (0-0.4 puntos) - MediaPipe es más preciso
            face_area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
            image_area = image.shape[0] * image.shape[1]
            size_ratio = face_area / image_area

            if 0.15 <= size_ratio <= 0.6:
                score += 0.4
            elif 0.1 <= size_ratio <= 0.8:
                score += 0.3

            # 2. Centrado (0-0.3 puntos)
            if centered:
                score += 0.3
            else:
                score += 0.1

            # 3. Calidad de iluminación (0-0.2 puntos)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            mean_brightness = gray.mean()
            std_brightness = gray.std()

            if 80 <= mean_brightness <= 200 and std_brightness >= 30:
                score += 0.2
            elif 60 <= mean_brightness <= 220:
                score += 0.1

            # 4. Bordes y definición (0-0.1 puntos)
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])

            if edge_density > 0.05:
                score += 0.1

            return min(1.0, score)

        except Exception as e:
            print(f"Error calculando score de calidad MediaPipe: {e}")
            return 0.0

    def _calculate_quality_score_opencv(self, image: np.ndarray, bbox: List[int], centered: bool) -> float:
        """
        Calcular score de calidad del rostro detectado usando OpenCV
        """
        try:
            score = 0.0

            # 1. Tamaño del rostro (0-0.35 puntos) - OpenCV es menos preciso
            face_area = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
            image_area = image.shape[0] * image.shape[1]
            size_ratio = face_area / image_area

            if 0.15 <= size_ratio <= 0.6:
                score += 0.35
            elif 0.1 <= size_ratio <= 0.8:
                score += 0.25

            # 2. Centrado (0-0.3 puntos)
            if centered:
                score += 0.3
            else:
                score += 0.1

            # 3. Calidad de iluminación (0-0.2 puntos)
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            mean_brightness = gray.mean()
            std_brightness = gray.std()

            if 80 <= mean_brightness <= 200 and std_brightness >= 30:
                score += 0.2
            elif 60 <= mean_brightness <= 220:
                score += 0.1

            # 4. Bordes y definición (0-0.15 puntos) - Más tolerante con OpenCV
            edges = cv2.Canny(gray, 50, 150)
            edge_density = np.sum(edges > 0) / (edges.shape[0] * edges.shape[1])

            if edge_density > 0.03:  # Umbral más bajo para OpenCV
                score += 0.15

            return min(1.0, score)

        except Exception as e:
            print(f"Error calculando score de calidad OpenCV: {e}")
            return 0.0

    def process_multiple_frames(self, frames: List[np.ndarray]) -> Dict[str, Any]:
        """
        Procesar múltiples frames para mayor precisión
        """
        if not frames:
            return {'success': False, 'error': 'No frames provided'}

        results = []
        best_result = None
        best_score = 0.0

        # Procesar cada frame
        for i, frame in enumerate(frames):
            result = self.process_single_frame(frame)
            results.append(result)

            if result['success'] and result['quality_score'] > best_score:
                best_result = result
                best_score = result['quality_score']

        # Si no hay resultados exitosos, devolver el último error
        if not best_result:
            return {
                'success': False,
                'error': results[-1].get('error', 'No se pudo procesar ningún frame')
            }

        # Retornar el mejor resultado
        return {
            'success': True,
            'face_crop': best_result['face_crop'],
            'quality_score': best_score,
            'face_centered': best_result['face_centered'],
            'frames_processed': len(frames),
            'best_frame_index': results.index(best_result)
        }

    def create_embedding_from_crop(self, face_crop: np.ndarray) -> List[float]:
        """
        Crear embedding desde crop facial usando técnicas avanzadas
        Usa MediaPipe Face Mesh cuando está disponible para características más precisas
        """
        try:
            # Redimensionar para consistencia
            face_crop = cv2.resize(face_crop, (160, 160))

            features = []

            # Intentar MediaPipe Face Mesh para características avanzadas
            if MEDIAPIPE_AVAILABLE and self.face_mesh:
                mesh_features = self._extract_mesh_features(face_crop)
                if mesh_features:
                    features.extend(mesh_features)
                    print(f"✅ Extraídas {len(mesh_features)} características de Face Mesh")

            # Características tradicionales como complemento o fallback
            traditional_features = self._extract_traditional_features(face_crop)
            features.extend(traditional_features)

            # Normalizar y convertir a lista
            features = np.array(features, dtype=np.float32)
            features = (features - np.mean(features)) / (np.std(features) + 1e-8)

            # Asegurar exactamente 128 dimensiones
            if len(features) > 128:
                features = features[:128]
            elif len(features) < 128:
                # Rellenar con ceros si es necesario
                padding = np.zeros(128 - len(features))
                features = np.concatenate([features, padding])

            return features.tolist()

        except Exception as e:
            print(f"Error creando embedding: {e}")
            # Fallback a embedding básico
            return [0.0] * 128

    def _extract_mesh_features(self, face_crop: np.ndarray) -> Optional[List[float]]:
        """
        Extraer características usando MediaPipe Face Mesh
        """
        if not MEDIAPIPE_AVAILABLE or not self.face_mesh:
            return None

        try:
            # MediaPipe espera RGB
            rgb_crop = cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB)

            # Procesar con Face Mesh
            results = self.face_mesh.process(rgb_crop)

            if not results.multi_face_landmarks:
                return None

            # Usar el primer rostro detectado
            face_landmarks = results.multi_face_landmarks[0]

            # Extraer coordenadas de landmarks clave
            features = []
            for landmark in face_landmarks.landmark:
                features.extend([landmark.x, landmark.y, landmark.z])

            # Calcular distancias entre puntos clave para características geométricas
            landmark_points = [(lm.x, lm.y, lm.z) for lm in face_landmarks.landmark]

            # Distancias entre ojos, nariz, boca, etc.
            distances = self._calculate_key_distances(landmark_points)
            features.extend(distances)

            # Ratios de proporciones faciales
            ratios = self._calculate_facial_ratios(landmark_points)
            features.extend(ratios)

            return features[:64]  # Limitar a 64 características de mesh

        except Exception as e:
            print(f"Error extrayendo características de mesh: {e}")
            return None

    def _calculate_key_distances(self, landmarks: List[Tuple[float, float, float]]) -> List[float]:
        """
        Calcular distancias entre puntos clave del rostro
        """
        try:
            distances = []

            # Índices de MediaPipe Face Mesh para puntos clave
            left_eye_outer = 33
            left_eye_inner = 133
            right_eye_outer = 362
            right_eye_inner = 263
            nose_tip = 1
            mouth_left = 61
            mouth_right = 291
            chin = 152

            # Distancia entre ojos
            left_eye_center = ((landmarks[left_eye_outer][0] + landmarks[left_eye_inner][0]) / 2,
                             (landmarks[left_eye_outer][1] + landmarks[left_eye_inner][1]) / 2)
            right_eye_center = ((landmarks[right_eye_outer][0] + landmarks[right_eye_inner][0]) / 2,
                              (landmarks[right_eye_outer][1] + landmarks[right_eye_inner][1]) / 2)

            eye_distance = math.sqrt((left_eye_center[0] - right_eye_center[0])**2 +
                                   (left_eye_center[1] - right_eye_center[1])**2)
            distances.append(eye_distance)

            # Distancia ojo-nariz
            nose_pos = landmarks[nose_tip][:2]
            left_eye_to_nose = math.sqrt((left_eye_center[0] - nose_pos[0])**2 +
                                       (left_eye_center[1] - nose_pos[1])**2)
            right_eye_to_nose = math.sqrt((right_eye_center[0] - nose_pos[0])**2 +
                                        (right_eye_center[1] - nose_pos[1])**2)
            distances.extend([left_eye_to_nose, right_eye_to_nose])

            # Ancho de boca
            mouth_width = math.sqrt((landmarks[mouth_left][0] - landmarks[mouth_right][0])**2 +
                                  (landmarks[mouth_left][1] - landmarks[mouth_right][1])**2)
            distances.append(mouth_width)

            # Altura facial (nariz-mentón)
            face_height = math.sqrt((landmarks[nose_tip][0] - landmarks[chin][0])**2 +
                                  (landmarks[nose_tip][1] - landmarks[chin][1])**2)
            distances.append(face_height)

            return distances

        except Exception as e:
            print(f"Error calculando distancias: {e}")
            return [0.1] * 5

    def _calculate_facial_ratios(self, landmarks: List[Tuple[float, float, float]]) -> List[float]:
        """
        Calcular ratios de proporciones faciales
        """
        try:
            ratios = []

            # Índices de puntos clave
            left_eye_outer = 33
            right_eye_outer = 362
            nose_tip = 1
            mouth_left = 61
            mouth_right = 291
            chin = 152

            # Ratio ancho ojos / ancho cara
            eye_distance = math.sqrt((landmarks[left_eye_outer][0] - landmarks[right_eye_outer][0])**2 +
                                   (landmarks[left_eye_outer][1] - landmarks[right_eye_outer][1])**2)
            face_width = eye_distance * 2  # Aproximación
            eye_to_face_ratio = eye_distance / face_width if face_width > 0 else 0
            ratios.append(eye_to_face_ratio)

            # Ratio ancho boca / ancho ojos
            mouth_width = math.sqrt((landmarks[mouth_left][0] - landmarks[mouth_right][0])**2 +
                                  (landmarks[mouth_left][1] - landmarks[mouth_right][1])**2)
            mouth_to_eye_ratio = mouth_width / eye_distance if eye_distance > 0 else 0
            ratios.append(mouth_to_eye_ratio)

            # Ratio altura nariz / altura total
            nose_to_chin = math.sqrt((landmarks[nose_tip][0] - landmarks[chin][0])**2 +
                                   (landmarks[nose_tip][1] - landmarks[chin][1])**2)
            face_height = nose_to_chin * 2  # Aproximación
            nose_ratio = nose_to_chin / face_height if face_height > 0 else 0
            ratios.append(nose_ratio)

            return ratios

        except Exception as e:
            print(f"Error calculando ratios: {e}")
            return [0.1] * 3

    def _extract_traditional_features(self, face_crop: np.ndarray) -> List[float]:
        """
        Extraer características tradicionales como complemento
        """
        try:
            features = []

            # 1. Características de color (histograma LAB)
            lab = cv2.cvtColor(face_crop, cv2.COLOR_BGR2LAB)
            for channel in range(3):
                hist = cv2.calcHist([lab], [channel], None, [16], [0, 256])
                hist = cv2.normalize(hist, hist).flatten()
                features.extend(hist)

            # 2. Características de textura (GLCM simplificado)
            gray = cv2.cvtColor(face_crop, cv2.COLOR_BGR2GRAY)
            glcm_features = self._calculate_glcm_features_simple(gray)
            features.extend(glcm_features)

            # 3. Características geométricas (momentos)
            moments = cv2.moments(gray)
            hu_moments = cv2.HuMoments(moments).flatten()
            features.extend(hu_moments)

            # 4. Características de frecuencia (DCT)
            dct_features = self._extract_dct_features(gray)
            features.extend(dct_features)

            return features

        except Exception as e:
            print(f"Error extrayendo características tradicionales: {e}")
            return [0.0] * 64

    def _calculate_glcm_features_simple(self, gray_image: np.ndarray) -> List[float]:
        """Calcular características GLCM simplificadas"""
        try:
            # Matriz GLCM simplificada
            h, w = gray_image.shape
            matrix = np.zeros((16, 16), dtype=np.float32)

            # Cuantizar a 16 niveles
            quantized = (gray_image // 16).astype(np.uint8)

            # Calcular co-ocurrencias
            for i in range(h):
                for j in range(w-1):
                    val1 = min(15, quantized[i, j])
                    val2 = min(15, quantized[i, j+1])
                    matrix[val1, val2] += 1

            # Normalizar
            total = matrix.sum()
            if total > 0:
                matrix = matrix / total

            # Calcular propiedades
            contrast = energy = homogeneity = correlation = 0

            for i in range(16):
                for j in range(16):
                    contrast += (i - j) ** 2 * matrix[i, j]
                    energy += matrix[i, j] ** 2
                    homogeneity += matrix[i, j] / (1 + abs(i - j))
                    correlation += (i * j * matrix[i, j])

            return [contrast, energy, homogeneity, correlation]

        except Exception:
            return [0.1] * 4

    def _extract_dct_features(self, gray_image: np.ndarray) -> List[float]:
        """Extraer características usando DCT"""
        try:
            # Aplicar DCT
            dct = cv2.dct(np.float32(gray_image))

            # Tomar coeficientes de baja frecuencia (esquinas superiores)
            features = []
            for i in range(min(8, dct.shape[0])):
                for j in range(min(8, dct.shape[1])):
                    if not (i == 0 and j == 0):  # Excluir DC component
                        features.append(abs(dct[i, j]))

            # Normalizar
            if features:
                features = np.array(features)
                features = features / (np.max(features) + 1e-8)

            return features[:12].tolist()  # Máximo 12 características

        except Exception:
            return [0.1] * 8

    def compare_embeddings(self, embedding1: List[float], embedding2: List[float]) -> Dict[str, float]:
        """
        Comparar dos embeddings usando distancia coseno y euclidiana
        """
        try:
            # Convertir a arrays numpy
            enc1 = np.array(embedding1, dtype=np.float32)
            enc2 = np.array(embedding2, dtype=np.float32)

            # Normalizar
            norm1 = np.linalg.norm(enc1)
            norm2 = np.linalg.norm(enc2)

            if norm1 > 0:
                enc1 = enc1 / norm1
            if norm2 > 0:
                enc2 = enc2 / norm2

            # Distancia euclidiana
            euclidean_distance = np.linalg.norm(enc1 - enc2)

            # Similitud coseno
            cosine_similarity = np.dot(enc1, enc2)

            # Convertir similitud coseno a escala 0-1
            similarity = (cosine_similarity + 1) / 2

            # Confianza basada en ambas métricas
            confidence = (similarity + (1 - euclidean_distance)) / 2

            return {
                'match': confidence > 0.7,  # Umbral para matching
                'confidence': float(confidence),
                'similarity': float(similarity),
                'distance': float(euclidean_distance)
            }

        except Exception as e:
            print(f"Error comparando embeddings: {e}")
            return {
                'match': False,
                'confidence': 0.0,
                'similarity': 0.0,
                'distance': 1.0
            }

    def _validate_face_region(self, gray_image: np.ndarray, x: int, y: int, w: int, h: int) -> bool:
        """
        Validar que la región detectada tenga características de un rostro real
        """
        try:
            # Extraer la región del rostro
            face_region = gray_image[y:y+h, x:x+w]

            if face_region.size == 0:
                return False

            # 1. Verificar variación de intensidad (los rostros tienen gradientes)
            std_intensity = face_region.std()
            if std_intensity < 25:  # Muy poco contraste
                return False

            # 2. Verificar que no sea uniforme (como un gradiente simple)
            mean_intensity = face_region.mean()
            if std_intensity / (mean_intensity + 1) < 0.1:  # Relación baja varianza/media
                return False

            # 3. Verificar densidad de bordes (los rostros tienen muchos bordes)
            edges = cv2.Canny(face_region, 50, 150)
            edge_density = np.sum(edges > 0) / face_region.size

            if edge_density < 0.05:  # Muy pocos bordes
                return False

            # 4. Verificar simetría horizontal aproximada (los rostros son aproximadamente simétricos)
            left_half = face_region[:, :w//2]
            right_half = cv2.flip(face_region[:, w//2:], 1)  # Flip horizontal

            if left_half.shape != right_half.shape:
                # Ajustar tamaño si son diferentes
                min_width = min(left_half.shape[1], right_half.shape[1])
                left_half = left_half[:, :min_width]
                right_half = right_half[:, :min_width]

            if left_half.size > 0 and right_half.size > 0:
                symmetry_score = np.mean(np.abs(left_half.astype(np.float32) - right_half.astype(np.float32)))
                if symmetry_score > 30:  # Baja simetría
                    return False

            # 5. Verificar que no sea ruido aleatorio (comprobar histograma)
            hist = cv2.calcHist([face_region], [0], None, [32], [0, 256])
            hist = hist.flatten()
            hist_std = np.std(hist)

            if hist_std < 50:  # Histograma muy uniforme (ruido o gradiente simple)
                return False

            return True

        except Exception as e:
            print(f"Error en validación de región facial: {e}")
            return False

    def __del__(self):
        """
        Liberar recursos de MediaPipe al destruir la instancia
        """
        try:
            if hasattr(self, 'face_detection') and self.face_detection:
                self.face_detection.close()
            if hasattr(self, 'face_mesh') and self.face_mesh:
                self.face_mesh.close()
        except:
            pass