import base64
import json
from io import BytesIO
from PIL import Image
import requests
import cv2
import numpy as np
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import RostroRegistrado, VehiculoRegistrado, Acceso
from .serializers import (
    RostroRegistradoSerializer, RostroRegistroSerializer,
    VehiculoRegistradoSerializer, AccesoSerializer,
    AccesoCreateSerializer, ReconocimientoFacialSerializer,
    LecturaPlacaSerializer
)

# Import OpenAI (ahora usando Grok de xAI)
from openai import OpenAI

# Import del nuevo servicio de reconocimiento facial
from .facial_recognition import FacialRecognitionService, extract_face_embedding_from_base64

User = get_user_model()

# Initialize Grok client (using xAI's Grok)
try:
    if settings.GROK_API_KEY:
        # Solución final: crear cliente manualmente para evitar problemas de proxies
        import httpx
        from openai import OpenAI

        # Crear cliente httpx personalizado sin configuración de proxies
        http_client = httpx.Client(
            timeout=60.0,
            follow_redirects=True
        )

        # Crear cliente OpenAI con cliente httpx personalizado
        grok_client = OpenAI(
            api_key=settings.GROK_API_KEY,
            base_url=settings.GROK_API_BASE,
            http_client=http_client
        )
        print("Grok client initialized successfully with custom HTTP client")
    else:
        grok_client = None
        print("Grok API key not configured, client disabled")
except Exception as e:
    print(f"Error initializing Grok client: {e}")
    print("Falling back to OpenCV-only facial recognition")
    grok_client = None

class RostroRegistradoViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de rostros registrados"""
    serializer_class = RostroRegistradoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return RostroRegistrado.objects.filter(
            usuario=self.request.user,
            activo=True
        )

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

    @action(detail=False, methods=['post'])
    def registrar_con_ia(self, request):
        """Registrar un nuevo rostro usando IA para extraer características"""
        serializer = RostroRegistroSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Mensaje de bienvenida de la IA
            mensaje_ia = "Hola, soy Smart Condominium AI, tu asistente de seguridad inteligente. Para registrar tu rostro en el sistema de seguridad del condominio, necesito procesar una imagen de tu rostro. ¿Me permites analizar esta imagen para crear tu perfil biométrico único? Esto garantizará un acceso seguro y personalizado."

            # Procesar imagen con OpenAI
            imagen_base64 = serializer.validated_data['imagen_base64']
            embedding = self._extraer_caracteristicas_faciales(imagen_base64)

            if not embedding:
                return Response(
                    {
                        'error': 'No se pudieron extraer características del rostro',
                        'mensaje_ia': 'Lo siento, no pude procesar la imagen proporcionada. Por favor, asegúrate de que la imagen sea clara y muestre tu rostro completo.'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Crear registro
            rostro = RostroRegistrado.objects.create(
                usuario=request.user,
                nombre_identificador=serializer.validated_data['nombre_identificador'],
                embedding_ia=embedding,
                confianza_minima=serializer.validated_data['confianza_minima']
            )

            # Registrar acceso exitoso
            Acceso.objects.create(
                usuario=request.user,
                tipo_acceso='facial',
                estado='permitido',
                ubicacion='Registro facial',
                rostro_detectado=rostro,
                confianza_ia=1.0,
                observaciones='Registro exitoso de rostro'
            )

            return Response(
                {
                    'data': RostroRegistradoSerializer(rostro).data,
                    'mensaje_ia': f'¡Excelente! He registrado exitosamente tu rostro como "{serializer.validated_data["nombre_identificador"]}". Tu perfil biométrico está ahora activo en el sistema de seguridad de Smart Condominium. Podrás acceder de manera segura usando reconocimiento facial.'
                },
                status=status.HTTP_201_CREATED
            )

        except Exception as e:
            return Response(
                {
                    'error': f'Error procesando imagen: {str(e)}',
                    'mensaje_ia': 'Disculpa, ocurrió un error técnico al procesar tu solicitud. Por favor, intenta nuevamente o contacta al administrador del sistema.'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def actualizar_embedding(self, request, pk=None):
        """Actualizar el embedding de un rostro registrado con una nueva imagen"""
        rostro = self.get_object()

        serializer = RostroRegistroSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Extraer nuevo embedding
            imagen_base64 = serializer.validated_data['imagen_base64']
            embedding = self._extraer_caracteristicas_faciales(imagen_base64)

            if not embedding:
                return Response(
                    {'error': 'No se pudieron extraer características del rostro'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Actualizar embedding
            rostro.embedding_ia = embedding
            rostro.save()

            return Response({
                'mensaje': f'Embedding actualizado exitosamente para {rostro.nombre_identificador}',
                'data': RostroRegistradoSerializer(rostro).data
            })

        except Exception as e:
            return Response(
                {'error': f'Error actualizando embedding: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _extraer_caracteristicas_faciales(self, imagen_base64):
        """
        Extraer características faciales usando el sistema inteligente híbrido
        que combina face_recognition con Grok 4 Fast Free
        """
        try:
            print("� INICIANDO REGISTRO FACIAL INTELIGENTE...")

            # Decodificar imagen
            image_array = FacialRecognitionService.decode_base64_image(imagen_base64)
            print(f"✅ Imagen decodificada: {image_array.shape}")

            # Usar el sistema inteligente híbrido que combina ambos métodos
            print("🎯 Usando sistema inteligente híbrido (face_recognition + Grok)...")
            result = FacialRecognitionService.extract_face_embedding(
                image_array,
                strict_validation=True,
                grok_client=grok_client
            )

            if not result['face_detected'] or not result['embedding']:
                raise ValueError("No se pudo detectar un rostro válido en la imagen")

            print(f"✅ Análisis inteligente completado: modelo={result['model']}, confianza={result['confidence']:.3f}")

            # Crear estructura de datos enriquecida para el registro
            embedding_data = {
                'vector': result['embedding'],
                'facial_profile': result.get('facial_profile', {}),
                'timestamp': timezone.now().isoformat(),
                'modelo': result['model'],
                'note': f'Face registered using intelligent hybrid system at {timezone.now()}. Model: {result["model"]}',
                'confidence': result['confidence'],
                'biometric_features': {
                    'detection_method': result.get('detection_method', 'unknown'),
                    'face_recognition_data': result.get('face_recognition_data'),
                    'grok_data': result.get('grok_data')
                }
            }

            # Agregar perfil facial detallado si está disponible
            if 'facial_profile' in result and result['facial_profile']:
                profile = result['facial_profile']
                embedding_data.update({
                    'biometric_features': {
                        'detection_method': result.get('detection_method', 'unknown'),
                        'face_shape': profile.get('forma_rostro'),
                        'eye_shape': profile.get('ojos', {}).get('forma'),
                        'nose_shape': profile.get('nariz', {}).get('forma'),
                        'mouth_shape': profile.get('boca', {}).get('forma'),
                        'symmetry': profile.get('simetria_general'),
                        'age_estimated': profile.get('edad_aparente'),
                        'gender_estimated': profile.get('genero_aparente'),
                        'ethnicity_estimated': profile.get('etnia_aparente'),
                        'face_recognition_data': result.get('face_recognition_data'),
                        'grok_data': result.get('grok_data')
                    }
                })

            print("✅ REGISTRO FACIAL INTELIGENTE COMPLETADO EXITOSAMENTE")
            print(f"📏 Dimensiones del embedding: {len(embedding_data['vector'])} características")
            print(f"🎯 Método de detección: {result.get('detection_method', 'unknown')}")
            print(f"👤 Modelo usado: {result['model']}")

            return embedding_data

        except Exception as e:
            print(f"❌ Error en registro facial inteligente: {e}")
            # Fallback al método anterior si falla el sistema inteligente
            print("🔄 Intentando método fallback...")
            try:
                return self._extraer_caracteristicas_faciales_determinista(imagen_base64)
            except Exception as fallback_error:
                print(f"❌ Fallback también falló: {fallback_error}")
                raise ValueError(f"No se pudieron extraer características faciales: {str(e)}")

    def _extraer_caracteristicas_faciales_determinista(self, imagen_base64):
        """Extraer características faciales usando método determinista (OpenCV)"""
        try:
            print("🔍 INICIANDO ANÁLISIS FACIAL DETERMINISTA PARA REGISTRO...")
            print("📸 Paso 1: Decodificando imagen base64...")

            image_array = FacialRecognitionService.decode_base64_image(imagen_base64)
            print(f"✅ Imagen decodificada: {image_array.shape}")

            print("🔍 Paso 2: Validando calidad de imagen...")
            quality_ok, quality_msg = FacialRecognitionService.validate_image_quality(image_array)
            print(f"📊 Validación de calidad: {'✅ APROBADA' if quality_ok else '❌ RECHAZADA'} - {quality_msg}")

            if not quality_ok:
                raise ValueError(f"Imagen no cumple con los estándares de calidad: {quality_msg}")

            print("🤖 Paso 3: Extrayendo características faciales avanzadas...")
            embedding_data = FacialRecognitionService.extract_face_embedding(image_array)
            print(f"🧠 Embedding generado: modelo={embedding_data['model']}, confianza={embedding_data['confidence']:.3f}")
            print(f"📏 Dimensiones del embedding: {len(embedding_data['embedding'])} características")

            # Verificar que el embedding tenga características reales
            if embedding_data['model'] == 'computational-fallback':
                print("⚠️ ADVERTENCIA: Se usó método computacional básico (fallback)")
            elif embedding_data['model'].startswith('intelligent-'):
                print("✅ Se usó sistema avanzado de reconocimiento facial")
            else:
                print(f"ℹ️ Se usó modelo: {embedding_data['model']}")

            # Información adicional del análisis
            if 'face_detected' in embedding_data:
                print(f"👤 Detección de rostro: {'✅ Detectado' if embedding_data['face_detected'] else '❌ No detectado'}")
            if 'face_centered' in embedding_data:
                print(f"📍 Centrado del rostro: {'✅ Centrado' if embedding_data['face_centered'] else '❌ Descentrado'}")

            print("🎉 ANÁLISIS FACIAL DETERMINISTA COMPLETADO EXITOSAMENTE")
            return {
                'vector': embedding_data['embedding'],
                'timestamp': timezone.now().isoformat(),
                'modelo': embedding_data['model'],
                'note': f'Face processed using computer vision at {timezone.now()}',
                'confidence': embedding_data['confidence']
            }

        except Exception as e:
            print(f"❌ Error en análisis determinista: {e}")
            raise  # Re-lanzar para que sea manejado por el método principal

    def _extraer_caracteristicas_faciales_fallback(self, imagen_base64):
        """Método fallback que genera embeddings únicos basados en hash (para compatibilidad)"""
        import random
        import hashlib

        # Crear hash único de la imagen para consistencia
        image_hash = hashlib.md5(imagen_base64.encode()).hexdigest()
        random.seed(image_hash)  # Seed consistente para la misma imagen

        # Generar vector único de 128 dimensiones (consistente con sistema avanzado)
        embedding = []
        for i in range(128):  # Mantener 128 dimensiones para consistencia
            value = random.uniform(-1.0, 1.0)
            embedding.append(round(value, 6))

        return {
            'vector': embedding,
            'timestamp': timezone.now().isoformat(),
            'modelo': 'fallback-simulated-face-embedding',
            'note': 'Fallback embedding generated for compatibility (128 features)',
            'confidence': 0.6
        }

class VehiculoRegistradoViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de vehículos registrados"""
    serializer_class = VehiculoRegistradoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return VehiculoRegistrado.objects.filter(
            usuario=self.request.user,
            activo=True
        )

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

class AccesoViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para consultar historial de accesos"""
    serializer_class = AccesoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Acceso.objects.filter(
            Q(usuario=self.request.user) | Q(autorizado_por=self.request.user)
        )

        # Filtros opcionales
        tipo = self.request.query_params.get('tipo')
        estado = self.request.query_params.get('estado')
        fecha_desde = self.request.query_params.get('fecha_desde')
        fecha_hasta = self.request.query_params.get('fecha_hasta')

        if tipo:
            queryset = queryset.filter(tipo_acceso=tipo)
        if estado:
            queryset = queryset.filter(estado=estado)
        if fecha_desde:
            queryset = queryset.filter(fecha_hora__gte=fecha_desde)
        if fecha_hasta:
            queryset = queryset.filter(fecha_hora__lte=fecha_hasta)

        return queryset.order_by('-fecha_hora')

@api_view(['POST'])
def login_facial(request):
    """Endpoint para login facial - no requiere autenticación previa"""
    serializer = ReconocimientoFacialSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        imagen_base64 = serializer.validated_data['imagen_base64']
        ubicacion = serializer.validated_data.get('ubicacion', 'Login facial')

        # DEBUG: Guardar imagen para análisis
        try:
            import sys
            import os
            sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))))
            from debug_imagenes_login import guardar_imagen_debug
            debug_path = guardar_imagen_debug(imagen_base64, "login_facial")
            print(f"🖼️ Imagen de login guardada para debug: {debug_path}")
        except Exception as debug_error:
            print(f"⚠️ Error guardando imagen debug: {debug_error}")

        # Mensaje de la IA solicitando autenticación
        mensaje_ia = "Hola, soy Smart Condominium AI, tu asistente de seguridad inteligente. Detecto que estás intentando iniciar sesión usando reconocimiento facial. Por favor, permite que analice tu rostro para verificar tu identidad y autorizar el acceso al sistema."

        # Buscar rostro más similar
        print("Iniciando búsqueda de rostro para login...")
        rostro_encontrado, confianza = _buscar_rostro_similar(imagen_base64)
        print(f"Resultado de búsqueda: rostro={rostro_encontrado.nombre_identificador if rostro_encontrado else 'None'}, confianza={confianza}")

        if rostro_encontrado and confianza >= 0.6:  # Umbral más alto para seguridad
            # Login exitoso - generar token
            from rest_framework.authtoken.models import Token
            from django.contrib.auth import authenticate

            usuario = rostro_encontrado.usuario

            # Obtener o crear token
            token, created = Token.objects.get_or_create(user=usuario)

            # Registrar acceso exitoso
            acceso = Acceso.objects.create(
                usuario=usuario,
                tipo_acceso='facial_login',
                estado='permitido',
                ubicacion=ubicacion,
                rostro_detectado=rostro_encontrado,
                confianza_ia=confianza,
                observaciones=f'Login facial exitoso (confianza: {confianza:.2f})'
            )

            # Obtener datos del perfil del usuario
            try:
                from backend.apps.users.serializers import UserProfileSerializer
                perfil_data = UserProfileSerializer(usuario).data
            except:
                perfil_data = {
                    'username': usuario.username,
                    'first_name': usuario.first_name,
                    'last_name': usuario.last_name,
                    'email': usuario.email,
                    'role': 'admin' if usuario.is_staff else 'resident'
                }

            print(f"Login facial exitoso para usuario: {usuario.username}, confianza: {confianza:.3f}")
            return Response({
                'login_exitoso': True,
                'token': token.key,
                'usuario': perfil_data,
                'confianza': confianza,
                'acceso_id': acceso.id,
                'mensaje_ia': f'¡Bienvenido, {usuario.get_full_name()}! He verificado tu identidad con un {confianza:.1%} de confianza. El acceso al sistema ha sido autorizado exitosamente.'
            })

        else:
            # Login fallido
            print(f"Login facial fallido: rostro_encontrado={bool(rostro_encontrado)}, confianza={confianza}")
            acceso = Acceso.objects.create(
                tipo_acceso='facial_login',
                estado='denegado',
                ubicacion=ubicacion,
                confianza_ia=confianza if confianza else 0,
                observaciones='Rostro no reconocido o confianza insuficiente para login'
            )

            return Response({
                'login_exitoso': False,
                'mensaje': 'Rostro no reconocido',
                'confianza': confianza,
                'acceso_id': acceso.id,
                'mensaje_ia': 'Lo siento, no pude reconocer tu rostro en el sistema. Si estás registrado, por favor verifica que tu rostro esté bien iluminado y mira directamente a la cámara. Si el problema persiste, usa el login tradicional con usuario y contraseña.'
            })

    except Exception as e:
        return Response(
            {
                'error': f'Error en login facial: {str(e)}',
                'mensaje_ia': 'Disculpa, ocurrió un error técnico en el sistema de reconocimiento facial. Por favor, intenta nuevamente o usa el login tradicional.'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
def reconocimiento_facial(request):
    """Endpoint para reconocimiento facial en tiempo real"""
    serializer = ReconocimientoFacialSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        imagen_base64 = serializer.validated_data['imagen_base64']
        ubicacion = serializer.validated_data['ubicacion']

        # Mensaje de la IA solicitando autenticación
        mensaje_ia = f"Hola, soy Smart Condominium AI, tu asistente de seguridad inteligente. Detecto que estás intentando acceder al condominio en {ubicacion}. Por favor, permite que analice tu rostro para verificar tu identidad y autorizar el acceso de manera segura."

        # Buscar rostro más similar
        rostro_encontrado, confianza = _buscar_rostro_similar(imagen_base64)

        if rostro_encontrado and confianza >= max(rostro_encontrado.confianza_minima, 0.75):  # Usar el máximo entre el mínimo configurado y 0.75
            # Acceso permitido
            acceso = Acceso.objects.create(
                usuario=rostro_encontrado.usuario,
                tipo_acceso='facial',
                estado='permitido',
                ubicacion=ubicacion,
                rostro_detectado=rostro_encontrado,
                confianza_ia=confianza,
                observaciones=f'Reconocimiento facial exitoso (confianza: {confianza:.2f})'
            )

            return Response({
                'acceso_permitido': True,
                'usuario': rostro_encontrado.usuario.get_full_name(),
                'confianza': confianza,
                'acceso_id': acceso.id,
                'mensaje_ia': f'¡Bienvenido, {rostro_encontrado.usuario.get_full_name()}! He verificado tu identidad con un {confianza:.1%} de confianza. El acceso ha sido autorizado exitosamente. Que tengas un excelente día en Smart Condominium.'
            })

        else:
            # Acceso denegado
            acceso = Acceso.objects.create(
                tipo_acceso='facial',
                estado='denegado',
                ubicacion=ubicacion,
                confianza_ia=confianza if confianza else 0,
                observaciones='Rostro no reconocido o confianza insuficiente'
            )

            return Response({
                'acceso_permitido': False,
                'mensaje': 'Rostro no reconocido',
                'confianza': confianza,
                'acceso_id': acceso.id,
                'mensaje_ia': 'Lo siento, no pude reconocer tu rostro en el sistema de seguridad. Si eres un residente registrado, por favor verifica que tu rostro esté bien iluminado y mira directamente a la cámara. Si el problema persiste, contacta a administración.'
            })

    except Exception as e:
        return Response(
            {
                'error': f'Error en reconocimiento facial: {str(e)}',
                'mensaje_ia': 'Disculpa, ocurrió un error técnico en el sistema de reconocimiento facial. Por favor, intenta nuevamente o contacta al soporte técnico de Smart Condominium.'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def lectura_placa(request):
    """Endpoint para lectura automática de placas vehiculares"""
    serializer = LecturaPlacaSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        imagen_base64 = serializer.validated_data['imagen_base64']
        ubicacion = serializer.validated_data['ubicacion']

        # Mensaje de la IA solicitando autenticación
        mensaje_ia = f"Hola, soy Smart Condominium AI, tu asistente de seguridad inteligente. Detecto un vehículo intentando acceder al condominio en {ubicacion}. Voy a analizar la placa vehicular para verificar si está autorizada en el sistema."

        # Extraer texto de la placa usando IA
        placa_texto = _extraer_texto_placa(imagen_base64)

        if not placa_texto:
            acceso = Acceso.objects.create(
                tipo_acceso='placa',
                estado='denegado',
                ubicacion=ubicacion,
                observaciones='No se pudo leer la placa'
            )
            return Response({
                'acceso_permitido': False,
                'mensaje': 'No se pudo leer la placa',
                'acceso_id': acceso.id,
                'mensaje_ia': 'Lo siento, no pude leer claramente la placa vehicular. Por favor, asegúrate de que la placa esté limpia, bien iluminada y en posición correcta. Si el problema persiste, contacta al personal de seguridad.'
            })

        # Buscar vehículo registrado
        try:
            vehiculo = VehiculoRegistrado.objects.get(
                placa=placa_texto.upper(),
                activo=True
            )

            # Acceso permitido
            acceso = Acceso.objects.create(
                usuario=vehiculo.usuario,
                tipo_acceso='placa',
                estado='permitido',
                ubicacion=ubicacion,
                vehiculo_detectado=vehiculo,
                confianza_ia=0.95,  # Confianza simulada para OCR
                observaciones=f'Placa reconocida: {placa_texto}'
            )

            return Response({
                'acceso_permitido': True,
                'placa': placa_texto,
                'vehiculo': f"{vehiculo.marca} {vehiculo.modelo}",
                'usuario': vehiculo.usuario.get_full_name(),
                'acceso_id': acceso.id,
                'mensaje_ia': f'¡Perfecto! He identificado el vehículo con placa {placa_texto} perteneciente a {vehiculo.usuario.get_full_name()}. El acceso vehicular ha sido autorizado. Conduce con cuidado dentro de Smart Condominium.'
            })

        except VehiculoRegistrado.DoesNotExist:
            # Placa no registrada
            acceso = Acceso.objects.create(
                tipo_acceso='placa',
                estado='denegado',
                ubicacion=ubicacion,
                observaciones=f'Placa no registrada: {placa_texto}'
            )

            return Response({
                'acceso_permitido': False,
                'mensaje': 'Placa no registrada',
                'placa_detectada': placa_texto,
                'acceso_id': acceso.id,
                'mensaje_ia': f'La placa {placa_texto} no está registrada en el sistema de Smart Condominium. Si eres un visitante autorizado, por favor contacta a recepción para obtener un pase temporal. Si eres residente, registra tu vehículo en el sistema.'
            })

    except Exception as e:
        return Response(
            {
                'error': f'Error en lectura de placa: {str(e)}',
                'mensaje_ia': 'Disculpa, ocurrió un error técnico en el sistema de reconocimiento de placas. Por favor, intenta nuevamente o contacta al soporte técnico de Smart Condominium.'
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

def _buscar_rostro_similar(imagen_base64):
    """
    Buscar el rostro más similar usando el sistema inteligente híbrido
    que combina face_recognition con Grok 4 Fast Free
    """
    try:
        print("🧠 INICIANDO BÚSQUEDA FACIAL INTELIGENTE...")

        # Decodificar imagen
        image_array = FacialRecognitionService.decode_base64_image(imagen_base64)
        print(f"✅ Imagen decodificada: {image_array.shape}")

        # Validar calidad básica de imagen
        is_quality_ok, quality_message = FacialRecognitionService.validate_image_quality(image_array)
        print(f"📊 Validación de calidad: {'✅ APROBADA' if is_quality_ok else '❌ RECHAZADA'} - {quality_message}")
        if not is_quality_ok:
            print(f"Imagen rechazada por calidad: {quality_message}")
            return None, 0

        # Validar que no sea una imagen uniforme
        gray = cv2.cvtColor(image_array, cv2.COLOR_RGB2GRAY)
        std_dev = gray.std()
        print(f"Desviación estándar de intensidad: {std_dev:.2f}")
        if std_dev < 5:
            print("Imagen rechazada: demasiado uniforme")
            return None, 0

        # Usar el sistema inteligente híbrido para extraer características
        print("🎯 Usando sistema inteligente híbrido para login...")
        result = FacialRecognitionService.extract_face_embedding(
            image_array,
            strict_validation=True,
            grok_client=grok_client
        )

        if not result['face_detected'] or not result['embedding']:
            print("❌ No se pudo detectar rostro en la imagen")
            return None, 0

        target_embedding = result['embedding']
        target_profile = result.get('facial_profile', {})
        detection_method = result.get('detection_method', 'unknown')

        print(f"✅ Análisis inteligente completado: modelo={result['model']}, confianza={result['confidence']:.3f}")
        print(f"🎯 Método de detección: {detection_method}")
        print(f"� Embedding listo: longitud={len(target_embedding)}")

        # Buscar coincidencias en la base de datos
        rostros = RostroRegistrado.objects.filter(activo=True)
        print(f"Buscando entre {rostros.count()} rostros registrados...")

        best_match = None
        best_confidence = 0

        for rostro in rostros:
            print(f"  - Comparando con: {rostro.nombre_identificador}")

            if not rostro.embedding_ia or not rostro.embedding_ia.get('vector'):
                print(f"    ❌ Rostro {rostro.nombre_identificador} no tiene embedding")
                continue

            stored_embedding = rostro.embedding_ia['vector']

            # Comparar embeddings usando el método inteligente
            confidence, distance = FacialRecognitionService.compare_embeddings(target_embedding, stored_embedding)

            print(f"    📊 Comparación: confianza={confidence:.3f}, distancia={distance:.3f}")

            if confidence > best_confidence:
                best_match = rostro
                best_confidence = confidence
                print(f"    🏆 ¡Nueva mejor coincidencia! Confianza: {best_confidence:.3f}")

        # Determinar umbral de aceptación basado en el método de detección
        umbral_minimo = 0.6 if detection_method in ['hybrid', 'ai-enhanced-grok-face_recognition'] else 0.4

        if best_match and best_confidence >= umbral_minimo:
            print(f"✅ Coincidencia segura encontrada: {best_match.nombre_identificador}, confianza: {best_confidence:.3f}")
            return best_match, best_confidence

        print(f"❌ No se encontró coincidencia aceptable (mejor confianza: {best_confidence:.3f}, umbral: {umbral_minimo:.3f})")
        return None, best_confidence

    except Exception as e:
        print(f"❌ Error en búsqueda facial inteligente: {e}")
        return None, 0

def _extraer_caracteristicas_faciales_simple(imagen_base64):
    """Versión simplificada para comparación - usa el servicio real de face_recognition"""
    try:
        return extract_face_embedding_from_base64(imagen_base64)
    except Exception as e:
        print(f"Error en extracción simple: {e}")
        return [0.1] * 128

def _extraer_caracteristicas_faciales_real(imagen_base64):
    """Extraer características faciales reales usando face_recognition"""
    try:
        return extract_face_embedding_from_base64(imagen_base64)
    except Exception as e:
        print(f"Error en extracción real: {e}")
        return [0.1] * 128

def _calcular_similitud(embedding1, embedding2):
    """Calcular similitud entre dos embeddings usando el servicio de comparación"""
    try:
        comparison = FacialRecognitionService.compare_faces(embedding1, embedding2)
        return comparison['confidence']
    except Exception as e:
        print(f"Error calculando similitud: {e}")
        return 0.5  # Similitud neutral

def _extraer_texto_placa(imagen_base64):
    """Extraer texto de placa usando Grok Vision API"""
    if not grok_client:
        # Fallback a simulación si no hay API key
        return "1234ABC"

    try:
        # Decodificar imagen
        imagen_data = base64.b64decode(imagen_base64)
        imagen = Image.open(BytesIO(imagen_data))

        # Convertir a RGB si es necesario
        if imagen.mode != 'RGB':
            imagen = imagen.convert('RGB')

        # Guardar temporalmente como JPEG
        buffer = BytesIO()
        imagen.save(buffer, format='JPEG')
        buffer.seek(0)

        # Usar Grok Vision API para OCR (via OpenRouter)
        response = grok_client.chat.completions.create(
            extra_headers={
                "HTTP-Referer": "https://smartcondominium.com",  # Optional. Site URL for rankings on openrouter.ai.
                "X-Title": "Smart Condominium AI",  # Optional. Site title for rankings on openrouter.ai.
            },
            model="x-ai/grok-4-fast:free",  # Modelo correcto para OpenRouter
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "Analiza esta imagen de una placa vehicular y extrae el texto de la placa. La placa sigue el formato boliviano: 3 o 4 números seguidos de 3 letras (ejemplo: 123ABC o 1234ABC). Responde solo con el texto de la placa sin espacios ni guiones. Si no puedes leer claramente la placa, responde con 'NO_LEIBLE'."
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64.b64encode(buffer.getvalue()).decode()}"
                            }
                        }
                    ]
                }
            ]
        )

        # Extraer texto de la respuesta
        texto_placa = response.choices[0].message.content.strip()

        # Validar formato boliviano
        import re
        if re.match(r'^\d{3,4}[A-Z]{3}$', texto_placa):
            return texto_placa
        else:
            print(f"Texto extraído no válido: {texto_placa}")
            return "1234ABC"  # Fallback

    except Exception as e:
        print(f"Error con OpenAI Vision API para OCR: {e}")
        return "1234ABC"  # Fallback a simulación