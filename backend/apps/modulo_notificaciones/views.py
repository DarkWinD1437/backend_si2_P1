from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from django.utils import timezone
from .models import Dispositivo, PreferenciasNotificacion, Notificacion
from .serializers import (
    DispositivoSerializer, DispositivoRegistroSerializer,
    PreferenciasNotificacionSerializer, NotificacionSerializer,
    NotificacionCreateSerializer, EnviarNotificacionSerializer
)

User = get_user_model()


class DispositivoViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de dispositivos"""
    serializer_class = DispositivoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Dispositivo.objects.filter(
            usuario=self.request.user,
            activo=True
        )

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

    @action(detail=False, methods=['post'])
    def registrar(self, request):
        """Registrar o actualizar un dispositivo"""
        serializer = DispositivoRegistroSerializer(data=request.data, context={'request': request})
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        dispositivo = serializer.save()
        return Response(
            DispositivoSerializer(dispositivo).data,
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['post'])
    def desactivar(self, request, pk=None):
        """Desactivar un dispositivo"""
        dispositivo = self.get_object()
        dispositivo.activo = False
        dispositivo.save()

        return Response({'mensaje': 'Dispositivo desactivado correctamente'})


class PreferenciasNotificacionViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de preferencias de notificación"""
    serializer_class = PreferenciasNotificacionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PreferenciasNotificacion.objects.filter(usuario=self.request.user)

    def perform_create(self, serializer):
        serializer.save(usuario=self.request.user)

    @action(detail=False, methods=['post'])
    def bulk_update(self, request):
        """Actualizar múltiples preferencias a la vez"""
        preferencias_data = request.data.get('preferencias', [])

        updated = []
        for pref_data in preferencias_data:
            pref, created = PreferenciasNotificacion.objects.get_or_create(
                usuario=request.user,
                tipo_notificacion=pref_data['tipo_notificacion'],
                defaults=pref_data
            )
            if not created:
                for key, value in pref_data.items():
                    if key != 'tipo_notificacion':
                        setattr(pref, key, value)
                pref.save()
            updated.append(pref)

        serializer = self.get_serializer(updated, many=True)
        return Response(serializer.data)


class NotificacionViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet para consultar notificaciones"""
    serializer_class = NotificacionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Notificacion.objects.filter(usuario=self.request.user)

        # Filtros opcionales
        tipo = self.request.query_params.get('tipo')
        estado = self.request.query_params.get('estado')
        leida = self.request.query_params.get('leida')

        if tipo:
            queryset = queryset.filter(tipo=tipo)
        if estado:
            queryset = queryset.filter(estado=estado)
        if leida is not None:
            if leida.lower() == 'true':
                queryset = queryset.filter(fecha_lectura__isnull=False)
            elif leida.lower() == 'false':
                queryset = queryset.filter(fecha_lectura__isnull=True)

        return queryset.order_by('-fecha_creacion')

    @action(detail=True, methods=['post'])
    def marcar_leida(self, request, pk=None):
        """Marcar una notificación como leída"""
        notificacion = self.get_object()
        notificacion.marcar_como_leida()

        serializer = self.get_serializer(notificacion)
        return Response(serializer.data)

    @action(detail=False, methods=['post'])
    def marcar_todas_leidas(self, request):
        """Marcar todas las notificaciones del usuario como leídas"""
        notificaciones = self.get_queryset().filter(fecha_lectura__isnull=True)
        count = notificaciones.update(
            estado='leida',
            fecha_lectura=timezone.now()
        )

        return Response({
            'mensaje': f'{count} notificaciones marcadas como leídas'
        })

    @action(detail=False, methods=['get'])
    def no_leidas(self, request):
        """Obtener solo notificaciones no leídas"""
        queryset = self.get_queryset().filter(fecha_lectura__isnull=True)
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def enviar_notificacion_push(request):
    """Endpoint para enviar notificaciones push"""
    serializer = EnviarNotificacionSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        resultado = serializer.save()
        return Response({
            'mensaje': 'Notificaciones enviadas correctamente',
            'resultado': resultado
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {'error': f'Error al enviar notificaciones: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def crear_notificacion(request):
    """Endpoint para crear una notificación individual"""
    serializer = NotificacionCreateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    try:
        notificacion = serializer.save()
        return Response(
            NotificacionSerializer(notificacion).data,
            status=status.HTTP_201_CREATED
        )

    except Exception as e:
        return Response(
            {'error': f'Error al crear notificación: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
def test_notificaciones(request):
    """
    Endpoint de prueba para testing de notificaciones (solo desarrollo)
    Permite enviar notificaciones de prueba sin autenticación completa
    """
    from .services import NotificacionService
    from django.contrib.auth import get_user_model

    User = get_user_model()
    service = NotificacionService()

    # Crear usuario de prueba si no existe
    user, created = User.objects.get_or_create(
        username='test_user',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Usuario',
            'last_name': 'Prueba'
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()

    # Crear dispositivo de prueba si no existe
    from .models import Dispositivo
    dispositivo, created = Dispositivo.objects.get_or_create(
        usuario=user,
        token_push='test-device-token-12345',
        defaults={
            'tipo_dispositivo': 'web',
            'activo': True
        }
    )

    # Enviar notificación de prueba
    try:
        resultado = service.enviar_notificacion_push(
            titulo=request.data.get('titulo', '🧪 Notificación de Prueba'),
            mensaje=request.data.get('mensaje', 'Esta es una notificación de prueba desde el endpoint de test. ¡Firebase está funcionando! 🎉'),
            usuario_id=user.id,
            tipo=request.data.get('tipo', 'prueba'),
            prioridad=request.data.get('prioridad', 'normal')
        )

        return Response({
            'mensaje': 'Notificación de prueba enviada',
            'usuario_creado': created,
            'dispositivo_creado': created,
            'resultado': resultado,
            'test_data': {
                'usuario_id': user.id,
                'dispositivo_id': dispositivo.id,
                'titulo': request.data.get('titulo', 'Notificación de Prueba'),
                'mensaje': request.data.get('mensaje', 'Mensaje de prueba'),
            }
        }, status=status.HTTP_200_OK)

    except Exception as e:
        return Response(
            {'error': f'Error en prueba de notificaciones: {str(e)}'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )