"""
Vistas API para el Módulo de Reportes y Analítica
Módulo 8: Reportes y Analítica

Este módulo proporciona endpoints para:
1. Generar Reporte Financiero
2. Generar Reporte de Seguridad
3. Generar Reporte de Uso de Áreas Comunes
4. Generar Predicción de Morosidad con IA
"""

from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.db.models import Sum, Count, Avg, Q
from django.db.models.functions import TruncMonth, TruncWeek, TruncDay
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)

from .services import GrokMorosidadService
from .serializers import (
    ReporteFinancieroSerializer,
    ReporteFinancieroListSerializer,
    CrearReporteFinancieroSerializer,
    ReporteSeguridadSerializer,
    ReporteSeguridadListSerializer,
    CrearReporteSeguridadSerializer,
    ReporteUsoAreasSerializer,
    ReporteUsoAreasListSerializer,
    CrearReporteUsoAreasSerializer,
    PrediccionMorosidadSerializer,
    PrediccionMorosidadListSerializer,
    CrearPrediccionMorosidadSerializer
)
from .models import ReporteFinanciero, ReporteSeguridad, ReporteUsoAreas, PrediccionMorosidad


class IsAdminOrStaff(permissions.BasePermission):
    """
    Permiso personalizado para analítica:
    - Administradores: acceso completo
    - Staff (mantenimiento, seguridad): acceso limitado
    """
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False

        # Administradores tienen acceso completo
        if hasattr(request.user, 'role') and request.user.role == 'admin':
            return True

        # Staff limitado (mantenimiento, seguridad) puede ver reportes
        if hasattr(request.user, 'role') and request.user.role in ['maintenance', 'security']:
            return request.method in permissions.SAFE_METHODS

        return False


class ReporteFinancieroViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de Reportes Financieros
    """
    permission_classes = [IsAdminOrStaff]

    def get_serializer_class(self):
        if self.action == 'list':
            return ReporteFinancieroListSerializer
        elif self.action == 'create':
            return CrearReporteFinancieroSerializer
        elif self.action == 'retrieve':
            return ReporteFinancieroSerializer
        return ReporteFinancieroSerializer

    def get_queryset(self):
        user = self.request.user

        # Administradores ven todos los reportes
        if hasattr(user, 'role') and user.role == 'admin':
            queryset = ReporteFinanciero.objects.all()
        else:
            # Staff solo ve reportes que generaron
            queryset = ReporteFinanciero.objects.filter(generado_por=user)

        # Filtros opcionales
        tipo = self.request.query_params.get('tipo', None)
        if tipo:
            queryset = queryset.filter(tipo=tipo)

        periodo = self.request.query_params.get('periodo', None)
        if periodo:
            queryset = queryset.filter(periodo=periodo)

        return queryset.order_by('-fecha_generacion')

    def perform_create(self, serializer):
        serializer.save(generado_por=self.request.user)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def generar_reporte(self, request):
        """
        Generar un reporte financiero basado en los parámetros proporcionados
        Solo administradores pueden generar reportes
        """
        if not (hasattr(request.user, 'role') and request.user.role == 'admin'):
            return Response(
                {'error': 'No tienes permisos para generar reportes financieros'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = CrearReporteFinancieroSerializer(data=request.data)
        if serializer.is_valid():
            # Generar datos del reporte basado en el tipo
            datos_reporte = self._generar_datos_financieros(
                serializer.validated_data['tipo'],
                serializer.validated_data['fecha_inicio'],
                serializer.validated_data['fecha_fin'],
                serializer.validated_data.get('filtros_aplicados', {})
            )

            # Crear el reporte
            reporte = ReporteFinanciero.objects.create(
                titulo=serializer.validated_data['titulo'],
                descripcion=serializer.validated_data.get('descripcion', ''),
                tipo=serializer.validated_data['tipo'],
                periodo=serializer.validated_data['periodo'],
                formato=serializer.validated_data['formato'],
                fecha_inicio=serializer.validated_data['fecha_inicio'],
                fecha_fin=serializer.validated_data['fecha_fin'],
                generado_por=request.user,
                datos=datos_reporte,
                total_registros=datos_reporte.get('total_registros', 0),
                filtros_aplicados=serializer.validated_data.get('filtros_aplicados', {})
            )

            # Retornar el reporte creado
            response_serializer = ReporteFinancieroSerializer(reporte)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _generar_datos_financieros(self, tipo, fecha_inicio, fecha_fin, filtros):
        """
        Generar datos para el reporte financiero basado en el tipo
        """
        from finances.models import ConceptoFinanciero, CargoFinanciero, TipoConcepto
        from django.db.models import Sum, Count, Q
        from django.contrib.auth import get_user_model

        User = get_user_model()

        # Filtrar por fechas
        fecha_inicio = datetime.combine(fecha_inicio, datetime.min.time())
        fecha_fin = datetime.combine(fecha_fin, datetime.max.time())

        if tipo == 'ingresos':
            # Calcular ingresos reales de cuotas pagadas
            ingresos_cuotas = CargoFinanciero.objects.filter(
                estado='pagado',
                fecha_pago__range=[fecha_inicio, fecha_fin],
                concepto__tipo__in=[TipoConcepto.CUOTA_MENSUAL, TipoConcepto.CUOTA_EXTRAORDINARIA]
            ).aggregate(
                total=Sum('monto'),
                count=Count('id')
            )

            # Ingresos por mes
            ingresos_por_mes = {}
            for mes in range(fecha_inicio.month, fecha_fin.month + 1):
                mes_inicio = fecha_inicio.replace(month=mes, day=1)
                if mes == 12:
                    mes_fin = mes_inicio.replace(year=mes_inicio.year + 1, month=1, day=1) - timedelta(days=1)
                else:
                    mes_fin = mes_inicio.replace(month=mes + 1, day=1) - timedelta(days=1)

                ingresos_mes = CargoFinanciero.objects.filter(
                    estado='pagado',
                    fecha_pago__range=[mes_inicio, mes_fin],
                    concepto__tipo__in=[TipoConcepto.CUOTA_MENSUAL, TipoConcepto.CUOTA_EXTRAORDINARIA]
                ).aggregate(total=Sum('monto'))['total'] or 0

                ingresos_por_mes[f"{mes_inicio.year}-{mes_inicio.month:02d}"] = float(ingresos_mes)

            # Fuentes de ingreso
            fuentes = CargoFinanciero.objects.filter(
                estado='pagado',
                fecha_pago__range=[fecha_inicio, fecha_fin]
            ).values('concepto__tipo').annotate(
                total=Sum('monto')
            ).order_by('-total')

            fuentes_dict = {}
            for fuente in fuentes:
                tipo_display = dict(TipoConcepto.choices)[fuente['concepto__tipo']]
                fuentes_dict[tipo_display.lower().replace(' ', '_')] = float(fuente['total'])

            return {
                'total_ingresos': float(ingresos_cuotas['total'] or 0),
                'ingresos_por_mes': ingresos_por_mes,
                'fuentes_ingreso': fuentes_dict,
                'total_registros': ingresos_cuotas['count'] or 0
            }

        elif tipo == 'egresos':
            # Para egresos, por ahora usamos datos mock ya que no hay modelo de gastos
            # Se puede extender cuando se implemente el módulo de gastos
            return {
                'total_egresos': 0.00,
                'egresos_por_categoria': {},
                'egresos_por_mes': {},
                'total_registros': 0
            }

        elif tipo == 'balance':
            # Calcular balance basado en ingresos y egresos
            ingresos_total = CargoFinanciero.objects.filter(
                estado='pagado',
                fecha_pago__range=[fecha_inicio, fecha_fin]
            ).aggregate(total=Sum('monto'))['total'] or 0

            # Por ahora egresos = 0
            egresos_total = 0
            balance_neto = ingresos_total - egresos_total

            return {
                'ingresos_totales': float(ingresos_total),
                'egresos_totales': float(egresos_total),
                'balance_neto': float(balance_neto),
                'reservas_acumuladas': 0.00,  # Se puede calcular basado en historial
                'proyeccion_mensual': float(ingresos_total / max(1, (fecha_fin - fecha_inicio).days / 30)),
                'total_registros': CargoFinanciero.objects.filter(
                    fecha_aplicacion__range=[fecha_inicio.date(), fecha_fin.date()]
                ).count()
            }

        elif tipo == 'morosidad':
            # Calcular datos de morosidad reales
            total_residentes = User.objects.filter(role='resident').count()

            residentes_al_dia = CargoFinanciero.objects.filter(
                residente__role='resident',
                estado='pagado',
                fecha_vencimiento__range=[fecha_inicio.date(), fecha_fin.date()]
            ).values('residente').distinct().count()

            # Morosidad por mes
            morosidad_por_mes = {}
            for mes in range(fecha_inicio.month, fecha_fin.month + 1):
                mes_inicio = fecha_inicio.replace(month=mes, day=1)
                if mes == 12:
                    mes_fin = mes_inicio.replace(year=mes_inicio.year + 1, month=1, day=1) - timedelta(days=1)
                else:
                    mes_fin = mes_inicio.replace(month=mes + 1, day=1) - timedelta(days=1)

                morosos_mes = CargoFinanciero.objects.filter(
                    residente__role='resident',
                    estado__in=['pendiente', 'vencido'],
                    fecha_vencimiento__range=[mes_inicio.date(), mes_fin.date()]
                ).values('residente').distinct().count()

                morosidad_por_mes[f"{mes_inicio.year}-{mes_inicio.month:02d}"] = morosos_mes

            monto_moroso = CargoFinanciero.objects.filter(
                residente__role='resident',
                estado__in=['pendiente', 'vencido'],
                fecha_vencimiento__range=[fecha_inicio.date(), fecha_fin.date()]
            ).aggregate(total=Sum('monto'))['total'] or 0

            return {
                'total_residentes': total_residentes,
                'residentes_al_dia': residentes_al_dia,
                'residentes_morosos': total_residentes - residentes_al_dia,
                'porcentaje_morosos': round(((total_residentes - residentes_al_dia) / max(1, total_residentes)) * 100, 2),
                'monto_total_moroso': float(monto_moroso),
                'morosidad_por_mes': morosidad_por_mes,
                'total_registros': total_residentes
            }

        else:
            return {
                'mensaje': f'Reporte de tipo {tipo} generado exitosamente',
                'periodo': f'{fecha_inicio.date()} - {fecha_fin.date()}',
                'total_registros': 0
            }


class ReporteSeguridadViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de Reportes de Seguridad
    """
    permission_classes = [IsAdminOrStaff]

    def get_serializer_class(self):
        if self.action == 'list':
            return ReporteSeguridadListSerializer
        elif self.action == 'create':
            return CrearReporteSeguridadSerializer
        elif self.action == 'retrieve':
            return ReporteSeguridadSerializer
        return ReporteSeguridadSerializer

    def get_queryset(self):
        user = self.request.user

        # Administradores ven todos los reportes
        if hasattr(user, 'role') and user.role == 'admin':
            queryset = ReporteSeguridad.objects.all()
        else:
            # Staff solo ve reportes que generaron
            queryset = ReporteSeguridad.objects.filter(generado_por=user)

        # Filtros opcionales
        tipo = self.request.query_params.get('tipo', None)
        if tipo:
            queryset = queryset.filter(tipo=tipo)

        return queryset.order_by('-fecha_generacion')

    def perform_create(self, serializer):
        serializer.save(generado_por=self.request.user)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def generar_reporte(self, request):
        """
        Generar un reporte de seguridad basado en los parámetros proporcionados
        Administradores y personal de seguridad pueden generar reportes
        """
        if not (hasattr(request.user, 'role') and
                request.user.role in ['admin', 'security']):
            return Response(
                {'error': 'No tienes permisos para generar reportes de seguridad'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = CrearReporteSeguridadSerializer(data=request.data)
        if serializer.is_valid():
            # Generar datos del reporte basado en el tipo
            datos_reporte = self._generar_datos_seguridad(
                serializer.validated_data['tipo'],
                serializer.validated_data['fecha_inicio'],
                serializer.validated_data['fecha_fin'],
                serializer.validated_data.get('filtros_aplicados', {})
            )

            # Crear el reporte
            reporte = ReporteSeguridad.objects.create(
                titulo=serializer.validated_data['titulo'],
                descripcion=serializer.validated_data.get('descripcion', ''),
                tipo=serializer.validated_data['tipo'],
                periodo=serializer.validated_data['periodo'],
                fecha_inicio=serializer.validated_data['fecha_inicio'],
                fecha_fin=serializer.validated_data['fecha_fin'],
                generado_por=request.user,
                datos=datos_reporte,
                total_eventos=datos_reporte.get('total_eventos', 0),
                eventos_criticos=datos_reporte.get('eventos_criticos', 0),
                alertas_generadas=datos_reporte.get('alertas_generadas', 0),
                filtros_aplicados=serializer.validated_data.get('filtros_aplicados', {})
            )

            # Retornar el reporte creado
            response_serializer = ReporteSeguridadSerializer(reporte)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _generar_datos_seguridad(self, tipo, fecha_inicio, fecha_fin, filtros):
        """
        Generar datos para el reporte de seguridad basado en el tipo
        """
        from modulo_ia.models import Acceso
        from audit.models import RegistroAuditoria, TipoActividad, NivelImportancia
        from django.db.models import Count

        # Filtrar por fechas
        fecha_inicio = datetime.combine(fecha_inicio, datetime.min.time())
        fecha_fin = datetime.combine(fecha_fin, datetime.max.time())

        if tipo == 'accesos':
            # Datos de accesos reales
            accesos_total = Acceso.objects.filter(
                fecha_hora__range=[fecha_inicio, fecha_fin]
            ).count()

            accesos_autorizados = Acceso.objects.filter(
                fecha_hora__range=[fecha_inicio, fecha_fin],
                estado='permitido'
            ).count()

            accesos_denegados = Acceso.objects.filter(
                fecha_hora__range=[fecha_inicio, fecha_fin],
                estado='denegado'
            ).count()

            # Accesos por hora
            accesos_por_hora = {}
            for hora in range(6, 24):
                hora_inicio = fecha_inicio.replace(hour=hora)
                hora_fin = hora_inicio.replace(hour=hora + 1)
                count = Acceso.objects.filter(
                    fecha_hora__range=[hora_inicio, hora_fin]
                ).count()
                accesos_por_hora[f"{hora:02d}:00-{hora+1:02d}:00"] = count

            # Métodos de acceso
            metodos = Acceso.objects.filter(
                fecha_hora__range=[fecha_inicio, fecha_fin]
            ).values('tipo_acceso').annotate(
                count=Count('id')
            )

            metodos_dict = {}
            for metodo in metodos:
                metodos_dict[metodo['tipo_acceso']] = metodo['count']

            # Alertas de auditoría (accesos denegados críticos)
            alertas = RegistroAuditoria.objects.filter(
                timestamp__range=[fecha_inicio, fecha_fin],
                tipo_actividad__in=['acceso_denegado', 'error_sistema'],
                nivel_importancia__in=['alto', 'critico']
            ).count()

            return {
                'total_accesos': accesos_total,
                'accesos_autorizados': accesos_autorizados,
                'accesos_denegados': accesos_denegados,
                'accesos_por_hora': accesos_por_hora,
                'metodos_acceso': metodos_dict,
                'total_eventos': accesos_total,
                'eventos_criticos': accesos_denegados,
                'alertas_generadas': alertas
            }

        elif tipo == 'incidentes':
            # Incidentes basados en auditoría
            incidentes = RegistroAuditoria.objects.filter(
                timestamp__range=[fecha_inicio, fecha_fin],
                tipo_actividad__in=['acceso_denegado', 'error_sistema'],
                nivel_importancia__in=['alto', 'critico']
            )

            total_incidentes = incidentes.count()
            incidentes_resueltos = incidentes.filter(descripcion__icontains='resuelto').count()

            # Tipos de incidentes
            tipos_incidentes = incidentes.values('tipo_actividad').annotate(
                count=Count('id')
            )

            tipos_dict = {}
            for tipo in tipos_incidentes:
                tipos_dict[tipo['tipo_actividad']] = tipo['count']

            return {
                'total_incidentes': total_incidentes,
                'incidentes_por_tipo': tipos_dict,
                'incidentes_resueltos': incidentes_resueltos,
                'incidentes_pendientes': total_incidentes - incidentes_resueltos,
                'tiempo_respuesta_promedio': '2.5 horas',  # Se puede calcular basado en timestamps
                'total_eventos': total_incidentes,
                'eventos_criticos': incidentes.filter(nivel_importancia='critico').count(),
                'alertas_generadas': total_incidentes
            }

        elif tipo == 'alertas':
            # Alertas del sistema
            alertas = RegistroAuditoria.objects.filter(
                timestamp__range=[fecha_inicio, fecha_fin],
                nivel_importancia__in=['alto', 'critico']
            )

            total_alertas = alertas.count()
            alertas_activas = alertas.filter(descripcion__icontains='activo').count()

            # Alertas por tipo
            alertas_por_tipo = alertas.values('tipo_actividad').annotate(
                count=Count('id')
            )

            tipos_dict = {}
            for tipo in alertas_por_tipo:
                tipos_dict[tipo['tipo_actividad']] = tipo['count']

            return {
                'total_alertas': total_alertas,
                'alertas_por_tipo': tipos_dict,
                'alertas_activas': alertas_activas,
                'alertas_resueltas': total_alertas - alertas_activas,
                'tiempo_resolucion_promedio': '3.2 horas',  # Se puede calcular
                'total_eventos': total_alertas,
                'eventos_criticos': alertas.filter(nivel_importancia='critico').count(),
                'alertas_generadas': total_alertas
            }

        else:
            return {
                'mensaje': f'Reporte de seguridad {tipo} generado exitosamente',
                'periodo': f'{fecha_inicio.date()} - {fecha_fin.date()}',
                'total_eventos': 0,
                'eventos_criticos': 0,
                'alertas_generadas': 0
            }


class ReporteUsoAreasViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de Reportes de Uso de Áreas Comunes
    """
    permission_classes = [IsAdminOrStaff]

    def get_serializer_class(self):
        if self.action == 'list':
            return ReporteUsoAreasListSerializer
        elif self.action == 'create':
            return CrearReporteUsoAreasSerializer
        elif self.action == 'retrieve':
            return ReporteUsoAreasSerializer
        return ReporteUsoAreasSerializer

    def get_queryset(self):
        user = self.request.user

        # Administradores ven todos los reportes
        if hasattr(user, 'role') and user.role == 'admin':
            queryset = ReporteUsoAreas.objects.all()
        else:
            # Staff solo ve reportes que generaron
            queryset = ReporteUsoAreas.objects.filter(generado_por=user)

        # Filtros opcionales
        area = self.request.query_params.get('area', None)
        if area:
            queryset = queryset.filter(area=area)

        return queryset.order_by('-fecha_generacion')

    def perform_create(self, serializer):
        serializer.save(generado_por=self.request.user)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def generar_reporte(self, request):
        """
        Generar un reporte de uso de áreas basado en los parámetros proporcionados
        Administradores pueden generar reportes
        """
        if not (hasattr(request.user, 'role') and request.user.role == 'admin'):
            return Response(
                {'error': 'No tienes permisos para generar reportes de uso de áreas'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = CrearReporteUsoAreasSerializer(data=request.data)
        if serializer.is_valid():
            # Generar datos del reporte basado en el área y métrica
            datos_reporte = self._generar_datos_uso_areas(
                serializer.validated_data['area'],
                serializer.validated_data['metrica_principal'],
                serializer.validated_data['fecha_inicio'],
                serializer.validated_data['fecha_fin'],
                serializer.validated_data.get('filtros_aplicados', {})
            )

            # Crear el reporte
            reporte = ReporteUsoAreas.objects.create(
                titulo=serializer.validated_data['titulo'],
                descripcion=serializer.validated_data.get('descripcion', ''),
                area=serializer.validated_data['area'],
                periodo=serializer.validated_data['periodo'],
                metrica_principal=serializer.validated_data['metrica_principal'],
                fecha_inicio=serializer.validated_data['fecha_inicio'],
                fecha_fin=serializer.validated_data['fecha_fin'],
                generado_por=request.user,
                datos=datos_reporte,
                total_reservas=datos_reporte.get('total_reservas', 0),
                horas_ocupacion=datos_reporte.get('horas_ocupacion', 0),
                tasa_ocupacion_promedio=datos_reporte.get('tasa_ocupacion_promedio', 0),
                filtros_aplicados=serializer.validated_data.get('filtros_aplicados', {})
            )

            # Retornar el reporte creado
            response_serializer = ReporteUsoAreasSerializer(reporte)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _generar_datos_uso_areas(self, area, metrica, fecha_inicio, fecha_fin, filtros):
        """
        Generar datos para el reporte de uso de áreas basado en el área y métrica
        """
        from reservations.models import Reserva, AreaComun, EstadoReserva
        from django.db.models import Count, Sum, Avg
        from django.db.models.functions import TruncDate

        # Filtrar por fechas
        fecha_inicio = datetime.combine(fecha_inicio, datetime.min.time())
        fecha_fin = datetime.combine(fecha_fin, datetime.max.time())

        # Filtrar por área si no es 'todas'
        area_filter = {}
        if area != 'todas':
            try:
                area_obj = AreaComun.objects.get(tipo=area)
                area_filter['area_comun'] = area_obj
            except AreaComun.DoesNotExist:
                return {
                    'mensaje': f'Área {area} no encontrada',
                    'total_reservas': 0,
                    'horas_ocupacion': 0,
                    'tasa_ocupacion_promedio': 0
                }

        if metrica == 'ocupacion':
            # Calcular tasa de ocupación
            reservas_confirmadas = Reserva.objects.filter(
                **area_filter,
                fecha__range=[fecha_inicio.date(), fecha_fin.date()],
                estado__in=[EstadoReserva.CONFIRMADA, EstadoReserva.PAGADA, EstadoReserva.USADA]
            )

            total_reservas = reservas_confirmadas.count()
            horas_totales = reservas_confirmadas.aggregate(
                total_horas=Sum('duracion_horas')
            )['total_horas'] or 0

            # Ocupación por día de la semana
            ocupacion_por_dia = {}
            dias_semana = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']

            for i, dia in enumerate(dias_semana):
                reservas_dia = reservas_confirmadas.filter(fecha__week_day=i+1)
                horas_dia = reservas_dia.aggregate(total=Sum('duracion_horas'))['total'] or 0
                ocupacion_por_dia[dia] = float(horas_dia)

            # Ocupación por hora del día
            ocupacion_por_hora = {}
            for hora in range(8, 21):  # 8 AM a 8 PM
                reservas_hora = reservas_confirmadas.filter(
                    hora_inicio__hour=hora
                )
                horas_hora = reservas_hora.aggregate(total=Sum('duracion_horas'))['total'] or 0
                ocupacion_por_hora[f"{hora:02d}:00"] = float(horas_hora)

            # Calcular tasa de ocupación promedio (simplificada)
            # Asumiendo 12 horas de operación por día
            dias_totales = (fecha_fin.date() - fecha_inicio.date()).days + 1
            horas_disponibles = dias_totales * 12  # 12 horas por día
            tasa_ocupacion = (horas_totales / max(1, horas_disponibles)) * 100

            return {
                'tasa_ocupacion_promedio': round(float(tasa_ocupacion), 2),
                'ocupacion_por_dia': ocupacion_por_dia,
                'ocupacion_por_hora': ocupacion_por_hora,
                'total_reservas': total_reservas,
                'horas_ocupacion': float(horas_totales),
                'tasa_ocupacion_promedio': round(float(tasa_ocupacion), 2)
            }

        elif metrica == 'reservas':
            # Estadísticas de reservas
            reservas = Reserva.objects.filter(
                **area_filter,
                fecha__range=[fecha_inicio.date(), fecha_fin.date()]
            )

            total_reservas = reservas.count()
            reservas_confirmadas = reservas.filter(
                estado__in=[EstadoReserva.CONFIRMADA, EstadoReserva.PAGADA, EstadoReserva.USADA]
            ).count()

            reservas_canceladas = reservas.filter(estado=EstadoReserva.CANCELADA).count()

            # Reservas por mes
            reservas_por_mes = {}
            for mes in range(fecha_inicio.month, fecha_fin.month + 1):
                mes_inicio = fecha_inicio.replace(month=mes, day=1)
                if mes == 12:
                    mes_fin = mes_inicio.replace(year=mes_inicio.year + 1, month=1, day=1) - timedelta(days=1)
                else:
                    mes_fin = mes_inicio.replace(month=mes + 1, day=1) - timedelta(days=1)

                count_mes = reservas.filter(fecha__range=[mes_inicio.date(), mes_fin.date()]).count()
                reservas_por_mes[f"{mes_inicio.year}-{mes_inicio.month:02d}"] = count_mes

            # Reservas por día de la semana
            reservas_por_dia = {}
            dias_semana = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo']

            for i, dia in enumerate(dias_semana):
                count_dia = reservas.filter(fecha__week_day=i+1).count()
                reservas_por_dia[dia] = count_dia

            horas_totales = reservas.filter(
                estado__in=[EstadoReserva.CONFIRMADA, EstadoReserva.PAGADA, EstadoReserva.USADA]
            ).aggregate(total=Sum('duracion_horas'))['total'] or 0

            return {
                'total_reservas': total_reservas,
                'reservas_confirmadas': reservas_confirmadas,
                'reservas_canceladas': reservas_canceladas,
                'reservas_por_mes': reservas_por_mes,
                'reservas_por_dia_semana': reservas_por_dia,
                'total_reservas': total_reservas,
                'horas_ocupacion': float(horas_totales),
                'tasa_ocupacion_promedio': 0  # Se calcula en la métrica de ocupación
            }

        else:
            # Para otras métricas, devolver datos básicos
            reservas = Reserva.objects.filter(
                **area_filter,
                fecha__range=[fecha_inicio.date(), fecha_fin.date()],
                estado__in=[EstadoReserva.CONFIRMADA, EstadoReserva.PAGADA, EstadoReserva.USADA]
            )

            total_reservas = reservas.count()
            horas_totales = reservas.aggregate(total=Sum('duracion_horas'))['total'] or 0

            return {
                'mensaje': f'Reporte de uso de {area} generado exitosamente',
                'metrica': metrica,
                'periodo': f'{fecha_inicio.date()} - {fecha_fin.date()}',
                'total_reservas': total_reservas,
                'horas_ocupacion': float(horas_totales),
                'tasa_ocupacion_promedio': 0
            }


class PrediccionMorosidadViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de Predicciones de Morosidad
    """
    permission_classes = [IsAdminOrStaff]

    def get_serializer_class(self):
        if self.action == 'list':
            return PrediccionMorosidadListSerializer
        elif self.action == 'create':
            return CrearPrediccionMorosidadSerializer
        elif self.action == 'retrieve':
            return PrediccionMorosidadSerializer
        return PrediccionMorosidadSerializer

    def get_queryset(self):
        user = self.request.user

        # Administradores ven todas las predicciones
        if hasattr(user, 'role') and user.role == 'admin':
            queryset = PrediccionMorosidad.objects.all()
        else:
            # Staff solo ve predicciones que generaron
            queryset = PrediccionMorosidad.objects.filter(generado_por=user)

        # Filtros opcionales
        modelo = self.request.query_params.get('modelo', None)
        if modelo:
            queryset = queryset.filter(modelo_usado=modelo)

        return queryset.order_by('-fecha_prediccion')

    def perform_create(self, serializer):
        serializer.save(generado_por=self.request.user)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def generar_prediccion(self, request):
        """
        Generar una predicción de morosidad usando IA
        Solo administradores pueden generar predicciones
        """
        if not (hasattr(request.user, 'role') and request.user.role == 'admin'):
            return Response(
                {'error': 'No tienes permisos para generar predicciones de morosidad'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = CrearPrediccionMorosidadSerializer(data=request.data)
        if serializer.is_valid():
            # Generar predicción usando IA
            resultados_prediccion = self._generar_prediccion_ia(
                serializer.validated_data['modelo_usado'],
                serializer.validated_data.get('datos_entrada', {}),
                serializer.validated_data.get('parametros_modelo', {}),
                serializer.validated_data.get('residente_id', None)
            )

            # Crear la predicción
            prediccion = PrediccionMorosidad.objects.create(
                titulo=serializer.validated_data['titulo'],
                descripcion=serializer.validated_data.get('descripcion', ''),
                modelo_usado=serializer.validated_data['modelo_usado'],
                periodo_predicho=serializer.validated_data['periodo_predicho'],
                generado_por=request.user,
                datos_entrada=serializer.validated_data.get('datos_entrada', {}),
                resultados=resultados_prediccion['resultados'],
                total_residentes_analizados=resultados_prediccion['total_residentes_analizados'],
                residentes_riesgo_alto=resultados_prediccion['residentes_riesgo_alto'],
                residentes_riesgo_medio=resultados_prediccion['residentes_riesgo_medio'],
                precision_modelo=resultados_prediccion['precision_modelo'],
                parametros_modelo=serializer.validated_data.get('parametros_modelo', {}),
                metricas_evaluacion=resultados_prediccion['metricas_evaluacion'],
                nivel_confianza=resultados_prediccion['nivel_confianza'],
                residente_especifico=serializer.validated_data.get('residente_id', None) is not None
            )

            # Retornar la predicción creada
            response_serializer = PrediccionMorosidadSerializer(prediccion)
            return Response(response_serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def _generar_prediccion_ia(self, modelo, datos_entrada, parametros, residente_id=None):
        """
        Generar predicción de morosidad usando IA con Grok
        """
        try:
            # Inicializar servicio de Grok
            grok_service = GrokMorosidadService()

            # Validar datos de entrada
            validacion = grok_service.validar_datos_entrada(datos_entrada)

            if not validacion['valido']:
                # Si hay errores de validación, retornar error
                return {
                    'error': 'Datos de entrada inválidos',
                    'detalles': validacion['errores'],
                    'warnings': validacion['warnings'],
                    'total_residentes_analizados': 0,
                    'residentes_riesgo_alto': 0,
                    'residentes_riesgo_medio': 0,
                    'precision_modelo': 0.0,
                    'nivel_confianza': 'bajo',
                    'metricas_evaluacion': {},
                    'resultados': {'error': 'Datos inválidos'}
                }

            # Generar predicción usando Grok
            resultado_prediccion = grok_service.generar_prediccion_morosidad(
                modelo=modelo,
                datos_entrada=datos_entrada,
                parametros=parametros,
                residente_id=residente_id
            )

            # Agregar información de validación
            resultado_prediccion['validacion_datos'] = validacion

            return resultado_prediccion

        except Exception as e:
            # En caso de error, usar método de fallback básico
            logger.error(f"Error generando predicción con IA: {e}")

            # Retornar respuesta de error
            return {
                'error': f'Error interno: {str(e)}',
                'total_residentes_analizados': 0,
                'residentes_riesgo_alto': 0,
                'residentes_riesgo_medio': 0,
                'precision_modelo': 0.0,
                'nivel_confianza': 'bajo',
                'metricas_evaluacion': {},
                'resultados': {'error': str(e)},
                'fuente': 'error'
            }