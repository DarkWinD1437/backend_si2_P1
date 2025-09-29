import cv2
import numpy as np
from PIL import Image
import base64
import io
import hashlib
import random
import json
import re
from math import sqrt
import face_recognition as fr

class FacialRecognitionService:
    """Servicio de reconocimiento facial inteligente que combina face_recognition con Grok 4 Fast Free"""

    @staticmethod
    def safe_float(value, default=0.0):
        """
        Convertir un valor a float de manera segura
        """
        try:
            if isinstance(value, (int, float)):
                return float(value)
            elif isinstance(value, str):
                # Intentar convertir string a float
                return float(value.replace(',', '.'))
            else:
                return default
        except (ValueError, TypeError):
            return default

    @staticmethod
    def safe_random_seed(seed_value):
        """
        Convertir un valor a un seed válido para np.random.seed (0 <= seed < 2**32)
        """
        try:
            # Convertir a entero positivo
            if isinstance(seed_value, str):
                # Usar hash de string y convertir a positivo
                seed = abs(hash(seed_value))
            else:
                # Para otros tipos, convertir a int y asegurar positivo
                seed = abs(int(seed_value))

            # Asegurar que esté en el rango válido (0 <= seed < 2**32)
            return seed % (2**32)
        except (ValueError, TypeError):
            # Fallback a seed fijo si hay error
            return 42

    @staticmethod
    def decode_base64_image(base64_string):
        """Decodificar imagen base64 a array numpy"""
        try:
            # Remover el prefijo data:image/jpeg;base64, si existe
            if ',' in base64_string:
                base64_string = base64_string.split(',')[1]

            # Decodificar base64
            image_data = base64.b64decode(base64_string)
            image = Image.open(io.BytesIO(image_data))

            # Convertir a RGB si es necesario
            if image.mode != 'RGB':
                image = image.convert('RGB')

            # Convertir a array numpy
            image_array = np.array(image)

            # Validación básica de tamaño ANTES de procesar
            height, width = image_array.shape[:2]
            if width < 64 or height < 64:
                raise ValueError(f"Imagen demasiado pequeña: {width}x{height} (mínimo 64x64)")

            if width > 4096 or height > 4096:
                raise ValueError(f"Imagen demasiado grande: {width}x{height} (máximo 4096x4096)")

            return image_array
        except Exception as e:
            raise ValueError(f"Error decodificando imagen: {str(e)}")

    @staticmethod
    def preprocess_image(image_array):
        """Preprocesar imagen para mejor reconocimiento facial"""
        try:
            # Redimensionar si es muy grande (máximo 512px en el lado más largo)
            height, width = image_array.shape[:2]
            max_size = 512

            if max(width, height) > max_size:
                scale = max_size / max(width, height)
                new_width = int(width * scale)
                new_height = int(height * scale)
                image_array = cv2.resize(image_array, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)

            # Convertir a espacio de color LAB para mejor procesamiento
            lab = cv2.cvtColor(image_array, cv2.COLOR_RGB2LAB)
            l, a, b = cv2.split(lab)

            # Ecualizar histograma del canal L (luminancia)
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
            l = clahe.apply(l)

            # Recombinar canales
            lab = cv2.merge((l,a,b))
            image_array = cv2.cvtColor(lab, cv2.COLOR_LAB2RGB)

            return image_array
        except Exception as e:
            print(f"Error preprocesando imagen: {e}")
            return image_array

    @staticmethod
    def extract_face_embedding(image_array, strict_validation=True, grok_client=None):
        """
        Extraer embedding facial inteligente combinando face_recognition con Grok 4 Fast Free
        Ambos métodos funcionan simultáneamente para mayor precisión
        """
        try:
            print("🧠 INICIANDO RECONOCIMIENTO FACIAL INTELIGENTE...")

            # Validar calidad básica de imagen
            quality_ok, quality_msg = FacialRecognitionService.validate_image_quality(image_array)
            if not quality_ok:
                print(f"❌ Imagen no pasa validación: {quality_msg}")
                return {
                    'embedding': None,
                    'model': None,
                    'confidence': 0,
                    'face_detected': False,
                    'detection_method': None
                }

            # Preparar imagen para ambos métodos
            processed_image = FacialRecognitionService.preprocess_image(image_array)

            # Ejecutar ambos métodos en paralelo (simulado)
            face_recognition_result = None
            grok_result = None

            # 1. FACE_RECOGNITION: Detectar rostro y obtener datos detallados
            print("🔍 Ejecutando face_recognition para detección detallada...")
            try:
                face_recognition_data = FacialRecognitionService.extract_face_data_with_face_recognition(processed_image)
                if face_recognition_data['face_detected']:
                    face_recognition_result = face_recognition_data
                    print("✅ Face_recognition detectó rostro exitosamente")
                else:
                    print("❌ Face_recognition no detectó rostros")
            except Exception as e:
                print(f"Error con face_recognition: {e}")

            # 2. GROK 4 FAST FREE: Análisis inteligente con datos de face_recognition
            if grok_client:
                print("🤖 Ejecutando Grok con datos enriquecidos de face_recognition...")
                try:
                    grok_result = FacialRecognitionService.analyze_face_with_grok_enhanced(
                        processed_image,
                        grok_client,
                        face_recognition_data if face_recognition_data else None
                    )
                    if grok_result and grok_result.get('face_detected'):
                        print("✅ Grok analizó rostro exitosamente")
                    else:
                        print("❌ Grok no pudo analizar la imagen")
                except Exception as e:
                    print(f"Error con Grok: {e}")

            # 3. COMBINAR RESULTADOS PARA MAYOR ROBUSTEZ
            final_result = FacialRecognitionService.combine_recognition_results(
                face_recognition_result,
                grok_result
            )

            if final_result['face_detected']:
                print(f"🎯 Reconocimiento facial exitoso - Método: {final_result['model']} (confianza: {final_result['confidence']:.3f})")
            else:
                print("❌ Ambos métodos fallaron - no se pudo reconocer el rostro")

            return final_result

        except Exception as e:
            print(f"Error general en extract_face_embedding: {e}")
            return {
                'embedding': None,
                'model': None,
                'confidence': 0,
                'face_detected': False,
                'detection_method': None
            }

    @staticmethod
    def extract_face_data_with_face_recognition(image_array):
        """
        Extraer datos detallados del rostro usando face_recognition
        Incluye landmarks, bounding box y embedding
        """
        try:
            print("🔬 Extrayendo datos detallados con face_recognition...")

            # Convertir imagen a RGB si es necesario
            if len(image_array.shape) == 2:
                image_array_rgb = cv2.cvtColor(image_array, cv2.COLOR_GRAY2RGB)
            elif image_array.shape[2] == 4:
                image_array_rgb = cv2.cvtColor(image_array, cv2.COLOR_RGBA2RGB)
            else:
                image_array_rgb = image_array

            # Detectar rostros con face_recognition
            face_locations = fr.face_locations(image_array_rgb)

            if not face_locations:
                return {
                    'face_detected': False,
                    'face_locations': None,
                    'landmarks': None,
                    'embedding': None,
                    'confidence': 0
                }

            # Usar el primer rostro detectado (el más prominente)
            top, right, bottom, left = face_locations[0]
            face_location = face_locations[0]

            # Extraer landmarks faciales
            face_landmarks_list = fr.face_landmarks(image_array_rgb, [face_location])
            if face_landmarks_list:
                landmarks = face_landmarks_list[0]
            else:
                landmarks = None

            # Extraer embedding
            face_encodings = fr.face_encodings(image_array_rgb, [face_location])
            if face_encodings:
                embedding = face_encodings[0].tolist()
            else:
                embedding = None

            # Calcular confianza basada en el tamaño del rostro detectado
            face_width = right - left
            face_height = bottom - top
            face_area = face_width * face_height
            image_area = image_array.shape[0] * image_array.shape[1]
            face_ratio = face_area / image_area

            # Confianza basada en proporción del rostro en la imagen
            confidence = min(face_ratio * 4, 0.9)  # Máximo 90% de confianza

            return {
                'face_detected': True,
                'face_locations': (top, right, bottom, left),
                'landmarks': landmarks,
                'embedding': embedding,
                'confidence': confidence,
                'face_ratio': face_ratio,
                'face_dimensions': (face_width, face_height)
            }

        except Exception as e:
            print(f"Error extrayendo datos con face_recognition: {e}")
            return {
                'face_detected': False,
                'face_locations': None,
                'landmarks': None,
                'embedding': None,
                'confidence': 0
            }

    @staticmethod
    def analyze_face_with_grok_enhanced(image_array, grok_client, face_recognition_data=None):
        """
        Analizar rostro con Grok 4 Fast Free usando datos enriquecidos de face_recognition
        """
        try:
            print("🧠 Analizando rostro con Grok usando datos de face_recognition...")

            # Convertir imagen a base64
            pil_image = Image.fromarray(image_array.astype('uint8'), 'RGB')
            buffer = io.BytesIO()
            pil_image.save(buffer, format='JPEG')
            image_base64 = base64.b64encode(buffer.getvalue()).decode()

            # Crear prompt inteligente basado en datos de face_recognition
            prompt = FacialRecognitionService.create_enhanced_grok_prompt(face_recognition_data)

            # Análisis detallado de facciones con IA usando datos enriquecidos
            analysis_response = grok_client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": "https://smartcondominium.com",
                    "X-Title": "Smart Condominium AI",
                },
                model="x-ai/grok-4-fast:free",
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }]
            )

            # Procesar respuesta de IA
            ai_response = analysis_response.choices[0].message.content.strip()
            print(f"📋 Análisis facial inteligente recibido: {len(ai_response)} caracteres")

            # Intentar parsear como JSON, si no, extraer información estructurada
            facial_profile = FacialRecognitionService.parse_facial_analysis(ai_response)

            # Generar embedding basado en el perfil facial
            embedding = FacialRecognitionService.generate_embedding_from_facial_profile(facial_profile)

            return {
                'embedding': embedding,
                'facial_profile': facial_profile,
                'model': 'ai-enhanced-grok-face_recognition',
                'confidence': 0.95,  # Alta confianza en análisis inteligente
                'analysis_text': ai_response,
                'face_detected': True,
                'face_recognition_data': face_recognition_data
            }

        except Exception as e:
            print(f"❌ Error en análisis inteligente con Grok: {e}")
            return None

    @staticmethod
    def create_enhanced_grok_prompt(face_recognition_data):
        """
        Crear un prompt inteligente para Grok basado en datos de face_recognition
        """
        base_prompt = """Analiza detalladamente este rostro humano y proporciona un perfil biométrico completo. """

        if face_recognition_data and face_recognition_data.get('face_detected'):
            # Añadir información específica de face_recognition
            landmarks = face_recognition_data.get('landmarks', {})
            face_ratio = face_recognition_data.get('face_ratio', 0)
            face_dims = face_recognition_data.get('face_dimensions', (0, 0))

            prompt_enhancement = f"""
Los datos técnicos preliminares indican:
- Proporción del rostro en la imagen: {face_ratio:.3f}
- Dimensiones detectadas: {face_dims[0]}x{face_dims[1]} píxeles
- Landmarks faciales detectados: {len(landmarks) if landmarks else 0} puntos

Usa esta información técnica para hacer un análisis más preciso.
"""
            base_prompt += prompt_enhancement

        base_prompt += """
Describe y mide las siguientes características con la mayor precisión posible:

FORMA Y ESTRUCTURA GENERAL:
- Forma general del rostro (redondo, ovalado, cuadrado, rectangular, triangular, diamante)
- Proporciones generales (altura vs ancho)
- Simetría facial general (escala del 1-10)

OJOS:
- Forma de los ojos (almendrados, redondos, rasgados, etc.)
- Tamaño relativo de los ojos
- Distancia entre los ojos (en relación al ancho del rostro)
- Color aproximado de los ojos (si es visible)
- Posición de los ojos (alto, medio, bajo en el rostro)

NARIZ:
- Forma de la nariz (recta, respingona, aguileña, ancha, estrecha)
- Tamaño relativo de la nariz
- Anchura de las fosas nasales
- Longitud de la nariz (en relación a la altura facial)

BOCA Y LABIOS:
- Forma de la boca (ancho, estrecho, con comisuras hacia arriba/abajo)
- Tamaño relativo de la boca
- Grosor de los labios (fino, medio, grueso)
- Forma del arco de Cupido

MENTÓN Y MANDÍBULA:
- Forma del mentón (puntiagudo, cuadrado, redondo)
- Definición de la mandíbula
- Ángulo de la mandíbula

CEJAS:
- Forma de las cejas (rectas, arqueadas, redondeadas)
- Grosor de las cejas
- Distancia entre cejas

MEJILLAS Y POMULOS:
- Prominencia de los pómulos
- Redondez de las mejillas
- Definición de los huesos malares

FRENTE Y SIENAS:
- Altura de la frente (en relación al rostro total)
- Anchura de la frente
- Forma de las sienes

CARACTERÍSTICAS ESPECIALES:
- Pecas, lunares, cicatrices u otros rasgos distintivos
- Expresión facial típica
- Edad aproximada aparente
- Género aparente
- Etnia aproximada

MEDIDAS PROPORCIONALES (en porcentaje del ancho/altura del rostro):
- Distancia vertical ojos-nariz
- Distancia vertical nariz-boca
- Distancia vertical boca-mentón
- Relación ancho ojos/ancho rostro
- Relación ancho boca/ancho rostro
- Relación ancho nariz/ancho rostro

Proporciona la información en formato JSON estructurado con categorías claras y medidas específicas."""

        return base_prompt

    @staticmethod
    def combine_recognition_results(face_recognition_result, grok_result):
        """
        Combinar resultados de ambos métodos para mayor robustez
        """
        try:
            # Si ambos métodos funcionaron, combinar embeddings
            if face_recognition_result and grok_result:
                print("🔄 Combinando resultados de ambos métodos...")

                # Combinar embeddings ponderados
                fr_embedding = np.array(face_recognition_result['embedding']) if face_recognition_result.get('embedding') else None
                grok_embedding = np.array(grok_result['embedding']) if grok_result.get('embedding') else None

                if fr_embedding is not None and grok_embedding is not None:
                    # Ponderación: 60% face_recognition + 40% grok (face_recognition es más preciso para matching)
                    combined_embedding = 0.6 * fr_embedding + 0.4 * grok_embedding
                    combined_confidence = 0.6 * face_recognition_result['confidence'] + 0.4 * grok_result['confidence']

                    return {
                        'embedding': combined_embedding.tolist(),
                        'model': 'hybrid-face_recognition-grok',
                        'confidence': min(combined_confidence, 0.98),  # Máximo 98%
                        'face_detected': True,
                        'detection_method': 'hybrid',
                        'face_recognition_data': face_recognition_result,
                        'grok_data': grok_result
                    }

            # Si solo uno funcionó, usar ese
            if grok_result and grok_result.get('face_detected'):
                return grok_result
            elif face_recognition_result and face_recognition_result.get('face_detected'):
                return {
                    'embedding': face_recognition_result['embedding'],
                    'model': 'face_recognition-fallback',
                    'confidence': face_recognition_result['confidence'] * 0.8,  # Reducir confianza
                    'face_detected': True,
                    'detection_method': 'face_recognition'
                }

            # Si ninguno funcionó
            return {
                'embedding': None,
                'model': None,
                'confidence': 0,
                'face_detected': False,
                'detection_method': None
            }

        except Exception as e:
            print(f"Error combinando resultados: {e}")
            # Fallback al método que funcionó
            if grok_result and grok_result.get('face_detected'):
                return grok_result
            elif face_recognition_result and face_recognition_result.get('face_detected'):
                return face_recognition_result
            else:
                return {
                    'embedding': None,
                    'model': None,
                    'confidence': 0,
                    'face_detected': False,
                    'detection_method': None
                }

    @staticmethod
    def validate_image_quality(image_array):
        """
        Validar calidad de imagen para reconocimiento facial
        Retorna tupla (ok, mensaje)
        """
        try:
            # Validar dimensiones
            height, width = image_array.shape[:2]
            if width < 64 or height < 64:
                return False, "Imagen demasiado pequeña, mínimo 64x64 píxeles"

            if width > 4096 or height > 4096:
                return False, "Imagen demasiado grande, máximo 4096x4096 píxeles"

            # Validar relación de aspecto (permitir proporciones comunes de fotos de rostros)
            aspect_ratio = width / height
            # Permitir desde 3:4 (0.75) hasta 16:9 (1.78) - cubre formatos comunes
            if aspect_ratio < 0.5 or aspect_ratio > 2.0:
                return False, "Relación de aspecto inadecuada, debe estar entre 0.5 y 2.0"

            return True, "Calidad de imagen adecuada"
        except Exception as e:
            return False, f"Error en validación de calidad de imagen: {str(e)}"

    @staticmethod
    def find_best_match(target_embedding, rostros_queryset, min_confidence=0.6):
        """
        Encontrar la mejor coincidencia facial en la base de datos
        target_embedding: embedding de la imagen a comparar
        rostros_queryset: queryset de rostros registrados
        min_confidence: confianza mínima para considerar coincidencia
        Retorna: (mejor_rostro, confianza, distancia)
        """
        try:
            print(f"🔍 Buscando mejor coincidencia entre {len(rostros_queryset)} rostros registrados...")
            best_match = None
            best_confidence = 0
            best_distance = float('inf')

            for rostro in rostros_queryset:
                try:
                    # Obtener embedding almacenado
                    if hasattr(rostro, 'embedding_ia') and rostro.embedding_ia:
                        stored_embedding = rostro.embedding_ia.get('vector', [])
                    else:
                        print(f"⚠️ Rostro {rostro.nombre_identificador} no tiene embedding")
                        continue

                    if not stored_embedding:
                        print(f"⚠️ Embedding vacío para rostro {rostro.nombre_identificador}")
                        continue

                    # Comparar embeddings
                    confidence, distance = FacialRecognitionService.compare_embeddings(target_embedding, stored_embedding)

                    print(f"  📊 Comparación con {rostro.nombre_identificador}: confianza={confidence:.3f}, distancia={distance:.3f}")

                    if confidence > best_confidence and confidence >= min_confidence:
                        best_match = rostro
                        best_confidence = confidence
                        best_distance = distance
                        print(f"    🏆 ¡Nueva mejor coincidencia!")

                except Exception as e:
                    print(f"❌ Error comparando con {rostro.nombre_identificador}: {e}")
                    continue

            if best_match:
                print(f"✅ Mejor coincidencia encontrada: {best_match.nombre_identificador} (confianza: {best_confidence:.3f})")
            else:
                print("❌ No se encontró ninguna coincidencia aceptable")

            return best_match, best_confidence, best_distance

        except Exception as e:
            print(f"Error buscando mejor coincidencia: {e}")
            return None, 0, float('inf')

    @staticmethod
    def compare_embeddings(embedding1, embedding2):
        """
        Comparar dos embeddings faciales
        Retorna: (confianza, distancia)
        """
        try:
            # Convertir a arrays numpy
            emb1 = np.array(embedding1, dtype=np.float32)
            emb2 = np.array(embedding2, dtype=np.float32)

            # Calcular distancia euclidiana
            distance = np.linalg.norm(emb1 - emb2)

            # Convertir distancia a confianza (valores más bajos = mayor confianza)
            # Usar función sigmoide para convertir distancia a confianza
            confidence = 1 / (1 + distance)

            # Ajustar el rango para que distancias pequeñas den alta confianza
            if distance < 0.5:
                confidence = min(confidence * 2, 0.95)  # Máximo 95% para evitar falsos positivos
            elif distance > 2.0:
                confidence = max(confidence * 0.1, 0.01)  # Mínimo 1% para distancias grandes

            return confidence, distance

        except Exception as e:
            print(f"Error comparando embeddings: {e}")
            return 0, float('inf')

    @staticmethod
    def analyze_facial_features_with_ai(image_array, grok_client):
        """
        Analizar características faciales detalladas usando IA (Grok Vision)
        Extrae medidas, proporciones y características específicas del rostro
        """
        try:
            print("🤖 INICIANDO ANÁLISIS DETALLADO DE FACciones CON IA...")

            # Convertir imagen a base64
            pil_image = Image.fromarray(image_array.astype('uint8'), 'RGB')
            buffer = io.BytesIO()
            pil_image.save(buffer, format='JPEG')
            image_base64 = base64.b64encode(buffer.getvalue()).decode()

            # Análisis detallado de facciones con IA
            analysis_response = grok_client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": "https://smartcondominium.com",
                    "X-Title": "Smart Condominium AI",
                },
                model="x-ai/grok-4-fast:free",
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """Analiza detalladamente este rostro humano y proporciona un perfil biométrico completo. Describe y mide las siguientes características con la mayor precisión posible:

FORMA Y ESTRUCTURA GENERAL:
- Forma general del rostro (redondo, ovalado, cuadrado, rectangular, triangular, diamante)
- Proporciones generales (altura vs ancho)
- Simetría facial general (escala del 1-10)

OJOS:
- Forma de los ojos (almendrados, redondos, rasgados, etc.)
- Tamaño relativo de los ojos
- Distancia entre los ojos (en relación al ancho del rostro)
- Color aproximado de los ojos (si es visible)
- Posición de los ojos (alto, medio, bajo en el rostro)

NARIZ:
- Forma de la nariz (recta, respingona, aguileña, ancha, estrecha)
- Tamaño relativo de la nariz
- Anchura de las fosas nasales
- Longitud de la nariz (en relación a la altura facial)

BOCA Y LABIOS:
- Forma de la boca (ancho, estrecho, con comisuras hacia arriba/abajo)
- Tamaño relativo de la boca
- Grosor de los labios (fino, medio, grueso)
- Forma del arco de Cupido

MENTÓN Y MANDÍBULA:
- Forma del mentón (puntiagudo, cuadrado, redondo)
- Definición de la mandíbula
- Ángulo de la mandíbula

CEJAS:
- Forma de las cejas (rectas, arqueadas, redondeadas)
- Grosor de las cejas
- Distancia entre cejas

MEJILLAS Y POMULOS:
- Prominencia de los pómulos
- Redondez de las mejillas
- Definición de los huesos malares

FRENTE Y SIENAS:
- Altura de la frente (en relación al rostro total)
- Anchura de la frente
- Forma de las sienes

CARACTERÍSTICAS ESPECIALES:
- Pecas, lunares, cicatrices u otros rasgos distintivos
- Expresión facial típica
- Edad aproximada aparente
- Género aparente
- Etnia aproximada

MEDIDAS PROPORCIONALES (en porcentaje del ancho/altura del rostro):
- Distancia vertical ojos-nariz
- Distancia vertical nariz-boca
- Distancia vertical boca-mentón
- Relación ancho ojos/ancho rostro
- Relación ancho boca/ancho rostro
- Relación ancho nariz/ancho rostro

Proporciona la información en formato JSON estructurado con categorías claras y medidas específicas."""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }]
            )

            # Procesar respuesta de IA
            ai_response = analysis_response.choices[0].message.content.strip()
            print(f"📋 Análisis facial recibido de IA: {len(ai_response)} caracteres")

            # Intentar parsear como JSON, si no, extraer información estructurada
            facial_profile = FacialRecognitionService.parse_facial_analysis(ai_response)

            # Generar embedding basado en el perfil facial
            embedding = FacialRecognitionService.generate_embedding_from_facial_profile(facial_profile)

            return {
                'embedding': embedding,
                'facial_profile': facial_profile,
                'model': 'ai-facial-analysis-grok',
                'confidence': 0.95,  # Alta confianza en análisis de IA
                'analysis_text': ai_response,
                'face_detected': True
            }

        except Exception as e:
            print(f"❌ Error en análisis facial con IA: {e}")
            # Fallback al método tradicional
            return FacialRecognitionService.extract_face_embedding(image_array)

    @staticmethod
    def clean_json_response(ai_response):
        """
        Limpiar respuesta JSON de la IA para manejar casos malformados
        """
        try:
            # Remover texto antes del primer '{'
            start_idx = ai_response.find('{')
            if start_idx != -1:
                ai_response = ai_response[start_idx:]

            # Remover texto después del último '}'
            end_idx = ai_response.rfind('}')
            if end_idx != -1:
                ai_response = ai_response[:end_idx + 1]

            # Limpiar caracteres de control y espacios extra
            ai_response = ai_response.strip()

            # Intentar reparar comillas simples por dobles en keys
            ai_response = re.sub(r"'([^']*)':", r'"\1":', ai_response)

            # Intentar reparar comillas simples por dobles en valores de string
            ai_response = re.sub(r": '([^']*)'", r': "\1"', ai_response)
            ai_response = re.sub(r": '([^']*),", r': "\1",', ai_response)
            ai_response = re.sub(r": '([^']*)\}", r': "\1"}', ai_response)

            # Limpiar caracteres de escape problemáticos
            ai_response = ai_response.replace('\\n', ' ').replace('\\t', ' ').replace('\\r', ' ')

            # Limpiar espacios múltiples
            ai_response = re.sub(r'\s+', ' ', ai_response)

            return ai_response

        except Exception as e:
            print(f"Error limpiando respuesta JSON: {e}")
            return ai_response

    @staticmethod
    def parse_facial_analysis(ai_response):
        """
        Parsear la respuesta de análisis facial de la IA y estructurarlas
        Maneja JSON malformado y respuestas de texto
        """
        try:
            # Limpiar la respuesta antes de procesar
            cleaned_response = FacialRecognitionService.clean_json_response(ai_response)

            # Intentar parsear como JSON primero
            if cleaned_response.strip().startswith('{'):
                try:
                    return json.loads(cleaned_response)
                except json.JSONDecodeError as json_error:
                    print(f"❌ Error de JSON: {json_error}")
                    print(f"📄 Respuesta limpiada: {cleaned_response[:200]}...")

                    # Intentar extraer JSON válido de una respuesta mixta
                    json_match = re.search(r'\{.*\}', cleaned_response, re.DOTALL)
                    if json_match:
                        try:
                            return json.loads(json_match.group())
                        except json.JSONDecodeError:
                            pass

            # Si no es JSON válido, extraer información estructurada del texto
            print("🔄 Extrayendo información estructurada del texto...")
            facial_profile = {
                'forma_rostro': FacialRecognitionService.extract_feature(cleaned_response, ['forma', 'rostro', 'cara'], ['redondo', 'ovalado', 'cuadrado', 'rectangular', 'triangular', 'diamante']),
                'simetria_general': FacialRecognitionService.extract_numeric_feature(cleaned_response, ['simetría', 'simetria'], 1, 10, 7),

                'ojos': {
                    'forma': FacialRecognitionService.extract_feature(cleaned_response, ['ojos', 'forma'], ['almendrados', 'redondos', 'rasgados', 'caídos', 'arqueados']),
                    'tamano_relativo': FacialRecognitionService.extract_feature(cleaned_response, ['ojos', 'tamaño'], ['grandes', 'medianos', 'pequeños']),
                    'distancia_entre_ojos': FacialRecognitionService.extract_percentage(cleaned_response, ['distancia.*ojos', 'ojos.*distancia']),
                    'color': FacialRecognitionService.extract_feature(cleaned_response, ['color.*ojos', 'ojos.*color'], ['marrones', 'negros', 'azules', 'verdes', 'grises'])
                },

                'nariz': {
                    'forma': FacialRecognitionService.extract_feature(cleaned_response, ['nariz', 'forma'], ['recta', 'respingona', 'aguileña', 'ancha', 'estrecha', 'gruesa']),
                    'tamano_relativo': FacialRecognitionService.extract_feature(cleaned_response, ['nariz', 'tamaño'], ['grande', 'mediana', 'pequeña']),
                    'anchura_fosas': FacialRecognitionService.extract_feature(cleaned_response, ['fosas', 'anchura'], ['anchas', 'estrechas', 'medias'])
                },

                'boca': {
                    'forma': FacialRecognitionService.extract_feature(cleaned_response, ['boca', 'forma'], ['ancho', 'estrecho', 'mediana', 'comisuras']),
                    'tamano_relativo': FacialRecognitionService.extract_feature(cleaned_response, ['boca', 'tamaño'], ['grande', 'mediana', 'pequeña']),
                    'grosor_labios': FacialRecognitionService.extract_feature(cleaned_response, ['labios', 'grosor'], ['finos', 'medios', 'gruesos'])
                },

                'menton': {
                    'forma': FacialRecognitionService.extract_feature(cleaned_response, ['mentón', 'menton', 'forma'], ['puntiagudo', 'cuadrado', 'redondo', 'afilado']),
                    'definicion': FacialRecognitionService.extract_feature(cleaned_response, ['mandíbula', 'mandibula'], ['definida', 'suave', 'marcada'])
                },

                'proporciones': {
                    'altura_frente': FacialRecognitionService.extract_percentage(cleaned_response, ['frente.*altura', 'altura.*frente']),
                    'distancia_ojos_nariz': FacialRecognitionService.extract_percentage(cleaned_response, ['ojos.*nariz', 'distancia.*ojos.*nariz']),
                    'distancia_nariz_boca': FacialRecognitionService.extract_percentage(cleaned_response, ['nariz.*boca', 'distancia.*nariz.*boca']),
                    'relacion_ancho_ojos': FacialRecognitionService.extract_percentage(cleaned_response, ['ojos.*ancho', 'ancho.*ojos']),
                    'relacion_ancho_boca': FacialRecognitionService.extract_percentage(cleaned_response, ['boca.*ancho', 'ancho.*boca'])
                },

                'edad_aparente': FacialRecognitionService.extract_numeric_feature(cleaned_response, ['edad'], 1, 100, 30),
                'genero_aparente': FacialRecognitionService.extract_feature(cleaned_response, ['género', 'genero'], ['masculino', 'femenino', 'no_binario']),
                'etnia_aparente': FacialRecognitionService.extract_feature(cleaned_response, ['etnia', 'origen'], ['caucásico', 'asiático', 'africano', 'latino', 'mestizo'])
            }

            return facial_profile

        except Exception as e:
            print(f"Error parseando análisis facial: {e}")
            return {
                'error': 'No se pudo parsear el análisis facial',
                'raw_response': ai_response[:500]
            }

    @staticmethod
    def extract_feature(text, keywords, possible_values):
        """Extraer una característica específica del texto"""
        text_lower = text.lower()
        for keyword in keywords:
            if keyword.lower() in text_lower:
                for value in possible_values:
                    if value.lower() in text_lower:
                        return value
        return possible_values[0] if possible_values else 'desconocido'

    @staticmethod
    def extract_numeric_feature(text, keywords, min_val, max_val, default):
        """Extraer un valor numérico del texto"""
        text_lower = text.lower()

        for keyword in keywords:
            if keyword.lower() in text_lower:
                # Buscar números en el contexto de la keyword
                numbers = re.findall(r'\d+', text_lower)
                if numbers:
                    num = int(numbers[0])
                    if min_val <= num <= max_val:
                        return num
        return default

    @staticmethod
    def extract_percentage(text, patterns):
        """Extraer porcentajes del texto"""
        text_lower = text.lower()

        for pattern in patterns:
            if re.search(pattern, text_lower):
                # Buscar porcentajes
                percentages = re.findall(r'(\d+(?:\.\d+)?)%', text_lower)
                if percentages:
                    return float(percentages[0]) / 100.0
        return 0.5  # Valor por defecto

    @staticmethod
    def generate_embedding_from_facial_profile(facial_profile):
        """
        Generar un embedding numérico consistente basado en el perfil facial
        """
        try:
            features = []

            # Convertir características categóricas a valores numéricos
            feature_mappings = {
                'forma_rostro': {'redondo': 0.1, 'ovalado': 0.3, 'cuadrado': 0.5, 'rectangular': 0.7, 'triangular': 0.9, 'diamante': 0.8},
                'ojos_forma': {'almendrados': 0.2, 'redondos': 0.4, 'rasgados': 0.6, 'caídos': 0.8, 'arqueados': 0.7},
                'ojos_tamano': {'pequeños': 0.3, 'medianos': 0.5, 'grandes': 0.7},
                'nariz_forma': {'recta': 0.2, 'respingona': 0.4, 'aguileña': 0.6, 'ancha': 0.8, 'estrecha': 0.7},
                'boca_forma': {'estrecha': 0.3, 'mediana': 0.5, 'ancha': 0.7},
                'labios_grosor': {'finos': 0.3, 'medios': 0.5, 'gruesos': 0.7},
                'menton_forma': {'puntiagudo': 0.3, 'cuadrado': 0.5, 'redondo': 0.7},
                'genero': {'masculino': 0.3, 'femenino': 0.7, 'no_binario': 0.5},
                'etnia': {'caucásico': 0.2, 'asiático': 0.4, 'africano': 0.6, 'latino': 0.8, 'mestizo': 0.7}
            }

            # Extraer valores del perfil
            features.append(FacialRecognitionService.safe_float(facial_profile.get('simetria_general', 7)) / 10.0)
            features.append(FacialRecognitionService.safe_float(facial_profile.get('edad_aparente', 30)) / 100.0)

            # Características de ojos
            ojos = facial_profile.get('ojos', {})
            features.append(feature_mappings['ojos_forma'].get(ojos.get('forma', 'almendrados'), 0.2))
            features.append(feature_mappings['ojos_tamano'].get(ojos.get('tamano_relativo', 'medianos'), 0.5))
            features.append(FacialRecognitionService.safe_float(ojos.get('distancia_entre_ojos', 0.3)))

            # Características de nariz
            nariz = facial_profile.get('nariz', {})
            features.append(feature_mappings['nariz_forma'].get(nariz.get('forma', 'recta'), 0.2))
            features.append(feature_mappings['nariz_forma'].get(nariz.get('tamano_relativo', 'mediana'), 0.5))

            # Características de boca
            boca = facial_profile.get('boca', {})
            features.append(feature_mappings['boca_forma'].get(boca.get('forma', 'mediana'), 0.5))
            features.append(feature_mappings['labios_grosor'].get(boca.get('grosor_labios', 'medios'), 0.5))

            # Características de mentón
            menton = facial_profile.get('menton', {})
            features.append(feature_mappings['menton_forma'].get(menton.get('forma', 'redondo'), 0.7))

            # Proporciones
            proporciones = facial_profile.get('proporciones', {})
            features.append(FacialRecognitionService.safe_float(proporciones.get('altura_frente', 0.3)))
            features.append(FacialRecognitionService.safe_float(proporciones.get('distancia_ojos_nariz', 0.3)))
            features.append(FacialRecognitionService.safe_float(proporciones.get('distancia_nariz_boca', 0.3)))
            features.append(FacialRecognitionService.safe_float(proporciones.get('relacion_ancho_ojos', 0.25)))
            features.append(FacialRecognitionService.safe_float(proporciones.get('relacion_ancho_boca', 0.4)))

            # Demográficos
            features.append(feature_mappings['genero'].get(facial_profile.get('genero_aparente', 'femenino'), 0.7))
            features.append(feature_mappings['etnia'].get(facial_profile.get('etnia_aparente', 'latino'), 0.8))

            # Forma del rostro
            features.append(feature_mappings['forma_rostro'].get(facial_profile.get('forma_rostro', 'ovalado'), 0.3))

            # Rellenar hasta 128 dimensiones con valores derivados
            while len(features) < 128:
                # Crear variaciones basadas en las características existentes
                base_value = features[len(features) % len(features)]
                variation = (len(features) * 0.01) % 1.0
                features.append((base_value + variation) % 1.0)

            # Normalizar a rango -1 a 1
            features = [(x * 2 - 1) for x in features[:128]]

            return features

        except Exception as e:
            print(f"Error generando embedding desde perfil facial: {e}")
            # Fallback a embedding básico
            return FacialRecognitionService.extract_basic_embedding(None)['embedding']

    @staticmethod
    def compare_facial_profiles(profile1, profile2):
        """
        Comparar dos perfiles faciales usando IA para determinar similitud
        """
        try:
            # Usar IA para comparar perfiles si está disponible
            # Por ahora usamos comparación numérica
            return FacialRecognitionService.compare_facial_profiles_numeric(profile1, profile2)

        except Exception as e:
            print(f"Error en comparación de perfiles con IA: {e}")

        # Fallback a comparación numérica
        return FacialRecognitionService.compare_facial_profiles_numeric(profile1, profile2)

    @staticmethod
    def compare_facial_profiles_numeric(profile1, profile2):
        """
        Comparar perfiles faciales usando cálculo numérico
        """
        try:
            score = 0.0
            total_features = 0

            # Comparar características principales
            if profile1.get('forma_rostro') == profile2.get('forma_rostro'):
                score += 0.15
            total_features += 0.15

            if profile1.get('simetria_general') and profile2.get('simetria_general'):
                sim_diff = abs(profile1['simetria_general'] - profile2['simetria_general']) / 10.0
                score += 0.1 * (1 - sim_diff)
            total_features += 0.1

            # Comparar ojos
            ojos1 = profile1.get('ojos', {})
            ojos2 = profile2.get('ojos', {})
            if ojos1.get('forma') == ojos2.get('forma'):
                score += 0.1
            if ojos1.get('tamano_relativo') == ojos2.get('tamano_relativo'):
                score += 0.05
            total_features += 0.15

            # Comparar nariz
            nariz1 = profile1.get('nariz', {})
            nariz2 = profile2.get('nariz', {})
            if nariz1.get('forma') == nariz2.get('forma'):
                score += 0.1
            if nariz1.get('tamano_relativo') == nariz2.get('tamano_relativo'):
                score += 0.05
            total_features += 0.15

            # Comparar boca
            boca1 = profile1.get('boca', {})
            boca2 = profile2.get('boca', {})
            if boca1.get('forma') == boca2.get('forma'):
                score += 0.08
            if boca1.get('grosor_labios') == boca2.get('grosor_labios'):
                score += 0.07
            total_features += 0.15

            # Comparar proporciones
            prop1 = profile1.get('proporciones', {})
            prop2 = profile2.get('proporciones', {})
            for key in ['distancia_ojos_nariz', 'distancia_nariz_boca', 'relacion_ancho_ojos', 'relacion_ancho_boca']:
                if key in prop1 and key in prop2:
                    diff = abs(prop1[key] - prop2[key])
                    score += 0.05 * (1 - min(diff * 2, 1))  # Penalizar diferencias grandes

            total_features += 0.2

            # Normalizar score
            if total_features > 0:
                confidence = score / total_features
            else:
                confidence = 0.0

            return {
                'confidence': confidence,
                'similarity_score': score,
                'total_features': total_features,
                'matched_features': score
            }

        except Exception as e:
            print(f"Error en comparación numérica de perfiles: {e}")
            return {
                'confidence': 0.0,
                'similarity_score': 0.0,
                'total_features': 0,
                'matched_features': 0
            }

    @staticmethod
    def extract_basic_embedding(image_array):
        """
        Extraer un embedding básico como fallback cuando otros métodos fallan
        """
        try:
            # Crear un embedding básico de 128 dimensiones con valores aleatorios pero consistentes
            # Usar un hash simple de la forma de la imagen para consistencia
            if image_array is not None:
                shape_hash = hash((image_array.shape[0], image_array.shape[1], image_array.shape[2] if len(image_array.shape) > 2 else 1))
            else:
                shape_hash = hash("fallback")

            # Generar embedding pseudo-aleatorio pero determinístico
            np.random.seed(FacialRecognitionService.safe_random_seed(shape_hash))
            embedding = np.random.normal(0, 0.5, 128).tolist()

            return {
                'embedding': embedding,
                'model': 'basic_fallback',
                'confidence': 0.1,  # Baja confianza para indicar que es fallback
                'face_detected': False
            }

        except Exception as e:
            print(f"Error creando embedding básico: {e}")
            return {
                'embedding': [0.0] * 128,
                'model': 'error_fallback',
                'confidence': 0.0,
                'face_detected': False
            }


# Funciones de compatibilidad para el código existente
def extract_face_embedding_from_base64(base64_image, strict_validation=True):
    """Extraer embedding desde imagen base64 (función de compatibilidad)"""
    try:
        image_array = FacialRecognitionService.decode_base64_image(base64_image)
        result = FacialRecognitionService.extract_face_embedding(image_array, strict_validation=strict_validation)
        return result['embedding']
    except Exception as e:
        print(f"Error extrayendo embedding: {e}")
        return None

def compare_face_embeddings(embedding1, embedding2):
    """Comparar embeddings (función de compatibilidad)"""
    return FacialRecognitionService.compare_faces(embedding1, embedding2)

    @staticmethod
    def validate_image_quality(image_array):
        """
        Validar calidad de imagen para reconocimiento facial
        Retorna tupla (ok, mensaje)
        """
        try:
            # Validar dimensiones
            height, width = image_array.shape[:2]
            if width < 64 or height < 64:
                return False, "Imagen demasiado pequeña, mínimo 64x64 píxeles"

            if width > 4096 or height > 4096:
                return False, "Imagen demasiado grande, máximo 4096x4096 píxeles"

            # Validar relación de aspecto (permitir proporciones comunes de fotos de rostros)
            aspect_ratio = width / height
            # Permitir desde 3:4 (0.75) hasta 16:9 (1.78) - cubre formatos comunes
            if aspect_ratio < 0.5 or aspect_ratio > 2.0:
                return False, "Relación de aspecto inadecuada, debe estar entre 0.5 y 2.0"

            return True, "Calidad de imagen adecuada"
        except Exception as e:
            return False, f"Error en validación de calidad de imagen: {str(e)}"

    @staticmethod
    def find_best_match(target_embedding, rostros_queryset, min_confidence=0.6):
        """
        Encontrar la mejor coincidencia facial en la base de datos
        target_embedding: embedding de la imagen a comparar
        rostros_queryset: queryset de rostros registrados
        min_confidence: confianza mínima para considerar coincidencia
        Retorna: (mejor_rostro, confianza, distancia)
        """
        try:
            print(f"🔍 Buscando mejor coincidencia entre {len(rostros_queryset)} rostros registrados...")
            best_match = None
            best_confidence = 0
            best_distance = float('inf')

            for rostro in rostros_queryset:
                try:
                    # Obtener embedding almacenado
                    if hasattr(rostro, 'embedding_ia') and rostro.embedding_ia:
                        stored_embedding = rostro.embedding_ia.get('vector', [])
                    else:
                        print(f"⚠️ Rostro {rostro.nombre_identificador} no tiene embedding")
                        continue

                    if not stored_embedding:
                        print(f"⚠️ Embedding vacío para rostro {rostro.nombre_identificador}")
                        continue

                    # Comparar embeddings
                    confidence, distance = FacialRecognitionService.compare_embeddings(target_embedding, stored_embedding)

                    print(f"  📊 Comparación con {rostro.nombre_identificador}: confianza={confidence:.3f}, distancia={distance:.3f}")

                    if confidence > best_confidence and confidence >= min_confidence:
                        best_match = rostro
                        best_confidence = confidence
                        best_distance = distance
                        print(f"    🏆 ¡Nueva mejor coincidencia!")

                except Exception as e:
                    print(f"❌ Error comparando con {rostro.nombre_identificador}: {e}")
                    continue

            if best_match:
                print(f"✅ Mejor coincidencia encontrada: {best_match.nombre_identificador} (confianza: {best_confidence:.3f})")
            else:
                print("❌ No se encontró ninguna coincidencia aceptable")

            return best_match, best_confidence, best_distance

        except Exception as e:
            print(f"Error buscando mejor coincidencia: {e}")
            return None, 0, float('inf')

    @staticmethod
    def compare_embeddings(embedding1, embedding2):
        """
        Comparar dos embeddings faciales
        Retorna: (confianza, distancia)
        """
        try:
            # Convertir a arrays numpy
            emb1 = np.array(embedding1, dtype=np.float32)
            emb2 = np.array(embedding2, dtype=np.float32)

            # Calcular distancia euclidiana
            distance = np.linalg.norm(emb1 - emb2)

            # Convertir distancia a confianza (valores más bajos = mayor confianza)
            # Usar función sigmoide para convertir distancia a confianza
            confidence = 1 / (1 + distance)

            # Ajustar el rango para que distancias pequeñas den alta confianza
            if distance < 0.5:
                confidence = min(confidence * 2, 0.95)  # Máximo 95% para evitar falsos positivos
            elif distance > 2.0:
                confidence = max(confidence * 0.1, 0.01)  # Mínimo 1% para distancias grandes

            return confidence, distance

        except Exception as e:
            print(f"Error comparando embeddings: {e}")
            return 0, float('inf')

    @staticmethod
    def analyze_facial_features_with_ai(image_array, grok_client):
        """
        Analizar características faciales detalladas usando IA (Grok Vision)
        Extrae medidas, proporciones y características específicas del rostro
        """
        try:
            print("🤖 INICIANDO ANÁLISIS DETALLADO DE FACciones CON IA...")

            # Convertir imagen a base64
            pil_image = Image.fromarray(image_array.astype('uint8'), 'RGB')
            buffer = io.BytesIO()
            pil_image.save(buffer, format='JPEG')
            image_base64 = base64.b64encode(buffer.getvalue()).decode()

            # Análisis detallado de facciones con IA
            analysis_response = grok_client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": "https://smartcondominium.com",
                    "X-Title": "Smart Condominium AI",
                },
                model="x-ai/grok-4-fast:free",
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """Analiza detalladamente este rostro humano y proporciona un perfil biométrico completo. Describe y mide las siguientes características con la mayor precisión posible:

FORMA Y ESTRUCTURA GENERAL:
- Forma general del rostro (redondo, ovalado, cuadrado, rectangular, triangular, diamante)
- Proporciones generales (altura vs ancho)
- Simetría facial general (escala del 1-10)

OJOS:
- Forma de los ojos (almendrados, redondos, rasgados, etc.)
- Tamaño relativo de los ojos
- Distancia entre los ojos (en relación al ancho del rostro)
- Color aproximado de los ojos (si es visible)
- Posición de los ojos (alto, medio, bajo en el rostro)

NARIZ:
- Forma de la nariz (recta, respingona, aguileña, ancha, estrecha)
- Tamaño relativo de la nariz
- Anchura de las fosas nasales
- Longitud de la nariz (en relación a la altura facial)

BOCA Y LABIOS:
- Forma de la boca (ancho, estrecho, con comisuras hacia arriba/abajo)
- Tamaño relativo de la boca
- Grosor de los labios (fino, medio, grueso)
- Forma del arco de Cupido

MENTÓN Y MANDÍBULA:
- Forma del mentón (puntiagudo, cuadrado, redondo)
- Definición de la mandíbula
- Ángulo de la mandíbula

CEJAS:
- Forma de las cejas (rectas, arqueadas, redondeadas)
- Grosor de las cejas
- Distancia entre cejas

MEJILLAS Y POMULOS:
- Prominencia de los pómulos
- Redondez de las mejillas
- Definición de los huesos malares

FRENTE Y SIENAS:
- Altura de la frente (en relación al rostro total)
- Anchura de la frente
- Forma de las sienes

CARACTERÍSTICAS ESPECIALES:
- Pecas, lunares, cicatrices u otros rasgos distintivos
- Expresión facial típica
- Edad aproximada aparente
- Género aparente
- Etnia aproximada

MEDIDAS PROPORCIONALES (en porcentaje del ancho/altura del rostro):
- Distancia vertical ojos-nariz
- Distancia vertical nariz-boca
- Distancia vertical boca-mentón
- Relación ancho ojos/ancho rostro
- Relación ancho boca/ancho rostro
- Relación ancho nariz/ancho rostro

Proporciona la información en formato JSON estructurado con categorías claras y medidas específicas."""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }]
            )

            # Procesar respuesta de IA
            ai_response = analysis_response.choices[0].message.content.strip()
            print(f"📋 Análisis facial recibido de IA: {len(ai_response)} caracteres")

            # Intentar parsear como JSON, si no, extraer información estructurada
            facial_profile = FacialRecognitionService.parse_facial_analysis(ai_response)

            # Generar embedding basado en el perfil facial
            embedding = FacialRecognitionService.generate_embedding_from_facial_profile(facial_profile)

            return {
                'embedding': embedding,
                'facial_profile': facial_profile,
                'model': 'ai-facial-analysis-grok',
                'confidence': 0.95,  # Alta confianza en análisis de IA
                'analysis_text': ai_response,
                'face_detected': True
            }

        except Exception as e:
            print(f"❌ Error en análisis facial con IA: {e}")
            # Fallback al método tradicional
            return FacialRecognitionService.extract_face_embedding(image_array)

    @staticmethod
    def clean_json_response(ai_response):
        """
        Limpiar respuesta JSON de la IA para manejar casos malformados
        """
        try:
            # Remover texto antes del primer '{'
            start_idx = ai_response.find('{')
            if start_idx != -1:
                ai_response = ai_response[start_idx:]

            # Remover texto después del último '}'
            end_idx = ai_response.rfind('}')
            if end_idx != -1:
                ai_response = ai_response[:end_idx + 1]

            # Limpiar caracteres de control y espacios extra
            ai_response = ai_response.strip()

            # Intentar reparar comillas simples por dobles en keys
            ai_response = re.sub(r"'([^']*)':", r'"\1":', ai_response)

            # Intentar reparar comillas simples por dobles en valores de string
            ai_response = re.sub(r": '([^']*)'", r': "\1"', ai_response)
            ai_response = re.sub(r": '([^']*),", r': "\1",', ai_response)
            ai_response = re.sub(r": '([^']*)\}", r': "\1"}', ai_response)

            # Limpiar caracteres de escape problemáticos
            ai_response = ai_response.replace('\\n', ' ').replace('\\t', ' ').replace('\\r', ' ')

            # Limpiar espacios múltiples
            ai_response = re.sub(r'\s+', ' ', ai_response)

            return ai_response

        except Exception as e:
            print(f"Error limpiando respuesta JSON: {e}")
            return ai_response

    @staticmethod
    def parse_facial_analysis(ai_response):
        """
        Parsear la respuesta de análisis facial de la IA y estructurarlas
        Maneja JSON malformado y respuestas de texto
        """
        try:
            # Limpiar la respuesta antes de procesar
            cleaned_response = FacialRecognitionService.clean_json_response(ai_response)

            # Intentar parsear como JSON primero
            if cleaned_response.strip().startswith('{'):
                try:
                    return json.loads(cleaned_response)
                except json.JSONDecodeError as json_error:
                    print(f"❌ Error de JSON: {json_error}")
                    print(f"📄 Respuesta limpiada: {cleaned_response[:200]}...")

                    # Intentar extraer JSON válido de una respuesta mixta
                    json_match = re.search(r'\{.*\}', cleaned_response, re.DOTALL)
                    if json_match:
                        try:
                            return json.loads(json_match.group())
                        except json.JSONDecodeError:
                            pass

            # Si no es JSON válido, extraer información estructurada del texto
            print("🔄 Extrayendo información estructurada del texto...")
            facial_profile = {
                'forma_rostro': FacialRecognitionService.extract_feature(cleaned_response, ['forma', 'rostro', 'cara'], ['redondo', 'ovalado', 'cuadrado', 'rectangular', 'triangular', 'diamante']),
                'simetria_general': FacialRecognitionService.extract_numeric_feature(cleaned_response, ['simetría', 'simetria'], 1, 10, 7),

                'ojos': {
                    'forma': FacialRecognitionService.extract_feature(cleaned_response, ['ojos', 'forma'], ['almendrados', 'redondos', 'rasgados', 'caídos', 'arqueados']),
                    'tamano_relativo': FacialRecognitionService.extract_feature(cleaned_response, ['ojos', 'tamaño'], ['grandes', 'medianos', 'pequeños']),
                    'distancia_entre_ojos': FacialRecognitionService.extract_percentage(cleaned_response, ['distancia.*ojos', 'ojos.*distancia']),
                    'color': FacialRecognitionService.extract_feature(cleaned_response, ['color.*ojos', 'ojos.*color'], ['marrones', 'negros', 'azules', 'verdes', 'grises'])
                },

                'nariz': {
                    'forma': FacialRecognitionService.extract_feature(cleaned_response, ['nariz', 'forma'], ['recta', 'respingona', 'aguileña', 'ancha', 'estrecha', 'gruesa']),
                    'tamano_relativo': FacialRecognitionService.extract_feature(cleaned_response, ['nariz', 'tamaño'], ['grande', 'mediana', 'pequeña']),
                    'anchura_fosas': FacialRecognitionService.extract_feature(cleaned_response, ['fosas', 'anchura'], ['anchas', 'estrechas', 'medias'])
                },

                'boca': {
                    'forma': FacialRecognitionService.extract_feature(cleaned_response, ['boca', 'forma'], ['ancho', 'estrecho', 'mediana', 'comisuras']),
                    'tamano_relativo': FacialRecognitionService.extract_feature(cleaned_response, ['boca', 'tamaño'], ['grande', 'mediana', 'pequeña']),
                    'grosor_labios': FacialRecognitionService.extract_feature(cleaned_response, ['labios', 'grosor'], ['finos', 'medios', 'gruesos'])
                },

                'menton': {
                    'forma': FacialRecognitionService.extract_feature(cleaned_response, ['mentón', 'menton', 'forma'], ['puntiagudo', 'cuadrado', 'redondo', 'afilado']),
                    'definicion': FacialRecognitionService.extract_feature(cleaned_response, ['mandíbula', 'mandibula'], ['definida', 'suave', 'marcada'])
                },

                'proporciones': {
                    'altura_frente': FacialRecognitionService.extract_percentage(cleaned_response, ['frente.*altura', 'altura.*frente']),
                    'distancia_ojos_nariz': FacialRecognitionService.extract_percentage(cleaned_response, ['ojos.*nariz', 'distancia.*ojos.*nariz']),
                    'distancia_nariz_boca': FacialRecognitionService.extract_percentage(cleaned_response, ['nariz.*boca', 'distancia.*nariz.*boca']),
                    'relacion_ancho_ojos': FacialRecognitionService.extract_percentage(cleaned_response, ['ojos.*ancho', 'ancho.*ojos']),
                    'relacion_ancho_boca': FacialRecognitionService.extract_percentage(cleaned_response, ['boca.*ancho', 'ancho.*boca'])
                },

                'edad_aparente': FacialRecognitionService.extract_numeric_feature(cleaned_response, ['edad'], 1, 100, 30),
                'genero_aparente': FacialRecognitionService.extract_feature(cleaned_response, ['género', 'genero'], ['masculino', 'femenino', 'no_binario']),
                'etnia_aparente': FacialRecognitionService.extract_feature(cleaned_response, ['etnia', 'origen'], ['caucásico', 'asiático', 'africano', 'latino', 'mestizo'])
            }

            return facial_profile

        except Exception as e:
            print(f"Error parseando análisis facial: {e}")
            return {
                'error': 'No se pudo parsear el análisis facial',
                'raw_response': ai_response[:500]
            }

    @staticmethod
    def extract_feature(text, keywords, possible_values):
        """Extraer una característica específica del texto"""
        text_lower = text.lower()
        for keyword in keywords:
            if keyword.lower() in text_lower:
                for value in possible_values:
                    if value.lower() in text_lower:
                        return value
        return possible_values[0] if possible_values else 'desconocido'

    @staticmethod
    def extract_numeric_feature(text, keywords, min_val, max_val, default):
        """Extraer un valor numérico del texto"""
        text_lower = text.lower()

        for keyword in keywords:
            if keyword.lower() in text_lower:
                # Buscar números en el contexto de la keyword
                numbers = re.findall(r'\d+', text_lower)
                if numbers:
                    num = int(numbers[0])
                    if min_val <= num <= max_val:
                        return num
        return default

    @staticmethod
    def extract_percentage(text, patterns):
        """Extraer porcentajes del texto"""
        text_lower = text.lower()

        for pattern in patterns:
            if re.search(pattern, text_lower):
                # Buscar porcentajes
                percentages = re.findall(r'(\d+(?:\.\d+)?)%', text_lower)
                if percentages:
                    return float(percentages[0]) / 100.0
        return 0.5  # Valor por defecto

    @staticmethod
    def generate_embedding_from_facial_profile(facial_profile):
        """
        Generar un embedding numérico consistente basado en el perfil facial
        """
        try:
            features = []

            # Convertir características categóricas a valores numéricos
            feature_mappings = {
                'forma_rostro': {'redondo': 0.1, 'ovalado': 0.3, 'cuadrado': 0.5, 'rectangular': 0.7, 'triangular': 0.9, 'diamante': 0.8},
                'ojos_forma': {'almendrados': 0.2, 'redondos': 0.4, 'rasgados': 0.6, 'caídos': 0.8, 'arqueados': 0.7},
                'ojos_tamano': {'pequeños': 0.3, 'medianos': 0.5, 'grandes': 0.7},
                'nariz_forma': {'recta': 0.2, 'respingona': 0.4, 'aguileña': 0.6, 'ancha': 0.8, 'estrecha': 0.7},
                'boca_forma': {'estrecha': 0.3, 'mediana': 0.5, 'ancha': 0.7},
                'labios_grosor': {'finos': 0.3, 'medios': 0.5, 'gruesos': 0.7},
                'menton_forma': {'puntiagudo': 0.3, 'cuadrado': 0.5, 'redondo': 0.7},
                'genero': {'masculino': 0.3, 'femenino': 0.7, 'no_binario': 0.5},
                'etnia': {'caucásico': 0.2, 'asiático': 0.4, 'africano': 0.6, 'latino': 0.8, 'mestizo': 0.7}
            }

            # Extraer valores del perfil
            features.append(FacialRecognitionService.safe_float(facial_profile.get('simetria_general', 7)) / 10.0)
            features.append(FacialRecognitionService.safe_float(facial_profile.get('edad_aparente', 30)) / 100.0)

            # Características de ojos
            ojos = facial_profile.get('ojos', {})
            features.append(feature_mappings['ojos_forma'].get(ojos.get('forma', 'almendrados'), 0.2))
            features.append(feature_mappings['ojos_tamano'].get(ojos.get('tamano_relativo', 'medianos'), 0.5))
            features.append(FacialRecognitionService.safe_float(ojos.get('distancia_entre_ojos', 0.3)))

            # Características de nariz
            nariz = facial_profile.get('nariz', {})
            features.append(feature_mappings['nariz_forma'].get(nariz.get('forma', 'recta'), 0.2))
            features.append(feature_mappings['nariz_forma'].get(nariz.get('tamano_relativo', 'mediana'), 0.5))

            # Características de boca
            boca = facial_profile.get('boca', {})
            features.append(feature_mappings['boca_forma'].get(boca.get('forma', 'mediana'), 0.5))
            features.append(feature_mappings['labios_grosor'].get(boca.get('grosor_labios', 'medios'), 0.5))

            # Características de mentón
            menton = facial_profile.get('menton', {})
            features.append(feature_mappings['menton_forma'].get(menton.get('forma', 'redondo'), 0.7))

            # Proporciones
            proporciones = facial_profile.get('proporciones', {})
            features.append(FacialRecognitionService.safe_float(proporciones.get('altura_frente', 0.3)))
            features.append(FacialRecognitionService.safe_float(proporciones.get('distancia_ojos_nariz', 0.3)))
            features.append(FacialRecognitionService.safe_float(proporciones.get('distancia_nariz_boca', 0.3)))
            features.append(FacialRecognitionService.safe_float(proporciones.get('relacion_ancho_ojos', 0.25)))
            features.append(FacialRecognitionService.safe_float(proporciones.get('relacion_ancho_boca', 0.4)))

            # Demográficos
            features.append(feature_mappings['genero'].get(facial_profile.get('genero_aparente', 'femenino'), 0.7))
            features.append(feature_mappings['etnia'].get(facial_profile.get('etnia_aparente', 'latino'), 0.8))

            # Forma del rostro
            features.append(feature_mappings['forma_rostro'].get(facial_profile.get('forma_rostro', 'ovalado'), 0.3))

            # Rellenar hasta 128 dimensiones con valores derivados
            while len(features) < 128:
                # Crear variaciones basadas en las características existentes
                base_value = features[len(features) % len(features)]
                variation = (len(features) * 0.01) % 1.0
                features.append((base_value + variation) % 1.0)

            # Normalizar a rango -1 a 1
            features = [(x * 2 - 1) for x in features[:128]]

            return features

        except Exception as e:
            print(f"Error generando embedding desde perfil facial: {e}")
            # Fallback a embedding básico
            return FacialRecognitionService.extract_basic_embedding(None)['embedding']

    @staticmethod
    def extract_basic_embedding(image_array):
        """
        Extraer un embedding básico como fallback cuando otros métodos fallan
        """
        try:
            # Crear un embedding básico de 128 dimensiones con valores aleatorios pero consistentes
            # Usar un hash simple de la forma de la imagen para consistencia
            if image_array is not None:
                shape_hash = hash((image_array.shape[0], image_array.shape[1], image_array.shape[2] if len(image_array.shape) > 2 else 1))
            else:
                shape_hash = hash("fallback")

            # Generar embedding pseudo-aleatorio pero determinístico
            np.random.seed(FacialRecognitionService.safe_random_seed(shape_hash))
            embedding = np.random.normal(0, 0.5, 128).tolist()

            return {
                'embedding': embedding,
                'model': 'basic_fallback',
                'confidence': 0.1,  # Baja confianza para indicar que es fallback
                'face_detected': False
            }

        except Exception as e:
            print(f"Error creando embedding básico: {e}")
            return {
                'embedding': [0.0] * 128,
                'model': 'error_fallback',
                'confidence': 0.0,
                'face_detected': False
            }


# Funciones de compatibilidad para el código existente
def extract_face_embedding_from_base64(base64_image, strict_validation=True):
    """Extraer embedding desde imagen base64 (función de compatibilidad)"""
    try:
        image_array = FacialRecognitionService.decode_base64_image(base64_image)
        result = FacialRecognitionService.extract_face_embedding(image_array, strict_validation=strict_validation)
        return result['embedding']
    except Exception as e:
        print(f"Error extrayendo embedding: {e}")
        return None

def compare_face_embeddings(embedding1, embedding2):
    """Comparar embeddings (función de compatibilidad)"""
    return FacialRecognitionService.compare_faces(embedding1, embedding2)

    @staticmethod
    def validate_image_quality(image_array):
        """
        Validar calidad de imagen para reconocimiento facial
        Retorna tupla (ok, mensaje)
        """
        try:
            # Validar dimensiones
            height, width = image_array.shape[:2]
            if width < 64 or height < 64:
                return False, "Imagen demasiado pequeña, mínimo 64x64 píxeles"

            if width > 4096 or height > 4096:
                return False, "Imagen demasiado grande, máximo 4096x4096 píxeles"

            # Validar relación de aspecto (permitir proporciones comunes de fotos de rostros)
            aspect_ratio = width / height
            # Permitir desde 3:4 (0.75) hasta 16:9 (1.78) - cubre formatos comunes
            if aspect_ratio < 0.5 or aspect_ratio > 2.0:
                return False, "Relación de aspecto inadecuada, debe estar entre 0.5 y 2.0"

            return True, "Calidad de imagen adecuada"
        except Exception as e:
            return False, f"Error en validación de calidad de imagen: {str(e)}"

    @staticmethod
    def find_best_match(target_embedding, rostros_queryset, min_confidence=0.6):
        """
        Encontrar la mejor coincidencia facial en la base de datos
        target_embedding: embedding de la imagen a comparar
        rostros_queryset: queryset de rostros registrados
        min_confidence: confianza mínima para considerar coincidencia
        Retorna: (mejor_rostro, confianza, distancia)
        """
        try:
            print(f"🔍 Buscando mejor coincidencia entre {len(rostros_queryset)} rostros registrados...")
            best_match = None
            best_confidence = 0
            best_distance = float('inf')

            for rostro in rostros_queryset:
                try:
                    # Obtener embedding almacenado
                    if hasattr(rostro, 'embedding_ia') and rostro.embedding_ia:
                        stored_embedding = rostro.embedding_ia.get('vector', [])
                    else:
                        print(f"⚠️ Rostro {rostro.nombre_identificador} no tiene embedding")
                        continue

                    if not stored_embedding:
                        print(f"⚠️ Embedding vacío para rostro {rostro.nombre_identificador}")
                        continue

                    # Comparar embeddings
                    confidence, distance = FacialRecognitionService.compare_embeddings(target_embedding, stored_embedding)

                    print(f"  📊 Comparación con {rostro.nombre_identificador}: confianza={confidence:.3f}, distancia={distance:.3f}")

                    if confidence > best_confidence and confidence >= min_confidence:
                        best_match = rostro
                        best_confidence = confidence
                        best_distance = distance
                        print(f"    🏆 ¡Nueva mejor coincidencia!")

                except Exception as e:
                    print(f"❌ Error comparando con {rostro.nombre_identificador}: {e}")
                    continue

            if best_match:
                print(f"✅ Mejor coincidencia encontrada: {best_match.nombre_identificador} (confianza: {best_confidence:.3f})")
            else:
                print("❌ No se encontró ninguna coincidencia aceptable")

            return best_match, best_confidence, best_distance

        except Exception as e:
            print(f"Error buscando mejor coincidencia: {e}")
            return None, 0, float('inf')

    @staticmethod
    def compare_embeddings(embedding1, embedding2):
        """
        Comparar dos embeddings faciales
        Retorna: (confianza, distancia)
        """
        try:
            # Convertir a arrays numpy
            emb1 = np.array(embedding1, dtype=np.float32)
            emb2 = np.array(embedding2, dtype=np.float32)

            # Calcular distancia euclidiana
            distance = np.linalg.norm(emb1 - emb2)

            # Convertir distancia a confianza (valores más bajos = mayor confianza)
            # Usar función sigmoide para convertir distancia a confianza
            confidence = 1 / (1 + distance)

            # Ajustar el rango para que distancias pequeñas den alta confianza
            if distance < 0.5:
                confidence = min(confidence * 2, 0.95)  # Máximo 95% para evitar falsos positivos
            elif distance > 2.0:
                confidence = max(confidence * 0.1, 0.01)  # Mínimo 1% para distancias grandes

            return confidence, distance

        except Exception as e:
            print(f"Error comparando embeddings: {e}")
            return 0, float('inf')

    @staticmethod
    def analyze_facial_features_with_ai(image_array, grok_client):
        """
        Analizar características faciales detalladas usando IA (Grok Vision)
        Extrae medidas, proporciones y características específicas del rostro
        """
        try:
            print("🤖 INICIANDO ANÁLISIS DETALLADO DE FACciones CON IA...")

            # Convertir imagen a base64
            pil_image = Image.fromarray(image_array.astype('uint8'), 'RGB')
            buffer = io.BytesIO()
            pil_image.save(buffer, format='JPEG')
            image_base64 = base64.b64encode(buffer.getvalue()).decode()

            # Análisis detallado de facciones con IA
            analysis_response = grok_client.chat.completions.create(
                extra_headers={
                    "HTTP-Referer": "https://smartcondominium.com",
                    "X-Title": "Smart Condominium AI",
                },
                model="x-ai/grok-4-fast:free",
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": """Analiza detalladamente este rostro humano y proporciona un perfil biométrico completo. Describe y mide las siguientes características con la mayor precisión posible:

FORMA Y ESTRUCTURA GENERAL:
- Forma general del rostro (redondo, ovalado, cuadrado, rectangular, triangular, diamante)
- Proporciones generales (altura vs ancho)
- Simetría facial general (escala del 1-10)

OJOS:
- Forma de los ojos (almendrados, redondos, rasgados, etc.)
- Tamaño relativo de los ojos
- Distancia entre los ojos (en relación al ancho del rostro)
- Color aproximado de los ojos (si es visible)
- Posición de los ojos (alto, medio, bajo en el rostro)

NARIZ:
- Forma de la nariz (recta, respingona, aguileña, ancha, estrecha)
- Tamaño relativo de la nariz
- Anchura de las fosas nasales
- Longitud de la nariz (en relación a la altura facial)

BOCA Y LABIOS:
- Forma de la boca (ancho, estrecho, con comisuras hacia arriba/abajo)
- Tamaño relativo de la boca
- Grosor de los labios (fino, medio, grueso)
- Forma del arco de Cupido

MENTÓN Y MANDÍBULA:
- Forma del mentón (puntiagudo, cuadrado, redondo)
- Definición de la mandíbula
- Ángulo de la mandíbula

CEJAS:
- Forma de las cejas (rectas, arqueadas, redondeadas)
- Grosor de las cejas
- Distancia entre cejas

MEJILLAS Y POMULOS:
- Prominencia de los pómulos
- Redondez de las mejillas
- Definición de los huesos malares

FRENTE Y SIENAS:
- Altura de la frente (en relación al rostro total)
- Anchura de la frente
- Forma de las sienes

CARACTERÍSTICAS ESPECIALES:
- Pecas, lunares, cicatrices u otros rasgos distintivos
- Expresión facial típica
- Edad aproximada aparente
- Género aparente
- Etnia aproximada

MEDIDAS PROPORCIONALES (en porcentaje del ancho/altura del rostro):
- Distancia vertical ojos-nariz
- Distancia vertical nariz-boca
- Distancia vertical boca-mentón
- Relación ancho ojos/ancho rostro
- Relación ancho boca/ancho rostro
- Relación ancho nariz/ancho rostro

Proporciona la información en formato JSON estructurado con categorías claras y medidas específicas."""
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{image_base64}"
                            }
                        }
                    ]
                }]
            )

            # Procesar respuesta de IA
            ai_response = analysis_response.choices[0].message.content.strip()
            print(f"📋 Análisis facial recibido de IA: {len(ai_response)} caracteres")

            # Intentar parsear como JSON, si no, extraer información estructurada
            facial_profile = FacialRecognitionService.parse_facial_analysis(ai_response)

            # Generar embedding basado en el perfil facial
            embedding = FacialRecognitionService.generate_embedding_from_facial_profile(facial_profile)

            return {
                'embedding': embedding,
                'facial_profile': facial_profile,
                'model': 'ai-facial-analysis-grok',
                'confidence': 0.95,  # Alta confianza en análisis de IA
                'analysis_text': ai_response,
                'face_detected': True
            }

        except Exception as e:
            print(f"❌ Error en análisis facial con IA: {e}")
            # Fallback al método tradicional
            return FacialRecognitionService.extract_face_embedding(image_array)

    @staticmethod
    def clean_json_response(ai_response):
        """
        Limpiar respuesta JSON de la IA para manejar casos malformados
        """
        try:
            # Remover texto antes del primer '{'
            start_idx = ai_response.find('{')
            if start_idx != -1:
                ai_response = ai_response[start_idx:]

            # Remover texto después del último '}'
            end_idx = ai_response.rfind('}')
            if end_idx != -1:
                ai_response = ai_response[:end_idx + 1]

            # Limpiar caracteres de control y espacios extra
            ai_response = ai_response.strip()

            # Intentar reparar comillas simples por dobles en keys
            ai_response = re.sub(r"'([^']*)':", r'"\1":', ai_response)

            # Intentar reparar comillas simples por dobles en valores de string
            ai_response = re.sub(r": '([^']*)'", r': "\1"', ai_response)
            ai_response = re.sub(r": '([^']*),", r': "\1",', ai_response)
            ai_response = re.sub(r": '([^']*)\}", r': "\1"}', ai_response)

            # Limpiar caracteres de escape problemáticos
            ai_response = ai_response.replace('\\n', ' ').replace('\\t', ' ').replace('\\r', ' ')

            # Limpiar espacios múltiples
            ai_response = re.sub(r'\s+', ' ', ai_response)

            return ai_response

        except Exception as e:
            print(f"Error limpiando respuesta JSON: {e}")
            return ai_response

    @staticmethod
    def parse_facial_analysis(ai_response):
        """
        Parsear la respuesta de análisis facial de la IA y estructurarlas
        Maneja JSON malformado y respuestas de texto
        """
        try:
            # Limpiar la respuesta antes de procesar
            cleaned_response = FacialRecognitionService.clean_json_response(ai_response)

            # Intentar parsear como JSON primero
            if cleaned_response.strip().startswith('{'):
                try:
                    return json.loads(cleaned_response)
                except json.JSONDecodeError as json_error:
                    print(f"❌ Error de JSON: {json_error}")
                    print(f"📄 Respuesta limpiada: {cleaned_response[:200]}...")

                    # Intentar extraer JSON válido de una respuesta mixta
                    json_match = re.search(r'\{.*\}', cleaned_response, re.DOTALL)
                    if json_match:
                        try:
                            return json.loads(json_match.group())
                        except json.JSONDecodeError:
                            pass

            # Si no es JSON válido, extraer información estructurada del texto
            print("🔄 Extrayendo información estructurada del texto...")
            facial_profile = {
                'forma_rostro': FacialRecognitionService.extract_feature(cleaned_response, ['forma', 'rostro', 'cara'], ['redondo', 'ovalado', 'cuadrado', 'rectangular', 'triangular', 'diamante']),
                'simetria_general': FacialRecognitionService.extract_numeric_feature(cleaned_response, ['simetría', 'simetria'], 1, 10, 7),

                'ojos': {
                    'forma': FacialRecognitionService.extract_feature(cleaned_response, ['ojos', 'forma'], ['almendrados', 'redondos', 'rasgados', 'caídos', 'arqueados']),
                    'tamano_relativo': FacialRecognitionService.extract_feature(cleaned_response, ['ojos', 'tamaño'], ['grandes', 'medianos', 'pequeños']),
                    'distancia_entre_ojos': FacialRecognitionService.extract_percentage(cleaned_response, ['distancia.*ojos', 'ojos.*distancia']),
                    'color': FacialRecognitionService.extract_feature(cleaned_response, ['color.*ojos', 'ojos.*color'], ['marrones', 'negros', 'azules', 'verdes', 'grises'])
                },

                'nariz': {
                    'forma': FacialRecognitionService.extract_feature(cleaned_response, ['nariz', 'forma'], ['recta', 'respingona', 'aguileña', 'ancha', 'estrecha', 'gruesa']),
                    'tamano_relativo': FacialRecognitionService.extract_feature(cleaned_response, ['nariz', 'tamaño'], ['grande', 'mediana', 'pequeña']),
                    'anchura_fosas': FacialRecognitionService.extract_feature(cleaned_response, ['fosas', 'anchura'], ['anchas', 'estrechas', 'medias'])
                },

                'boca': {
                    'forma': FacialRecognitionService.extract_feature(cleaned_response, ['boca', 'forma'], ['ancho', 'estrecho', 'mediana', 'comisuras']),
                    'tamano_relativo': FacialRecognitionService.extract_feature(cleaned_response, ['boca', 'tamaño'], ['grande', 'mediana', 'pequeña']),
                    'grosor_labios': FacialRecognitionService.extract_feature(cleaned_response, ['labios', 'grosor'], ['finos', 'medios', 'gruesos'])
                },

                'menton': {
                    'forma': FacialRecognitionService.extract_feature(cleaned_response, ['mentón', 'menton', 'forma'], ['puntiagudo', 'cuadrado', 'redondo', 'afilado']),
                    'definicion': FacialRecognitionService.extract_feature(cleaned_response, ['mandíbula', 'mandibula'], ['definida', 'suave', 'marcada'])
                },

                'proporciones': {
                    'altura_frente': FacialRecognitionService.extract_percentage(cleaned_response, ['frente.*altura', 'altura.*frente']),
                    'distancia_ojos_nariz': FacialRecognitionService.extract_percentage(cleaned_response, ['ojos.*nariz', 'distancia.*ojos.*nariz']),
                    'distancia_nariz_boca': FacialRecognitionService.extract_percentage(cleaned_response, ['nariz.*boca', 'distancia.*nariz.*boca']),
                    'relacion_ancho_ojos': FacialRecognitionService.extract_percentage(cleaned_response, ['ojos.*ancho', 'ancho.*ojos']),
                    'relacion_ancho_boca': FacialRecognitionService.extract_percentage(cleaned_response, ['boca.*ancho', 'ancho.*boca'])
                },

                'edad_aparente': FacialRecognitionService.extract_numeric_feature(cleaned_response, ['edad'], 1, 100, 30),
                'genero_aparente': FacialRecognitionService.extract_feature(cleaned_response, ['género', 'genero'], ['masculino', 'femenino', 'no_binario']),
                'etnia_aparente': FacialRecognitionService.extract_feature(cleaned_response, ['etnia', 'origen'], ['caucásico', 'asiático', 'africano', 'latino', 'mestizo'])
            }

            return facial_profile

        except Exception as e:
            print(f"Error parseando análisis facial: {e}")
            return {
                'error': 'No se pudo parsear el análisis facial',
                'raw_response': ai_response[:500]
            }

    @staticmethod
    def extract_feature(text, keywords, possible_values):
        """Extraer una característica específica del texto"""
        text_lower = text.lower()
        for keyword in keywords:
            if keyword.lower() in text_lower:
                for value in possible_values:
                    if value.lower() in text_lower:
                        return value
        return possible_values[0] if possible_values else 'desconocido'

    @staticmethod
    def extract_numeric_feature(text, keywords, min_val, max_val, default):
        """Extraer un valor numérico del texto"""
        text_lower = text.lower()

        for keyword in keywords:
            if keyword.lower() in text_lower:
                # Buscar números en el contexto de la keyword
                numbers = re.findall(r'\d+', text_lower)
                if numbers:
                    num = int(numbers[0])
                    if min_val <= num <= max_val:
                        return num
        return default

    @staticmethod
    def extract_percentage(text, patterns):
        """Extraer porcentajes del texto"""
        text_lower = text.lower()

        for pattern in patterns:
            if re.search(pattern, text_lower):
                # Buscar porcentajes
                percentages = re.findall(r'(\d+(?:\.\d+)?)%', text_lower)
                if percentages:
                    return float(percentages[0]) / 100.0
        return 0.5  # Valor por defecto

    @staticmethod
    def generate_embedding_from_facial_profile(facial_profile):
        """
        Generar un embedding numérico consistente basado en el perfil facial
        """
        try:
            features = []

            # Convertir características categóricas a valores numéricos
            feature_mappings = {
                'forma_rostro': {'redondo': 0.1, 'ovalado': 0.3, 'cuadrado': 0.5, 'rectangular': 0.7, 'triangular': 0.9, 'diamante': 0.8},
                'ojos_forma': {'almendrados': 0.2, 'redondos': 0.4, 'rasgados': 0.6, 'caídos': 0.8, 'arqueados': 0.7},
                'ojos_tamano': {'pequeños': 0.3, 'medianos': 0.5, 'grandes': 0.7},
                'nariz_forma': {'recta': 0.2, 'respingona': 0.4, 'aguileña': 0.6, 'ancha': 0.8, 'estrecha': 0.7},
                'boca_forma': {'estrecha': 0.3, 'mediana': 0.5, 'ancha': 0.7},
                'labios_grosor': {'finos': 0.3, 'medios': 0.5, 'gruesos': 0.7},
                'menton_forma': {'puntiagudo': 0.3, 'cuadrado': 0.5, 'redondo': 0.7},
                'genero': {'masculino': 0.3, 'femenino': 0.7, 'no_binario': 0.5},
                'etnia': {'caucásico': 0.2, 'asiático': 0.4, 'africano': 0.6, 'latino': 0.8, 'mestizo': 0.7}
            }

            # Extraer valores del perfil
            features.append(FacialRecognitionService.safe_float(facial_profile.get('simetria_general', 7)) / 10.0)
            features.append(FacialRecognitionService.safe_float(facial_profile.get('edad_aparente', 30)) / 100.0)

            # Características de ojos
            ojos = facial_profile.get('ojos', {})
            features.append(feature_mappings['ojos_forma'].get(ojos.get('forma', 'almendrados'), 0.2))
            features.append(feature_mappings['ojos_tamano'].get(ojos.get('tamano_relativo', 'medianos'), 0.5))
            features.append(FacialRecognitionService.safe_float(ojos.get('distancia_entre_ojos', 0.3)))

            # Características de nariz
            nariz = facial_profile.get('nariz', {})
            features.append(feature_mappings['nariz_forma'].get(nariz.get('forma', 'recta'), 0.2))
            features.append(feature_mappings['nariz_forma'].get(nariz.get('tamano_relativo', 'mediana'), 0.5))

            # Características de boca
            boca = facial_profile.get('boca', {})
            features.append(feature_mappings['boca_forma'].get(boca.get('forma', 'mediana'), 0.5))
            features.append(feature_mappings['labios_grosor'].get(boca.get('grosor_labios', 'medios'), 0.5))

            # Características de mentón
            menton = facial_profile.get('menton', {})
            features.append(feature_mappings['menton_forma'].get(menton.get('forma', 'redondo'), 0.7))

            # Proporciones
            proporciones = facial_profile.get('proporciones', {})
            features.append(FacialRecognitionService.safe_float(proporciones.get('altura_frente', 0.3)))
            features.append(FacialRecognitionService.safe_float(proporciones.get('distancia_ojos_nariz', 0.3)))
            features.append(FacialRecognitionService.safe_float(proporciones.get('distancia_nariz_boca', 0.3)))
            features.append(FacialRecognitionService.safe_float(proporciones.get('relacion_ancho_ojos', 0.25)))
            features.append(FacialRecognitionService.safe_float(proporciones.get('relacion_ancho_boca', 0.4)))

            # Demográficos
            features.append(feature_mappings['genero'].get(facial_profile.get('genero_aparente', 'femenino'), 0.7))
            features.append(feature_mappings['etnia'].get(facial_profile.get('etnia_aparente', 'latino'), 0.8))

            # Forma del rostro
            features.append(feature_mappings['forma_rostro'].get(facial_profile.get('forma_rostro', 'ovalado'), 0.3))

            # Rellenar hasta 128 dimensiones con valores derivados
            while len(features) < 128:
                # Crear variaciones basadas en las características existentes
                base_value = features[len(features) % len(features)]
                variation = (len(features) * 0.01) % 1.0
                features.append((base_value + variation) % 1.0)

            # Normalizar a rango -1 a 1
            features = [(x * 2 - 1) for x in features[:128]]

            return features

        except Exception as e:
            print(f"Error generando embedding desde perfil facial: {e}")
            # Fallback a embedding básico
            return FacialRecognitionService.extract_basic_embedding(None)['embedding']

    @staticmethod
    def extract_basic_embedding(image_array):
        """
        Extraer un embedding básico como fallback cuando otros métodos fallan
        """
        try:
            # Crear un embedding básico de 128 dimensiones con valores aleatorios pero consistentes
            # Usar un hash simple de la forma de la imagen para consistencia
            if image_array is not None:
                shape_hash = hash((image_array.shape[0], image_array.shape[1], image_array.shape[2] if len(image_array.shape) > 2 else 1))
            else:
                shape_hash = hash("fallback")

            # Generar embedding pseudo-aleatorio pero determinístico
            np.random.seed(FacialRecognitionService.safe_random_seed(shape_hash))
            embedding = np.random.normal(0, 0.5, 128).tolist()

            return {
                'embedding': embedding,
                'model': 'basic_fallback',
                'confidence': 0.1,  # Baja confianza para indicar que es fallback
                'face_detected': False
            }

        except Exception as e:
            print(f"Error creando embedding básico: {e}")
            return {
                'embedding': [0.0] * 128,
                'model': 'error_fallback',
                'confidence': 0.0,
                'face_detected': False
            }

# Funciones de compatibilidad para el código existente
def extract_face_embedding_from_base64(base64_image, strict_validation=True):
    """Extraer embedding desde imagen base64 (función de compatibilidad)"""
    try:
        image_array = FacialRecognitionService.decode_base64_image(base64_image)
        result = FacialRecognitionService.extract_face_embedding(image_array, strict_validation=strict_validation)
        return result['embedding']
    except Exception as e:
        print(f"Error extrayendo embedding: {e}")
        return None

def compare_face_embeddings(embedding1, embedding2):
    """Comparar embeddings (función de compatibilidad)"""
    return FacialRecognitionService.compare_faces(embedding1, embedding2)
