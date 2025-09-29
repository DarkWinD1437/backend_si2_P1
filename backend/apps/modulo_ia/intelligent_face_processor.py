"""
Sistema Inteligente de Reconocimiento Facial - Smart Condominium
Integra DeepFace + Grok 4 Fast Free para control de acceso avanzado
"""

import os
import cv2
import numpy as np
from deepface import DeepFace
from typing import Tuple, List, Dict, Any, Optional
import datetime
import base64
import io
from PIL import Image
import httpx
from openai import OpenAI
import math


class IntelligentFaceProcessor:
    """
    Procesador inteligente de rostros que combina:
    - DeepFace para detección y matching preciso
    - Grok 4 Fast Free para análisis inteligente
    - Lógica avanzada de control de acceso
    """

    def __init__(self, grok_client: Optional[OpenAI] = None):
        # SFace model for matching
        self.sface_model = "SFace"

        # Grok client for intelligent analysis
        self.grok_client = grok_client

        # Processing state variables
        self.frame_counter = 0
        self.required_frames = 48  # Process every 48 frames for accuracy
        self.current_user = None
        self.processing_state = "waiting"

    def process_frame_signup(self, image: np.ndarray, user_code: str) -> Dict[str, Any]:
        """
        Procesar frame para registro facial usando lógica avanzada
        """
        result = {
            'success': False,
            'face_detected': False,
            'face_centered': False,
            'face_saved': False,
            'message': '',
            'processed_image': image.copy(),
            'user_code': user_code
        }

        try:
            # Step 1: Face Detection using DeepFace
            face_detected, face_info = self._detect_face_deepface(image)
            result['face_detected'] = face_detected

            if not face_detected:
                result['message'] = '¡No se detectó rostro!'
                return result

            # Step 2: Check face center
            face_centered = self._check_face_center(face_info, image.shape)
            result['face_centered'] = face_centered

            # Step 3: Show state and process
            processed_image = self._draw_signup_state(image.copy(), face_centered)
            result['processed_image'] = processed_image

            if face_centered:
                # Step 4: Extract face crop
                face_crop = face_info

                # Step 5: Save face (this would be handled by Django model)
                result['face_crop'] = face_crop
                result['face_saved'] = True
                result['success'] = True
                result['message'] = '¡Rostro guardado exitosamente!'

                # Add intelligent analysis with Grok
                if self.grok_client:
                    grok_analysis = self._analyze_face_with_grok(face_crop, "signup")
                    result['grok_analysis'] = grok_analysis

            else:
                result['message'] = '¡Centra tu rostro en la cámara!'

        except Exception as e:
            result['message'] = f'Error en procesamiento: {str(e)}'

        return result

    def process_frame_login(self, image: np.ndarray, registered_faces: List[Dict]) -> Dict[str, Any]:
        """
        Procesar frame para login facial usando lógica avanzada
        """
        result = {
            'success': False,
            'face_detected': False,
            'face_centered': False,
            'user_matched': False,
            'matched_user': None,
            'confidence': 0.0,
            'message': '',
            'processed_image': image.copy(),
            'frame_count': self.frame_counter
        }

        try:
            # Step 1: Face Detection using DeepFace
            face_detected, face_info = self._detect_face_deepface(image)
            result['face_detected'] = face_detected

            if not face_detected:
                result['message'] = '¡No se detectó rostro!'
                self._reset_frame_counter()
                return result

            # Step 2: Check face center
            face_centered = self._check_face_center(face_info, image.shape)
            result['face_centered'] = face_centered

            # Step 3: Show state
            processed_image = self._draw_login_state(image.copy(), result.get('user_matched', False))
            result['processed_image'] = processed_image

            if face_centered:
                # Increment frame counter
                self.frame_counter += 1
                result['frame_count'] = self.frame_counter

                if self.frame_counter >= self.required_frames:
                    # Step 4: Extract face crop
                    face_crop = face_info

                    # Step 5: Face matching against database
                    if registered_faces:
                        match_result = self._match_face_against_database(face_crop, registered_faces)
                        result.update(match_result)

                        if match_result['user_matched']:
                            result['success'] = True
                            result['message'] = f'¡Acceso aprobado para {match_result["matched_user"]}!'

                            # Intelligent feedback with Grok
                            if self.grok_client:
                                grok_feedback = self._generate_access_feedback_with_grok(
                                    match_result["matched_user"], match_result["confidence"]
                                )
                                result['grok_feedback'] = grok_feedback
                        else:
                            result['message'] = 'Usuario no aprobado - Rostro no reconocido'
                    else:
                        result['message'] = 'Base de datos vacía'

                    # Reset counter after processing
                    self._reset_frame_counter()
                else:
                    remaining_frames = self.required_frames - self.frame_counter
                    result['message'] = f'Comparando rostros... espera {remaining_frames} frames'
            else:
                result['message'] = '¡Centra tu rostro en la cámara!'
                self._reset_frame_counter()

        except Exception as e:
            result['message'] = f'Error en procesamiento: {str(e)}'
            self._reset_frame_counter()

        return result



    def _check_face_center(self, face_info: np.ndarray, image_shape: Tuple[int, int, int]) -> bool:
        """Verificar si el rostro está centrado usando bounding box de DeepFace"""
        height, width = image_shape[:2]

        # Get face bounding box from DeepFace result
        # DeepFace returns the face crop, so we need to estimate position
        face_height, face_width = face_info.shape[:2]

        # Assume face is roughly centered if it's a reasonable size
        # For more precise centering, we'd need the original bounding box
        # For now, we'll use a simple heuristic based on face size
        min_face_size = min(width, height) * 0.1  # Face should be at least 10% of image
        max_face_size = min(width, height) * 0.8  # Face shouldn't be more than 80% of image

        face_area = face_width * face_height
        image_area = width * height

        # Check if face size is reasonable (not too small, not too large)
        face_ratio = face_area / image_area

        return 0.01 < face_ratio < 0.5  # Reasonable face size ratio



    def _match_face_against_database(self, face_crop: np.ndarray, registered_faces: List[Dict]) -> Dict[str, Any]:
        """Comparar rostro contra base de datos usando SFace"""
        result = {
            'user_matched': False,
            'matched_user': None,
            'confidence': 0.0,
            'best_distance': float('inf')
        }

        try:
            for face_data in registered_faces:
                # Convertir imagen registrada a array numpy si es necesario
                if isinstance(face_data['image'], str):
                    # Si es base64, decodificar
                    registered_image = self._decode_base64_image(face_data['image'])
                else:
                    registered_image = face_data['image']

                # Comparar usando SFace
                try:
                    verification = DeepFace.verify(
                        img1_path=face_crop,
                        img2_path=registered_image,
                        model_name=self.sface_model,
                        enforce_detection=False
                    )

                    distance = verification['distance']
                    verified = verification['verified']

                    print(f"Comparando con {face_data['user']}: distance={distance:.4f}, verified={verified}")

                    if verified and distance < result['best_distance']:
                        result['user_matched'] = True
                        result['matched_user'] = face_data['user']
                        result['confidence'] = 1.0 - distance  # Convert distance to confidence
                        result['best_distance'] = distance

                except Exception as e:
                    print(f"Error comparando con {face_data['user']}: {e}")
                    continue

        except Exception as e:
            print(f"Error en matching: {e}")

        return result

    def _draw_signup_state(self, image: np.ndarray, face_centered: bool) -> np.ndarray:
        """Dibujar estado del registro en la imagen"""
        if face_centered:
            text = 'Guardando rostro, espera tres segundos por favor'
            color = (0, 255, 0)  # Green
        else:
            text = 'Procesando rostro, mira a la cámara por favor!'
            color = (255, 0, 0)  # Red

        return self._draw_text_on_image(image, text, color)

    def _draw_login_state(self, image: np.ndarray, user_matched: bool) -> np.ndarray:
        """Dibujar estado del login en la imagen"""
        if user_matched:
            text = '¡Rostro aprobado, puedes entrar!'
            color = (0, 255, 0)  # Green
        elif user_matched is None:
            text = 'Comparando rostros, mira a la cámara y espera 3 segundos por favor!'
            color = (255, 255, 0)  # Yellow
        else:
            text = 'Rostro no aprobado, por favor regístrate!'
            color = (255, 0, 0)  # Red

        return self._draw_text_on_image(image, text, color)

    def _draw_text_on_image(self, image: np.ndarray, text: str, color: Tuple[int, int, int]) -> np.ndarray:
        """Dibujar texto en la imagen"""
        font = cv2.FONT_HERSHEY_DUPLEX
        font_scale = 0.75
        thickness = 1

        # Get text size
        (text_width, text_height), baseline = cv2.getTextSize(text, font, font_scale, thickness)

        # Position text
        x, y = 370, 650

        # Draw background rectangle
        cv2.rectangle(image,
                     (x, y - text_height - baseline),
                     (x + text_width, y + baseline),
                     (0, 0, 0), cv2.FILLED)

        # Draw text
        cv2.putText(image, text, (x, y - 5), font, font_scale, color, thickness)

        return image



    def _reset_frame_counter(self):
        """Reiniciar contador de frames"""
        self.frame_counter = 0

    def _decode_base64_image(self, base64_string: str) -> np.ndarray:
        """Decodificar imagen base64 a array numpy"""
        if ',' in base64_string:
            base64_string = base64_string.split(',')[1]

        image_data = base64.b64decode(base64_string)
        image = Image.open(io.BytesIO(image_data))

        if image.mode != 'RGB':
            image = image.convert('RGB')

        return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    def _analyze_face_with_grok(self, face_crop: np.ndarray, context: str) -> Dict[str, Any]:
        """Analizar rostro con Grok para feedback inteligente"""
        if not self.grok_client:
            return {"analysis": "Análisis no disponible - Grok no configurado"}

        try:
            # Convertir imagen a base64
            pil_image = Image.fromarray(cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB))
            buffer = io.BytesIO()
            pil_image.save(buffer, format='JPEG')
            image_base64 = base64.b64encode(buffer.getvalue()).decode()

            prompt = f"""
            Analiza esta imagen de un rostro humano en el contexto de {context}.
            Proporciona una descripción detallada de:
            1. Calidad de la imagen (iluminación, enfoque, ángulo)
            2. Características faciales distintivas
            3. Expresión facial y estado emocional aparente
            4. Recomendaciones para mejorar el registro/login

            Sé específico y útil para un sistema de reconocimiento facial.
            """

            response = self.grok_client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": "https://smartcondominium.com",
                    "X-Title": "Smart Condominium AI",
                },
                model="x-ai/grok-4-fast:free",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}
                            }
                        ]
                    }
                ]
            )

            analysis = response.choices[0].message.content.strip()

            return {
                "analysis": analysis,
                "timestamp": datetime.datetime.now().isoformat(),
                "context": context
            }

        except Exception as e:
            return {"analysis": f"Error en análisis con Grok: {str(e)}"}

    def _generate_access_feedback_with_grok(self, user_name: str, confidence: float) -> Dict[str, Any]:
        """Generar feedback inteligente de acceso con Grok"""
        if not self.grok_client:
            return {"feedback": "Feedback inteligente no disponible"}

        try:
            confidence_percent = confidence * 100

            prompt = f"""
            Como asistente de seguridad inteligente de Smart Condominium, genera un mensaje de bienvenida personalizado para {user_name} que acaba de acceder al sistema con {confidence_percent:.1f}% de confianza.

            El mensaje debe ser:
            1. Amigable y profesional
            2. Mencionar el nivel de confianza de verificación
            3. Incluir una recomendación de seguridad contextual
            4. Ser conciso pero informativo

            Contexto: Sistema de control de acceso facial con IA avanzada.
            """

            response = self.grok_client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": "https://smartcondominium.com",
                    "X-Title": "Smart Condominium AI",
                },
                model="x-ai/grok-4-fast:free",
                messages=[
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )

            feedback = response.choices[0].message.content.strip()

            return {
                "feedback": feedback,
                "confidence": confidence,
                "timestamp": datetime.datetime.now().isoformat()
            }

        except Exception as e:
            return {"feedback": f"Error generando feedback: {str(e)}"}

    def __del__(self):
        """Liberar recursos"""
        pass