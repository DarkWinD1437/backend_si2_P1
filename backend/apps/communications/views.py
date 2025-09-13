from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from django.db.models import Q, Count, Avg
from django.contrib.auth import get_user_model

from .models import Aviso, LecturaAviso, ComentarioAviso
from .serializers import (
    AvisoListSerializer,
    AvisoDetailSerializer, 
    AvisoCreateUpdateSerializer,
    ComentarioAvisoSerializer,
    ComentarioAvisoCreateSerializer,
    LecturaAvisoSerializer,
    EstadisticasAvisoSerializer
)

User = get_user_model()

class AvisoPagination(PageNumberPagination):
    """Paginación personalizada para avisos"""
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50

class AvisoViewSet(viewsets.ModelViewSet):
    """
    ViewSet completo para gestión de avisos del condominio
    
    - GET /api/communications/avisos/ - Listar avisos
    - POST /api/communications/avisos/ - Crear aviso (solo admins)
    - GET /api/communications/avisos/{id}/ - Detalle de aviso
    - PUT/PATCH /api/communications/avisos/{id}/ - Actualizar aviso
    - DELETE /api/communications/avisos/{id}/ - Eliminar aviso
    """
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = AvisoPagination
    
    def get_queryset(self):
        """
        Filtrar avisos según el rol del usuario
        Los usuarios solo ven avisos dirigidos a ellos
        """
        user = self.request.user
        
        # Los administradores ven todos los avisos
        if user.role == 'admin':
            queryset = Aviso.objects.all()
        else:
            # Otros usuarios ven solo avisos dirigidos a su rol
            queryset = Aviso.objects.filter(
                Q(tipo_destinatario='todos') |
                Q(tipo_destinatario='residentes', ) |
                Q(tipo_destinatario='seguridad', ) |
                Q(tipo_destinatario='admin_seguridad', ) |
                Q(tipo_destinatario='residentes_seguridad', ) |
                Q(tipo_destinatario='personalizado', roles_destinatarios__contains=user.role) |
                Q(usuarios_destinatarios=user)
            )
            
            # Filtrar según rol específico
            if user.role == 'resident':
                queryset = queryset.filter(
                    Q(tipo_destinatario__in=['todos', 'residentes', 'residentes_seguridad']) |
                    Q(tipo_destinatario='personalizado', roles_destinatarios__contains='resident') |
                    Q(usuarios_destinatarios=user)
                )
            elif user.role == 'security':
                queryset = queryset.filter(
                    Q(tipo_destinatario__in=['todos', 'seguridad', 'admin_seguridad', 'residentes_seguridad']) |
                    Q(tipo_destinatario='personalizado', roles_destinatarios__contains='security') |
                    Q(usuarios_destinatarios=user)
                )
        
        # Solo mostrar avisos publicados por defecto
        mostrar_todos = self.request.query_params.get('mostrar_todos', 'false').lower()
        if mostrar_todos != 'true' or user.role != 'admin':
            queryset = queryset.filter(estado='publicado', fecha_publicacion__lte=timezone.now())
        
        # Aplicar filtros adicionales
        prioridad = self.request.query_params.get('prioridad')
        if prioridad:
            queryset = queryset.filter(prioridad=prioridad)
            
        tipo_destinatario = self.request.query_params.get('tipo_destinatario')
        if tipo_destinatario:
            queryset = queryset.filter(tipo_destinatario=tipo_destinatario)
            
        autor_id = self.request.query_params.get('autor')
        if autor_id:
            queryset = queryset.filter(autor_id=autor_id)
        
        # Filtro de búsqueda por título o contenido
        busqueda = self.request.query_params.get('busqueda')
        if busqueda:
            queryset = queryset.filter(
                Q(titulo__icontains=busqueda) | 
                Q(contenido__icontains=busqueda)
            )
        
        return queryset.select_related('autor').prefetch_related('lecturas', 'comentarios')
    
    def get_serializer_class(self):
        if self.action == 'list':
            return AvisoListSerializer
        elif self.action in ['create', 'update', 'partial_update']:
            return AvisoCreateUpdateSerializer
        return AvisoDetailSerializer
    
    def perform_create(self, serializer):
        """Solo administradores pueden crear avisos"""
        if self.request.user.role != 'admin':
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Solo los administradores pueden crear avisos.")
        
        aviso = serializer.save(autor=self.request.user)
        
        # Auto-publicar si no es borrador
        if aviso.estado == 'borrador':
            aviso.publicar()
    
    def perform_update(self, serializer):
        """Solo el autor o administradores pueden actualizar"""
        aviso = self.get_object()
        user = self.request.user
        
        if aviso.autor != user and user.role != 'admin':
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("No tiene permisos para editar este aviso.")
        
        serializer.save()
    
    def perform_destroy(self, instance):
        """Solo el autor o administradores pueden eliminar"""
        user = self.request.user
        
        if instance.autor != user and user.role != 'admin':
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("No tiene permisos para eliminar este aviso.")
        
        instance.delete()
    
    def retrieve(self, request, *args, **kwargs):
        """Al ver detalle, incrementar visualizaciones y marcar como leído"""
        instance = self.get_object()
        
        # Incrementar visualizaciones
        instance.incrementar_visualizaciones()
        
        # Crear o actualizar lectura del usuario
        LecturaAviso.objects.get_or_create(
            aviso=instance,
            usuario=request.user,
            defaults={'confirmado': False}
        )
        
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def marcar_leido(self, request, pk=None):
        """Marcar aviso como leído y confirmado"""
        aviso = self.get_object()
        
        lectura, created = LecturaAviso.objects.get_or_create(
            aviso=aviso,
            usuario=request.user,
            defaults={'confirmado': True}
        )
        
        if not created:
            lectura.confirmado = True
            lectura.save()
        
        return Response({
            'success': True,
            'message': 'Aviso marcado como leído',
            'lectura': LecturaAvisoSerializer(lectura).data
        })

    @action(detail=True, methods=['post'])
    def publicar(self, request, pk=None):
        """Publicar aviso (solo autor o admin)"""
        aviso = self.get_object()
        user = request.user
        
        if aviso.autor != user and user.role != 'admin':
            return Response({
                'error': 'No tiene permisos para publicar este aviso'
            }, status=status.HTTP_403_FORBIDDEN)
        
        if aviso.estado == 'publicado':
            return Response({
                'error': 'El aviso ya está publicado'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        aviso.publicar()
        
        return Response({
            'success': True,
            'message': 'Aviso publicado exitosamente',
            'aviso': AvisoDetailSerializer(aviso, context={'request': request}).data
        })

    @action(detail=True, methods=['post'])
    def archivar(self, request, pk=None):
        """Archivar aviso (solo autor o admin)"""
        aviso = self.get_object()
        user = request.user
        
        if aviso.autor != user and user.role != 'admin':
            return Response({
                'error': 'No tiene permisos para archivar este aviso'
            }, status=status.HTTP_403_FORBIDDEN)
        
        aviso.archivar()
        
        return Response({
            'success': True,
            'message': 'Aviso archivado exitosamente',
            'aviso': AvisoDetailSerializer(aviso, context={'request': request}).data
        })

    @action(detail=True, methods=['get', 'post'])
    def comentarios(self, request, pk=None):
        """Gestionar comentarios de avisos"""
        aviso = self.get_object()
        
        if request.method == 'GET':
            comentarios = aviso.comentarios.filter(es_respuesta__isnull=True)
            serializer = ComentarioAvisoSerializer(
                comentarios, 
                many=True, 
                context={'request': request}
            )
            return Response(serializer.data)
        
        elif request.method == 'POST':
            serializer = ComentarioAvisoCreateSerializer(data=request.data)
            if serializer.is_valid():
                comentario = serializer.save(
                    aviso=aviso,
                    autor=request.user
                )
                return Response({
                    'success': True,
                    'message': 'Comentario agregado exitosamente',
                    'comentario': ComentarioAvisoSerializer(
                        comentario, 
                        context={'request': request}
                    ).data
                }, status=status.HTTP_201_CREATED)
            
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def lecturas(self, request, pk=None):
        """Ver quién ha leído el aviso (solo autor o admin)"""
        aviso = self.get_object()
        user = request.user
        
        if aviso.autor != user and user.role != 'admin':
            return Response({
                'error': 'No tiene permisos para ver las lecturas'
            }, status=status.HTTP_403_FORBIDDEN)
        
        lecturas = aviso.lecturas.all()
        destinatarios_total = aviso.get_destinatarios_queryset().count()
        
        return Response({
            'lecturas': LecturaAvisoSerializer(lecturas, many=True).data,
            'estadisticas': {
                'total_destinatarios': destinatarios_total,
                'total_lecturas': lecturas.count(),
                'lecturas_confirmadas': lecturas.filter(confirmado=True).count(),
                'porcentaje_lectura': (lecturas.count() / destinatarios_total * 100) if destinatarios_total > 0 else 0
            }
        })

    @action(detail=False, methods=['get'])
    def estadisticas(self, request):
        """Estadísticas generales de avisos (solo admin)"""
        if request.user.role != 'admin':
            return Response({
                'error': 'No tiene permisos para ver estadísticas'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Estadísticas básicas
        stats = {
            'total_avisos': Aviso.objects.count(),
            'avisos_activos': Aviso.objects.filter(estado='publicado').exclude(fecha_vencimiento__lte=timezone.now()).count(),
            'avisos_vencidos': Aviso.objects.filter(fecha_vencimiento__lte=timezone.now()).count(),
            'total_lecturas': LecturaAviso.objects.count(),
            'total_comentarios': ComentarioAviso.objects.count(),
        }
        
        # Estadísticas por prioridad
        prioridades = Aviso.objects.values('prioridad').annotate(count=Count('id'))
        stats['avisos_por_prioridad'] = {item['prioridad']: item['count'] for item in prioridades}
        
        # Estadísticas por tipo de destinatario
        tipos = Aviso.objects.values('tipo_destinatario').annotate(count=Count('id'))
        stats['avisos_por_tipo_destinatario'] = {item['tipo_destinatario']: item['count'] for item in tipos}
        
        # Promedio de visualizaciones
        promedio_viz = Aviso.objects.aggregate(promedio=Avg('visualizaciones'))
        stats['promedio_visualizaciones'] = round(promedio_viz['promedio'] or 0, 2)
        
        return Response(stats)

    @action(detail=False, methods=['get'])
    def mis_avisos(self, request):
        """Avisos creados por el usuario actual"""
        avisos = Aviso.objects.filter(autor=request.user)
        
        # Aplicar filtros
        estado = request.query_params.get('estado')
        if estado:
            avisos = avisos.filter(estado=estado)
        
        page = self.paginate_queryset(avisos)
        if page is not None:
            serializer = AvisoListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = AvisoListSerializer(avisos, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def no_leidos(self, request):
        """Avisos no leídos por el usuario actual"""
        avisos_leidos = LecturaAviso.objects.filter(usuario=request.user).values_list('aviso_id', flat=True)
        
        avisos_no_leidos = self.get_queryset().exclude(id__in=avisos_leidos)
        
        page = self.paginate_queryset(avisos_no_leidos)
        if page is not None:
            serializer = AvisoListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = AvisoListSerializer(avisos_no_leidos, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def dashboard(self, request):
        """
        Dashboard de avisos para el usuario actual
        Incluye contadores, avisos importantes y resumen
        """
        user = request.user
        queryset_base = self.get_queryset()
        
        # Avisos leídos por el usuario
        avisos_leidos = LecturaAviso.objects.filter(usuario=user).values_list('aviso_id', flat=True)
        
        # Contadores principales
        stats = {
            'total_avisos': queryset_base.count(),
            'avisos_no_leidos': queryset_base.exclude(id__in=avisos_leidos).count(),
            'avisos_urgentes': queryset_base.filter(prioridad='urgente').count(),
            'avisos_alta_prioridad': queryset_base.filter(prioridad='alta').count(),
            'avisos_fijados': queryset_base.filter(es_fijado=True).count(),
        }
        
        # Contadores por prioridad
        stats['por_prioridad'] = {}
        for prioridad, _ in Aviso.PRIORIDAD_CHOICES:
            count = queryset_base.filter(prioridad=prioridad).count()
            count_no_leidos = queryset_base.filter(prioridad=prioridad).exclude(id__in=avisos_leidos).count()
            stats['por_prioridad'][prioridad] = {
                'total': count,
                'no_leidos': count_no_leidos
            }
        
        # Avisos más recientes (últimos 5)
        avisos_recientes = queryset_base[:5]
        
        # Avisos urgentes no leídos
        avisos_urgentes_no_leidos = queryset_base.filter(
            prioridad__in=['urgente', 'alta']
        ).exclude(id__in=avisos_leidos)[:3]
        
        # Avisos fijados
        avisos_fijados = queryset_base.filter(es_fijado=True)[:3]
        
        return Response({
            'estadisticas': stats,
            'avisos_recientes': AvisoListSerializer(avisos_recientes, many=True, context={'request': request}).data,
            'avisos_urgentes_no_leidos': AvisoListSerializer(avisos_urgentes_no_leidos, many=True, context={'request': request}).data,
            'avisos_fijados': AvisoListSerializer(avisos_fijados, many=True, context={'request': request}).data,
            'usuario_info': {
                'role': user.role,
                'username': user.username,
                'puede_crear_avisos': user.role == 'admin'
            }
        })

    @action(detail=False, methods=['get'])
    def filtros_avanzados(self, request):
        """
        Endpoint para filtros avanzados de avisos
        Soporta múltiples filtros combinados
        """
        queryset = self.get_queryset()
        
        # Filtro por rango de fechas
        fecha_desde = request.query_params.get('fecha_desde')
        fecha_hasta = request.query_params.get('fecha_hasta')
        
        if fecha_desde:
            try:
                fecha_desde_parsed = timezone.datetime.strptime(fecha_desde, '%Y-%m-%d').date()
                queryset = queryset.filter(fecha_publicacion__date__gte=fecha_desde_parsed)
            except ValueError:
                pass
                
        if fecha_hasta:
            try:
                fecha_hasta_parsed = timezone.datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
                queryset = queryset.filter(fecha_publicacion__date__lte=fecha_hasta_parsed)
            except ValueError:
                pass
        
        # Filtro por palabras clave en título y contenido
        palabras_clave = request.query_params.get('palabras_clave')
        if palabras_clave:
            palabras = palabras_clave.split(',')
            query = Q()
            for palabra in palabras:
                palabra = palabra.strip()
                if palabra:
                    query |= Q(titulo__icontains=palabra) | Q(contenido__icontains=palabra)
            queryset = queryset.filter(query)
        
        # Filtro por múltiples prioridades
        prioridades = request.query_params.get('prioridades')
        if prioridades:
            prioridades_list = [p.strip() for p in prioridades.split(',')]
            queryset = queryset.filter(prioridad__in=prioridades_list)
        
        # Filtro por estado de lectura
        estado_lectura = request.query_params.get('estado_lectura')  # 'leidos', 'no_leidos', 'todos'
        if estado_lectura in ['leidos', 'no_leidos']:
            avisos_leidos = LecturaAviso.objects.filter(usuario=request.user).values_list('aviso_id', flat=True)
            if estado_lectura == 'leidos':
                queryset = queryset.filter(id__in=avisos_leidos)
            else:  # no_leidos
                queryset = queryset.exclude(id__in=avisos_leidos)
        
        # Filtro por avisos que requieren confirmación
        requiere_confirmacion = request.query_params.get('requiere_confirmacion')
        if requiere_confirmacion and requiere_confirmacion.lower() in ['true', '1']:
            queryset = queryset.filter(requiere_confirmacion=True)
        
        # Filtro por avisos fijados
        solo_fijados = request.query_params.get('solo_fijados')
        if solo_fijados and solo_fijados.lower() in ['true', '1']:
            queryset = queryset.filter(es_fijado=True)
        
        # Ordenamiento personalizado
        orden = request.query_params.get('orden', 'fecha_desc')  # fecha_desc, fecha_asc, prioridad, visualizaciones
        
        if orden == 'fecha_asc':
            queryset = queryset.order_by('fecha_publicacion')
        elif orden == 'prioridad':
            # Ordenar por prioridad: urgente, alta, media, baja
            prioridad_orden = {
                'urgente': 1,
                'alta': 2, 
                'media': 3,
                'baja': 4
            }
            queryset = sorted(queryset, key=lambda x: prioridad_orden.get(x.prioridad, 5))
        elif orden == 'visualizaciones':
            queryset = queryset.order_by('-visualizaciones')
        else:  # fecha_desc (por defecto)
            queryset = queryset.order_by('-es_fijado', '-fecha_publicacion')
        
        # Paginación
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = AvisoListSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = AvisoListSerializer(queryset, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def busqueda_inteligente(self, request):
        """
        Búsqueda inteligente de avisos
        Combina filtros de texto, fecha y prioridad de forma intuitiva
        """
        query = request.query_params.get('q', '').strip()
        
        if not query:
            return Response({
                'results': [],
                'message': 'Ingrese un término de búsqueda'
            })
        
        queryset = self.get_queryset()
        
        # Búsqueda en múltiples campos
        search_query = (
            Q(titulo__icontains=query) |
            Q(contenido__icontains=query) |
            Q(resumen__icontains=query) |
            Q(autor__username__icontains=query) |
            Q(autor__first_name__icontains=query) |
            Q(autor__last_name__icontains=query)
        )
        
        resultados = queryset.filter(search_query)
        
        # Separar por relevancia
        resultados_titulo = resultados.filter(titulo__icontains=query)
        resultados_contenido = resultados.filter(contenido__icontains=query).exclude(titulo__icontains=query)
        resultados_otros = resultados.exclude(
            Q(titulo__icontains=query) | Q(contenido__icontains=query)
        )
        
        # Ordenar por relevancia
        resultados_ordenados = list(resultados_titulo) + list(resultados_contenido) + list(resultados_otros)
        
        page = self.paginate_queryset(resultados_ordenados)
        if page is not None:
            serializer = AvisoListSerializer(page, many=True, context={'request': request})
            response_data = self.get_paginated_response(serializer.data).data
            response_data.update({
                'total_encontrados': len(resultados_ordenados),
                'query': query
            })
            return Response(response_data)
        
        serializer = AvisoListSerializer(resultados_ordenados, many=True, context={'request': request})
        return Response({
            'results': serializer.data,
            'total_encontrados': len(resultados_ordenados),
            'query': query
        })

    @action(detail=False, methods=['get'])
    def resumen_usuario(self, request):
        """
        Resumen personalizado para el usuario actual
        Incluye métricas de participación y avisos relevantes
        """
        user = request.user
        queryset = self.get_queryset()
        
        # Lecturas del usuario
        mis_lecturas = LecturaAviso.objects.filter(usuario=user)
        avisos_leidos_ids = mis_lecturas.values_list('aviso_id', flat=True)
        
        # Comentarios del usuario
        mis_comentarios = ComentarioAviso.objects.filter(autor=user)
        
        # Estadísticas personales
        resumen = {
            'avisos_disponibles': queryset.count(),
            'avisos_leidos': mis_lecturas.count(),
            'avisos_no_leidos': queryset.exclude(id__in=avisos_leidos_ids).count(),
            'comentarios_realizados': mis_comentarios.count(),
            'avisos_comentados': mis_comentarios.values('aviso').distinct().count(),
            'porcentaje_lectura': 0
        }
        
        if resumen['avisos_disponibles'] > 0:
            resumen['porcentaje_lectura'] = round(
                (resumen['avisos_leidos'] / resumen['avisos_disponibles']) * 100, 2
            )
        
        # Avisos pendientes de alta prioridad
        avisos_importantes_pendientes = queryset.filter(
            prioridad__in=['urgente', 'alta']
        ).exclude(id__in=avisos_leidos_ids)
        
        # Avisos que requieren confirmación pendientes
        avisos_confirmacion_pendientes = queryset.filter(
            requiere_confirmacion=True
        ).exclude(
            lecturas__usuario=user,
            lecturas__confirmado=True
        )
        
        # Últimos avisos interactuados
        ultimas_lecturas = mis_lecturas.select_related('aviso')[:5]
        
        return Response({
            'resumen': resumen,
            'avisos_importantes_pendientes': AvisoListSerializer(
                avisos_importantes_pendientes, many=True, context={'request': request}
            ).data,
            'avisos_confirmacion_pendientes': AvisoListSerializer(
                avisos_confirmacion_pendientes, many=True, context={'request': request}
            ).data,
            'ultimas_lecturas': [
                {
                    'aviso': AvisoListSerializer(lectura.aviso, context={'request': request}).data,
                    'fecha_lectura': lectura.fecha_lectura,
                    'confirmado': lectura.confirmado
                }
                for lectura in ultimas_lecturas
            ]
        })