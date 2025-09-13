"""
Vistas API para el Módulo de Gestión Financiera
Módulo 2: Gestión Financiera Básica - T1: Configurar Cuotas y Multas

Permisos:
- Administradores: CRUD completo de conceptos y cargos
- Residentes: Solo lectura de sus propios cargos y pagar
- Seguridad: Solo lectura de conceptos y cargos
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model
from django.db.models import Q, Sum, Count
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal

from .models import ConceptoFinanciero, CargoFinanciero, EstadoCargo, EstadoConcepto
from .serializers import (
    ConceptoFinancieroSerializer,
    ConceptoFinancieroListSerializer,
    CargoFinancieroSerializer,
    CargoFinancieroListSerializer,
    PagarCargoSerializer,
    ResumenFinancieroSerializer,
    EstadisticasFinancierasSerializer,
    ResidenteBasicoSerializer
)

User = get_user_model()


class IsAdminOrReadOnlyForResidents(permissions.BasePermission):
    """
    Permiso personalizado:
    - Administradores: acceso completo
    - Residentes y Seguridad: solo lectura
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Administradores tienen acceso completo
        if hasattr(request.user, 'role') and request.user.role == 'admin':
            return True
        
        # Superusers tienen acceso completo
        if request.user.is_superuser:
            return True
        
        # Para otros usuarios, solo métodos de lectura
        return request.method in permissions.SAFE_METHODS

    def has_object_permission(self, request, view, obj):
        return self.has_permission(request, view)


class ConceptoFinancieroViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar conceptos financieros (cuotas y multas)
    
    Endpoints:
    - GET /api/finances/conceptos/ - Listar conceptos
    - POST /api/finances/conceptos/ - Crear concepto (solo admins)
    - GET /api/finances/conceptos/{id}/ - Detalle de concepto
    - PUT/PATCH /api/finances/conceptos/{id}/ - Actualizar concepto (solo admins)
    - DELETE /api/finances/conceptos/{id}/ - Eliminar concepto (solo admins)
    - GET /api/finances/conceptos/vigentes/ - Solo conceptos vigentes
    - POST /api/finances/conceptos/{id}/toggle_estado/ - Activar/desactivar
    """
    
    queryset = ConceptoFinanciero.objects.all()
    permission_classes = [IsAdminOrReadOnlyForResidents]
    
    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'vigentes':
            return ConceptoFinancieroListSerializer
        return ConceptoFinancieroSerializer

    def get_queryset(self):
        queryset = ConceptoFinanciero.objects.all()
        
        # Filtros opcionales
        tipo = self.request.query_params.get('tipo', None)
        estado = self.request.query_params.get('estado', None)
        vigente = self.request.query_params.get('vigente', None)
        
        if tipo:
            queryset = queryset.filter(tipo=tipo)
        
        if estado:
            queryset = queryset.filter(estado=estado)
        
        if vigente == 'true':
            hoy = date.today()
            queryset = queryset.filter(
                estado=EstadoConcepto.ACTIVO,
                fecha_vigencia_desde__lte=hoy
            ).filter(
                Q(fecha_vigencia_hasta__isnull=True) | Q(fecha_vigencia_hasta__gte=hoy)
            )
        
        return queryset.order_by('tipo', 'nombre')

    @action(detail=False, methods=['get'])
    def vigentes(self, request):
        """Obtener solo conceptos vigentes"""
        hoy = date.today()
        conceptos = ConceptoFinanciero.objects.filter(
            estado=EstadoConcepto.ACTIVO,
            fecha_vigencia_desde__lte=hoy
        ).filter(
            Q(fecha_vigencia_hasta__isnull=True) | Q(fecha_vigencia_hasta__gte=hoy)
        ).order_by('tipo', 'nombre')
        
        serializer = ConceptoFinancieroListSerializer(conceptos, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def toggle_estado(self, request, pk=None):
        """Activar/desactivar un concepto"""
        if not (hasattr(request.user, 'role') and request.user.role == 'admin') and not request.user.is_superuser:
            return Response(
                {'error': 'No tiene permisos para realizar esta acción'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        concepto = get_object_or_404(ConceptoFinanciero, pk=pk)
        nuevo_estado = EstadoConcepto.ACTIVO if concepto.estado != EstadoConcepto.ACTIVO else EstadoConcepto.INACTIVO
        concepto.estado = nuevo_estado
        concepto.save()
        
        serializer = ConceptoFinancieroSerializer(concepto)
        return Response({
            'mensaje': f'Concepto {concepto.nombre} ahora está {concepto.get_estado_display()}',
            'concepto': serializer.data
        })


class CargoFinancieroViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar cargos financieros aplicados a residentes
    
    Endpoints:
    - GET /api/finances/cargos/ - Listar cargos (filtrados por permisos)
    - POST /api/finances/cargos/ - Crear cargo (solo admins)
    - GET /api/finances/cargos/{id}/ - Detalle de cargo
    - PUT/PATCH /api/finances/cargos/{id}/ - Actualizar cargo (solo admins)
    - DELETE /api/finances/cargos/{id}/ - Eliminar cargo (solo admins)
    - GET /api/finances/cargos/mis_cargos/ - Cargos del usuario actual
    - POST /api/finances/cargos/{id}/pagar/ - Marcar cargo como pagado
    - GET /api/finances/cargos/vencidos/ - Cargos vencidos (solo admins)
    - GET /api/finances/cargos/resumen/{user_id}/ - Resumen financiero de un residente
    """
    
    queryset = CargoFinanciero.objects.all()
    permission_classes = [permissions.IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'mis_cargos' or self.action == 'vencidos':
            return CargoFinancieroListSerializer
        elif self.action == 'pagar':
            return PagarCargoSerializer
        return CargoFinancieroSerializer

    def get_queryset(self):
        user = self.request.user
        queryset = CargoFinanciero.objects.select_related('concepto', 'residente', 'aplicado_por')
        
        # Filtrar por permisos
        if hasattr(user, 'role') and user.role == 'admin' or user.is_superuser:
            # Administradores ven todos los cargos
            pass
        else:
            # Residentes y seguridad solo ven cargos del residente actual
            queryset = queryset.filter(residente=user)
        
        # Filtros opcionales
        estado = self.request.query_params.get('estado', None)
        residente_id = self.request.query_params.get('residente', None)
        concepto_id = self.request.query_params.get('concepto', None)
        vencidos = self.request.query_params.get('vencidos', None)
        
        if estado:
            queryset = queryset.filter(estado=estado)
        
        if residente_id and (user.role == 'admin' or user.is_superuser):
            queryset = queryset.filter(residente_id=residente_id)
        
        if concepto_id:
            queryset = queryset.filter(concepto_id=concepto_id)
        
        if vencidos == 'true':
            queryset = queryset.filter(
                estado=EstadoCargo.PENDIENTE,
                fecha_vencimiento__lt=date.today()
            )
        
        return queryset.order_by('-fecha_aplicacion')

    def perform_create(self, serializer):
        """Solo administradores pueden crear cargos"""
        user = self.request.user
        if not (hasattr(user, 'role') and user.role == 'admin') and not user.is_superuser:
            raise permissions.PermissionDenied("No tiene permisos para crear cargos")
        serializer.save(aplicado_por=user)

    def perform_update(self, serializer):
        """Solo administradores pueden actualizar cargos"""
        user = self.request.user
        if not (hasattr(user, 'role') and user.role == 'admin') and not user.is_superuser:
            raise permissions.PermissionDenied("No tiene permisos para actualizar cargos")
        serializer.save()

    def perform_destroy(self, instance):
        """Solo administradores pueden eliminar cargos"""
        user = self.request.user
        if not (hasattr(user, 'role') and user.role == 'admin') and not user.is_superuser:
            raise permissions.PermissionDenied("No tiene permisos para eliminar cargos")
        super().perform_destroy(instance)

    @action(detail=False, methods=['get'])
    def mis_cargos(self, request):
        """Obtener cargos del usuario actual"""
        cargos = CargoFinanciero.objects.filter(
            residente=request.user
        ).select_related('concepto').order_by('-fecha_aplicacion')
        
        serializer = CargoFinancieroListSerializer(cargos, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def pagar(self, request, pk=None):
        """
        Pagar cuota en línea
        T3: Pagar cuota en línea - Módulo 2 Gestión Financiera Básica
        
        Permite que residentes paguen sus cargos en línea y que administradores
        procesen pagos presenciales en nombre de residentes.
        """
        cargo = get_object_or_404(CargoFinanciero, pk=pk)
        
        # Verificar permisos: admin o el propio residente
        if not ((hasattr(request.user, 'role') and request.user.role == 'admin') or 
                request.user.is_superuser or 
                cargo.residente == request.user):
            return Response(
                {'error': 'No tiene permisos para pagar este cargo'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Validar estado del cargo
        if cargo.estado != EstadoCargo.PENDIENTE:
            return Response({
                'error': f'No se puede pagar un cargo en estado "{cargo.get_estado_display()}"',
                'estado_actual': cargo.estado,
                'cargo_id': cargo.id
            }, status=status.HTTP_400_BAD_REQUEST)
        
        serializer = PagarCargoSerializer(
            data=request.data, 
            context={
                'cargo': cargo,
                'usuario': request.user
            }
        )
        
        if serializer.is_valid():
            # Obtener datos del pago
            referencia = serializer.validated_data.get('referencia_pago', '')
            observaciones = serializer.validated_data.get('observaciones', '')
            metodo_pago = serializer.validated_data.get('metodo_pago', 'online')
            monto_pagado = serializer.validated_data.get('monto_pagado', cargo.monto)
            
            # Determinar si es pago de admin por residente
            es_pago_admin = (hasattr(request.user, 'role') and request.user.role == 'admin') and cargo.residente != request.user
            
            # Calcular monto con recargo si está vencido
            monto_original = cargo.monto
            monto_final = cargo.calcular_monto_con_recargo() if hasattr(cargo, 'calcular_monto_con_recargo') else monto_original
            
            # Procesar pago
            cargo.marcar_como_pagado(
                referencia_pago=referencia,
                usuario_proceso=request.user
            )
            
            # Añadir observaciones
            observaciones_completas = []
            if es_pago_admin:
                observaciones_completas.append(f"Pago procesado por admin: {request.user.username}")
            if metodo_pago != 'online':
                observaciones_completas.append(f"Método de pago: {metodo_pago}")
            if monto_final != monto_original:
                observaciones_completas.append(f"Monto original: ${monto_original}, con recargo: ${monto_final}")
            if observaciones:
                observaciones_completas.append(f"Nota: {observaciones}")
            
            if observaciones_completas:
                nueva_observacion = "\n".join(observaciones_completas)
                cargo.observaciones = f"{cargo.observaciones}\n{nueva_observacion}".strip()
                cargo.save()
            
            # Preparar respuesta
            response_data = {
                'exito': True,
                'mensaje': 'Pago procesado exitosamente',
                'pago_info': {
                    'cargo_id': cargo.id,
                    'residente': cargo.residente.username,
                    'concepto': cargo.concepto.nombre,
                    'monto_original': float(monto_original),
                    'monto_pagado': float(monto_final),
                    'fecha_pago': cargo.fecha_pago,
                    'referencia_pago': cargo.referencia_pago,
                    'procesado_por': request.user.username,
                    'es_pago_admin': es_pago_admin,
                    'estado_anterior': 'pendiente',
                    'estado_actual': cargo.get_estado_display()
                },
                'cargo': CargoFinancieroSerializer(cargo).data
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def pagos(self, request):
        """
        Historial de pagos
        T3: Pagar cuota en línea - Módulo 2 Gestión Financiera Básica
        
        Proporciona el historial completo de pagos realizados.
        Para residentes: Solo sus propios pagos
        Para admins: Todos los pagos o filtrado por residente
        """
        user = request.user
        queryset = CargoFinanciero.objects.filter(estado=EstadoCargo.PAGADO).select_related('concepto', 'residente')
        
        # Aplicar filtros según permisos
        if hasattr(user, 'role') and user.role == 'admin' or user.is_superuser:
            # Admin puede ver todos los pagos
            residente_id = request.query_params.get('residente')
            if residente_id:
                try:
                    queryset = queryset.filter(residente_id=int(residente_id))
                except (ValueError, TypeError):
                    return Response(
                        {'error': 'ID de residente inválido'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
        else:
            # Residentes solo ven sus propios pagos
            queryset = queryset.filter(residente=user)
        
        # Filtros adicionales
        fecha_desde = request.query_params.get('fecha_desde')
        fecha_hasta = request.query_params.get('fecha_hasta')
        concepto_id = request.query_params.get('concepto')
        
        if fecha_desde:
            try:
                from datetime import datetime
                fecha_desde_obj = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
                queryset = queryset.filter(fecha_pago__date__gte=fecha_desde_obj)
            except ValueError:
                return Response(
                    {'error': 'Formato de fecha_desde inválido. Use YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        if fecha_hasta:
            try:
                from datetime import datetime
                fecha_hasta_obj = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
                queryset = queryset.filter(fecha_pago__date__lte=fecha_hasta_obj)
            except ValueError:
                return Response(
                    {'error': 'Formato de fecha_hasta inválido. Use YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        if concepto_id:
            try:
                queryset = queryset.filter(concepto_id=int(concepto_id))
            except (ValueError, TypeError):
                return Response(
                    {'error': 'ID de concepto inválido'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Ordenar por fecha de pago más reciente
        queryset = queryset.order_by('-fecha_pago')
        
        # Estadísticas del período consultado
        total_pagos = queryset.count()
        from django.db import models
        monto_total = queryset.aggregate(
            total=models.Sum('monto')
        )['total'] or 0
        
        # Paginar resultados
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = CargoFinancieroListSerializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
            response.data['estadisticas'] = {
                'total_pagos': total_pagos,
                'monto_total': float(monto_total),
                'periodo_consultado': {
                    'fecha_desde': fecha_desde,
                    'fecha_hasta': fecha_hasta
                }
            }
            return response
        
        serializer = CargoFinancieroListSerializer(queryset, many=True)
        return Response({
            'pagos': serializer.data,
            'estadisticas': {
                'total_pagos': total_pagos,
                'monto_total': float(monto_total),
                'periodo_consultado': {
                    'fecha_desde': fecha_desde,
                    'fecha_hasta': fecha_hasta
                }
            }
        })

    @action(detail=True, methods=['get'])
    def comprobante(self, request, pk=None):
        """
        Generar comprobante de pago en PDF
        T4: Generar comprobante de pago - Módulo 2 Gestión Financiera Básica
        
        Genera y descarga un comprobante en PDF para un cargo pagado.
        Para residentes: Solo pueden generar comprobantes de sus propios pagos
        Para admins: Pueden generar comprobantes de cualquier pago
        """
        from django.http import HttpResponse
        from .services import comprobante_service
        
        cargo = get_object_or_404(CargoFinanciero, pk=pk)
        
        # Verificar que el cargo está pagado
        if cargo.estado != EstadoCargo.PAGADO:
            return Response({
                'error': 'Solo se pueden generar comprobantes de cargos pagados',
                'estado_actual': cargo.estado,
                'cargo_id': cargo.id
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Verificar permisos: admin o el propio residente
        if not ((hasattr(request.user, 'role') and request.user.role == 'admin') or 
                request.user.is_superuser or 
                cargo.residente == request.user):
            return Response(
                {'error': 'No tiene permisos para generar el comprobante de este cargo'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        try:
            # Generar PDF del comprobante
            pdf_buffer = comprobante_service.generar_comprobante(cargo)
            
            # Crear respuesta HTTP con el PDF
            response = HttpResponse(
                pdf_buffer.getvalue(),
                content_type='application/pdf'
            )
            
            # Nombre del archivo
            numero_comprobante = comprobante_service._generar_numero_comprobante(cargo)
            filename = f"Comprobante_{numero_comprobante}_{cargo.residente.username}.pdf"
            
            # Headers para descarga
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            response['Content-Length'] = len(pdf_buffer.getvalue())
            
            # Metadata adicional en headers personalizados
            response['X-Cargo-ID'] = str(cargo.id)
            response['X-Residente'] = cargo.residente.username
            response['X-Monto'] = str(cargo.monto)
            response['X-Numero-Comprobante'] = numero_comprobante
            
            return response
            
        except Exception as e:
            return Response({
                'error': 'Error al generar el comprobante',
                'detalle': str(e),
                'cargo_id': cargo.id
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def comprobantes(self, request):
        """
        Listar comprobantes de pagos realizados
        T4: Generar comprobante de pago - Módulo 2 Gestión Financiera Básica
        
        Proporciona lista de pagos para los cuales se pueden generar comprobantes.
        Para residentes: Solo sus propios pagos
        Para admins: Todos los pagos o filtrado por residente
        """
        user = request.user
        queryset = CargoFinanciero.objects.filter(estado=EstadoCargo.PAGADO).select_related('concepto', 'residente')
        
        # Aplicar filtros según permisos
        if hasattr(user, 'role') and user.role == 'admin' or user.is_superuser:
            # Admin puede ver todos los pagos
            residente_id = request.query_params.get('residente')
            if residente_id:
                try:
                    queryset = queryset.filter(residente_id=int(residente_id))
                except (ValueError, TypeError):
                    return Response(
                        {'error': 'ID de residente inválido'},
                        status=status.HTTP_400_BAD_REQUEST
                    )
        else:
            # Residentes solo ven sus propios pagos
            queryset = queryset.filter(residente=user)
        
        # Filtros adicionales
        fecha_desde = request.query_params.get('fecha_desde')
        fecha_hasta = request.query_params.get('fecha_hasta')
        concepto_id = request.query_params.get('concepto')
        
        if fecha_desde:
            try:
                from datetime import datetime
                fecha_desde_obj = datetime.strptime(fecha_desde, '%Y-%m-%d').date()
                queryset = queryset.filter(fecha_pago__date__gte=fecha_desde_obj)
            except ValueError:
                return Response(
                    {'error': 'Formato de fecha_desde inválido. Use YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        if fecha_hasta:
            try:
                from datetime import datetime
                fecha_hasta_obj = datetime.strptime(fecha_hasta, '%Y-%m-%d').date()
                queryset = queryset.filter(fecha_pago__date__lte=fecha_hasta_obj)
            except ValueError:
                return Response(
                    {'error': 'Formato de fecha_hasta inválido. Use YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        if concepto_id:
            try:
                queryset = queryset.filter(concepto_id=int(concepto_id))
            except (ValueError, TypeError):
                return Response(
                    {'error': 'ID de concepto inválido'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Ordenar por fecha de pago más reciente
        queryset = queryset.order_by('-fecha_pago')
        
        # Estadísticas
        total_comprobantes = queryset.count()
        from django.db import models
        monto_total = queryset.aggregate(
            total=models.Sum('monto')
        )['total'] or 0
        
        # Agregar información adicional para comprobantes
        def enriquecer_cargo(cargo):
            from .services import comprobante_service
            data = CargoFinancieroListSerializer(cargo).data
            data['numero_comprobante'] = comprobante_service._generar_numero_comprobante(cargo)
            data['puede_generar_comprobante'] = True
            data['url_comprobante'] = f'/api/finances/cargos/{cargo.id}/comprobante/'
            return data
        
        # Paginar resultados
        page = self.paginate_queryset(queryset)
        if page is not None:
            comprobantes_data = [enriquecer_cargo(cargo) for cargo in page]
            response = self.get_paginated_response(comprobantes_data)
            response.data['estadisticas'] = {
                'total_comprobantes_disponibles': total_comprobantes,
                'monto_total_comprobantes': float(monto_total),
                'periodo_consultado': {
                    'fecha_desde': fecha_desde,
                    'fecha_hasta': fecha_hasta
                }
            }
            return response
        
        comprobantes_data = [enriquecer_cargo(cargo) for cargo in queryset]
        return Response({
            'comprobantes': comprobantes_data,
            'estadisticas': {
                'total_comprobantes_disponibles': total_comprobantes,
                'monto_total_comprobantes': float(monto_total),
                'periodo_consultado': {
                    'fecha_desde': fecha_desde,
                    'fecha_hasta': fecha_hasta
                }
            }
        })

    @action(detail=False, methods=['get'])
    def vencidos(self, request):
        """Obtener cargos vencidos (solo admins)"""
        if not (hasattr(request.user, 'role') and request.user.role == 'admin') and not request.user.is_superuser:
            return Response(
                {'error': 'No tiene permisos para ver esta información'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        cargos_vencidos = CargoFinanciero.objects.filter(
            estado=EstadoCargo.PENDIENTE,
            fecha_vencimiento__lt=date.today()
        ).select_related('concepto', 'residente').order_by('fecha_vencimiento')
        
        serializer = CargoFinancieroListSerializer(cargos_vencidos, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='resumen/(?P<user_id>[^/.]+)')
    def resumen_residente(self, request, user_id=None):
        """Obtener resumen financiero de un residente"""
        # Verificar permisos
        if not user_id:
            user_id = request.user.id
        
        if str(user_id) != str(request.user.id):
            if not (hasattr(request.user, 'role') and request.user.role == 'admin') and not request.user.is_superuser:
                return Response(
                    {'error': 'No tiene permisos para ver esta información'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        residente = get_object_or_404(User, id=user_id)
        
        # Calcular resumen
        cargos_pendientes = CargoFinanciero.objects.filter(
            residente=residente,
            estado=EstadoCargo.PENDIENTE
        )
        
        cargos_vencidos = cargos_pendientes.filter(fecha_vencimiento__lt=date.today())
        
        mes_actual = date.today().replace(day=1)
        cargos_pagados_mes = CargoFinanciero.objects.filter(
            residente=residente,
            estado=EstadoCargo.PAGADO,
            fecha_pago__gte=mes_actual
        )
        
        ultimo_pago = CargoFinanciero.objects.filter(
            residente=residente,
            estado=EstadoCargo.PAGADO
        ).order_by('-fecha_pago').first()
        
        resumen = {
            'residente_info': ResidenteBasicoSerializer(residente).data,
            'total_pendiente': cargos_pendientes.aggregate(Sum('monto'))['monto__sum'] or Decimal('0.00'),
            'total_vencido': cargos_vencidos.aggregate(Sum('monto'))['monto__sum'] or Decimal('0.00'),
            'total_pagado_mes': cargos_pagados_mes.aggregate(Sum('monto'))['monto__sum'] or Decimal('0.00'),
            'cantidad_cargos_pendientes': cargos_pendientes.count(),
            'cantidad_cargos_vencidos': cargos_vencidos.count(),
            'ultimo_pago': ultimo_pago.fecha_pago if ultimo_pago else None
        }
        
        return Response(resumen)

    @action(detail=False, methods=['get'])
    def estado_cuenta(self, request):
        """
        Consultar estado de cuenta completo
        T2: Consultar estado de cuenta - Módulo 2 Gestión Financiera Básica
        
        Para residentes: Solo su propio estado de cuenta
        Para admins: Pueden especificar residente con ?residente=user_id
        """
        # Determinar el residente a consultar
        user_id = request.query_params.get('residente', None)
        
        if user_id:
            # Verificar permisos: Solo admin puede consultar otros residentes
            if not (hasattr(request.user, 'role') and request.user.role == 'admin') and not request.user.is_superuser:
                return Response(
                    {'error': 'No tiene permisos para consultar el estado de cuenta de otros residentes'},
                    status=status.HTTP_403_FORBIDDEN
                )
            residente = get_object_or_404(User, id=user_id)
        else:
            # Usuario consultando su propio estado de cuenta
            residente = request.user
            
        # VALIDACIÓN ADICIONAL: Residente no puede consultar otros aunque no especifique en query
        if not (hasattr(request.user, 'role') and request.user.role == 'admin') and not request.user.is_superuser:
            if residente != request.user:
                return Response(
                    {'error': 'Solo puede consultar su propio estado de cuenta'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Obtener fechas para filtros
        hoy = date.today()
        mes_actual = hoy.replace(day=1)
        hace_6_meses = hoy - timedelta(days=180)
        
        # CARGOS PENDIENTES
        cargos_pendientes = CargoFinanciero.objects.filter(
            residente=residente,
            estado=EstadoCargo.PENDIENTE
        ).select_related('concepto').order_by('fecha_vencimiento')
        
        # CARGOS VENCIDOS
        cargos_vencidos = cargos_pendientes.filter(fecha_vencimiento__lt=hoy)
        
        # HISTORIAL DE PAGOS (últimos 6 meses)
        historial_pagos = CargoFinanciero.objects.filter(
            residente=residente,
            estado=EstadoCargo.PAGADO,
            fecha_pago__gte=hace_6_meses
        ).select_related('concepto').order_by('-fecha_pago')
        
        # CARGOS PAGADOS ESTE MES
        pagos_mes_actual = CargoFinanciero.objects.filter(
            residente=residente,
            estado=EstadoCargo.PAGADO,
            fecha_pago__gte=mes_actual
        ).select_related('concepto')
        
        # TOTALES Y ESTADÍSTICAS
        total_pendiente = cargos_pendientes.aggregate(Sum('monto'))['monto__sum'] or Decimal('0.00')
        total_vencido = cargos_vencidos.aggregate(Sum('monto'))['monto__sum'] or Decimal('0.00')
        total_pagado_mes = pagos_mes_actual.aggregate(Sum('monto'))['monto__sum'] or Decimal('0.00')
        total_pagado_6_meses = historial_pagos.aggregate(Sum('monto'))['monto__sum'] or Decimal('0.00')
        
        # PRÓXIMO VENCIMIENTO
        proximo_vencimiento = cargos_pendientes.filter(fecha_vencimiento__gte=hoy).first()
        
        # ÚLTIMO PAGO
        ultimo_pago = CargoFinanciero.objects.filter(
            residente=residente,
            estado=EstadoCargo.PAGADO
        ).select_related('concepto').order_by('-fecha_pago').first()
        
        # DESGLOSE POR TIPO DE CONCEPTO
        desglose_pendiente = cargos_pendientes.values(
            'concepto__tipo',
            'concepto__nombre'
        ).annotate(
            cantidad=Count('id'),
            total=Sum('monto')
        ).order_by('concepto__tipo')
        
        # ESTRUCTURA DEL ESTADO DE CUENTA
        estado_cuenta = {
            'residente_info': {
                'id': residente.id,
                'username': residente.username,
                'email': residente.email,
                'nombre_completo': f"{residente.first_name} {residente.last_name}".strip() or residente.username,
                'first_name': residente.first_name,
                'last_name': residente.last_name
            },
            'fecha_consulta': hoy,
            'resumen_general': {
                'total_pendiente': total_pendiente,
                'total_vencido': total_vencido,
                'total_al_dia': total_pendiente - total_vencido,
                'cantidad_cargos_pendientes': cargos_pendientes.count(),
                'cantidad_cargos_vencidos': cargos_vencidos.count(),
                'total_pagado_mes_actual': total_pagado_mes,
                'total_pagado_6_meses': total_pagado_6_meses
            },
            'cargos_pendientes': CargoFinancieroListSerializer(cargos_pendientes, many=True).data,
            'cargos_vencidos': CargoFinancieroListSerializer(cargos_vencidos, many=True).data,
            'historial_pagos': CargoFinancieroListSerializer(historial_pagos[:20], many=True).data,  # Últimos 20
            'desglose_por_tipo': list(desglose_pendiente),
            'proximo_vencimiento': {
                'cargo': CargoFinancieroListSerializer(proximo_vencimiento).data if proximo_vencimiento else None,
                'fecha': proximo_vencimiento.fecha_vencimiento if proximo_vencimiento else None,
                'dias_restantes': (proximo_vencimiento.fecha_vencimiento - hoy).days if proximo_vencimiento else None
            },
            'ultimo_pago': {
                'cargo': CargoFinancieroListSerializer(ultimo_pago).data if ultimo_pago else None,
                'fecha': ultimo_pago.fecha_pago if ultimo_pago else None,
                'hace_dias': (hoy - ultimo_pago.fecha_pago.date()).days if ultimo_pago and ultimo_pago.fecha_pago else None
            },
            'alertas': self._generar_alertas_estado_cuenta(cargos_vencidos, proximo_vencimiento)
        }
        
        return Response(estado_cuenta)
    
    def _generar_alertas_estado_cuenta(self, cargos_vencidos, proximo_vencimiento):
        """Generar alertas relevantes para el estado de cuenta"""
        alertas = []
        
        if cargos_vencidos.exists():
            total_vencido = cargos_vencidos.aggregate(Sum('monto'))['monto__sum'] or Decimal('0.00')
            alertas.append({
                'tipo': 'vencido',
                'severidad': 'alta',
                'titulo': f'Tiene {cargos_vencidos.count()} cargo(s) vencido(s)',
                'mensaje': f'Total vencido: ${total_vencido}. Se recomienda realizar el pago lo antes posible.',
                'accion': 'Pagar cargos vencidos'
            })
        
        if proximo_vencimiento:
            dias_restantes = (proximo_vencimiento.fecha_vencimiento - date.today()).days
            if dias_restantes <= 7:
                alertas.append({
                    'tipo': 'vencimiento_proximo',
                    'severidad': 'media' if dias_restantes > 3 else 'alta',
                    'titulo': f'Cargo próximo a vencer',
                    'mensaje': f'{proximo_vencimiento.concepto.nombre} vence en {dias_restantes} día(s)',
                    'accion': 'Revisar y programar pago'
                })
        
        return alertas


class EstadisticasFinancierasViewSet(viewsets.ViewSet):
    """
    ViewSet para estadísticas financieras generales (solo administradores)
    
    Endpoints:
    - GET /api/finances/estadisticas/ - Estadísticas generales
    """
    
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request):
        """Obtener estadísticas financieras generales"""
        if not (hasattr(request.user, 'role') and request.user.role == 'admin') and not request.user.is_superuser:
            return Response(
                {'error': 'No tiene permisos para ver esta información'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Calcular estadísticas
        total_conceptos_activos = ConceptoFinanciero.objects.filter(
            estado=EstadoConcepto.ACTIVO
        ).count()
        
        cargos_pendientes = CargoFinanciero.objects.filter(estado=EstadoCargo.PENDIENTE)
        cargos_vencidos = cargos_pendientes.filter(fecha_vencimiento__lt=date.today())
        
        mes_actual = date.today().replace(day=1)
        pagos_mes_actual = CargoFinanciero.objects.filter(
            estado=EstadoCargo.PAGADO,
            fecha_pago__gte=mes_actual
        ).aggregate(Sum('monto'))['monto__sum'] or Decimal('0.00')
        
        # Conceptos más aplicados
        conceptos_mas_aplicados = CargoFinanciero.objects.values(
            'concepto__nombre', 'concepto__tipo'
        ).annotate(
            cantidad=Count('id')
        ).order_by('-cantidad')[:5]
        
        estadisticas = {
            'total_conceptos_activos': total_conceptos_activos,
            'total_cargos_pendientes': cargos_pendientes.count(),
            'monto_total_pendiente': cargos_pendientes.aggregate(Sum('monto'))['monto__sum'] or Decimal('0.00'),
            'total_cargos_vencidos': cargos_vencidos.count(),
            'monto_total_vencido': cargos_vencidos.aggregate(Sum('monto'))['monto__sum'] or Decimal('0.00'),
            'total_pagos_mes_actual': pagos_mes_actual,
            'conceptos_mas_aplicados': list(conceptos_mas_aplicados)
        }
        
        return Response(estadisticas)