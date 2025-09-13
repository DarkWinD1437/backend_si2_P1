"""
Serializers para el Módulo de Gestión Financiera
Módulo 2: Gestión Financiera Básica - T1: Configurar Cuotas y Multas
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from datetime import date, timedelta
from .models import ConceptoFinanciero, CargoFinanciero, TipoConcepto, EstadoConcepto, EstadoCargo

User = get_user_model()


class ConceptoFinancieroSerializer(serializers.ModelSerializer):
    """Serializer para ConceptoFinanciero con validaciones"""
    
    creado_por_info = serializers.SerializerMethodField()
    esta_vigente = serializers.ReadOnlyField()
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)

    class Meta:
        model = ConceptoFinanciero
        fields = [
            'id', 'nombre', 'descripcion', 'tipo', 'tipo_display',
            'monto', 'estado', 'estado_display', 'fecha_vigencia_desde',
            'fecha_vigencia_hasta', 'es_recurrente', 'aplica_a_todos',
            'creado_por', 'creado_por_info', 'fecha_creacion',
            'fecha_modificacion', 'esta_vigente'
        ]
        read_only_fields = ['creado_por', 'fecha_creacion', 'fecha_modificacion']

    def get_creado_por_info(self, obj):
        """Información básica del usuario que creó el concepto"""
        if obj.creado_por:
            return {
                'id': obj.creado_por.id,
                'username': obj.creado_por.username,
                'nombre_completo': f"{obj.creado_por.first_name} {obj.creado_por.last_name}".strip()
            }
        return None

    def validate(self, data):
        """Validaciones personalizadas"""
        # Validar fechas de vigencia
        fecha_desde = data.get('fecha_vigencia_desde')
        fecha_hasta = data.get('fecha_vigencia_hasta')
        
        if fecha_hasta and fecha_desde and fecha_hasta < fecha_desde:
            raise serializers.ValidationError({
                'fecha_vigencia_hasta': 'La fecha de fin no puede ser anterior a la fecha de inicio'
            })
        
        # Validar monto
        if data.get('monto') and data['monto'] <= 0:
            raise serializers.ValidationError({
                'monto': 'El monto debe ser mayor a 0'
            })
        
        return data

    def create(self, validated_data):
        """Asignar usuario que crea el concepto"""
        validated_data['creado_por'] = self.context['request'].user
        return super().create(validated_data)


class ConceptoFinancieroListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listados"""
    
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    esta_vigente = serializers.ReadOnlyField()

    class Meta:
        model = ConceptoFinanciero
        fields = [
            'id', 'nombre', 'tipo', 'tipo_display', 'monto',
            'estado', 'estado_display', 'fecha_vigencia_desde',
            'fecha_vigencia_hasta', 'esta_vigente', 'es_recurrente'
        ]


class ResidenteBasicoSerializer(serializers.ModelSerializer):
    """Serializer básico para información de residentes"""
    
    nombre_completo = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'nombre_completo']

    def get_nombre_completo(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username


class CargoFinancieroSerializer(serializers.ModelSerializer):
    """Serializer para CargoFinanciero con validaciones"""
    
    concepto_info = ConceptoFinancieroListSerializer(source='concepto', read_only=True)
    residente_info = ResidenteBasicoSerializer(source='residente', read_only=True)
    aplicado_por_info = serializers.SerializerMethodField()
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    esta_vencido = serializers.ReadOnlyField()
    dias_para_vencimiento = serializers.ReadOnlyField()

    class Meta:
        model = CargoFinanciero
        fields = [
            'id', 'concepto', 'concepto_info', 'residente', 'residente_info',
            'monto', 'estado', 'estado_display', 'fecha_aplicacion',
            'fecha_vencimiento', 'fecha_pago', 'observaciones',
            'referencia_pago', 'aplicado_por', 'aplicado_por_info',
            'fecha_creacion', 'fecha_modificacion', 'esta_vencido',
            'dias_para_vencimiento'
        ]
        read_only_fields = ['aplicado_por', 'fecha_creacion', 'fecha_modificacion']

    def get_aplicado_por_info(self, obj):
        """Información del usuario que aplicó el cargo"""
        if obj.aplicado_por:
            return {
                'id': obj.aplicado_por.id,
                'username': obj.aplicado_por.username,
                'nombre_completo': f"{obj.aplicado_por.first_name} {obj.aplicado_por.last_name}".strip()
            }
        return None

    def validate(self, data):
        """Validaciones personalizadas"""
        # Validar fechas
        fecha_aplicacion = data.get('fecha_aplicacion', date.today())
        fecha_vencimiento = data.get('fecha_vencimiento')
        
        if fecha_vencimiento and fecha_vencimiento < fecha_aplicacion:
            raise serializers.ValidationError({
                'fecha_vencimiento': 'La fecha de vencimiento no puede ser anterior a la fecha de aplicación'
            })
        
        # Validar monto
        if data.get('monto') and data['monto'] <= 0:
            raise serializers.ValidationError({
                'monto': 'El monto debe ser mayor a 0'
            })
        
        # Validar que el residente existe y es residente
        residente = data.get('residente')
        if residente and hasattr(residente, 'role') and residente.role not in ['resident', 'admin']:
            raise serializers.ValidationError({
                'residente': 'Solo se pueden aplicar cargos a residentes'
            })
        
        return data

    def create(self, validated_data):
        """Asignar usuario que aplica el cargo"""
        validated_data['aplicado_por'] = self.context['request'].user
        
        # Si no se especifica fecha de vencimiento, usar 30 días por defecto
        if not validated_data.get('fecha_vencimiento'):
            validated_data['fecha_vencimiento'] = date.today() + timedelta(days=30)
        
        return super().create(validated_data)


class CargoFinancieroListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listados de cargos"""
    
    concepto_nombre = serializers.CharField(source='concepto.nombre', read_only=True)
    concepto_tipo = serializers.CharField(source='concepto.tipo', read_only=True)
    residente_username = serializers.CharField(source='residente.username', read_only=True)
    residente_nombre = serializers.SerializerMethodField()
    estado_display = serializers.CharField(source='get_estado_display', read_only=True)
    esta_vencido = serializers.ReadOnlyField()

    class Meta:
        model = CargoFinanciero
        fields = [
            'id', 'concepto_nombre', 'concepto_tipo', 'residente_username',
            'residente_nombre', 'monto', 'estado', 'estado_display',
            'fecha_aplicacion', 'fecha_vencimiento', 'esta_vencido'
        ]

    def get_residente_nombre(self, obj):
        return f"{obj.residente.first_name} {obj.residente.last_name}".strip() or obj.residente.username


class PagarCargoSerializer(serializers.Serializer):
    """
    Serializer para procesar pagos de cargos
    T3: Pagar cuota en línea - Módulo 2 Gestión Financiera Básica
    
    Valida y procesa pagos tanto en línea (residentes) como presenciales (admin).
    """
    
    referencia_pago = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        help_text="Referencia del pago (número de transacción, voucher, etc.)"
    )
    
    observaciones = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text="Observaciones adicionales sobre el pago"
    )
    
    metodo_pago = serializers.ChoiceField(
        choices=[
            ('online', 'Pago en línea'),
            ('efectivo', 'Efectivo en oficina'),
            ('transferencia', 'Transferencia bancaria'),
            ('cheque', 'Cheque'),
            ('tarjeta', 'Tarjeta de crédito/débito')
        ],
        default='online',
        help_text="Método utilizado para el pago"
    )
    
    monto_pagado = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=False,
        help_text="Monto pagado (opcional, por defecto el monto del cargo)"
    )
    
    confirmar_pago = serializers.BooleanField(
        default=True,
        help_text="Confirmación de que se desea procesar el pago"
    )

    def validate(self, data):
        """Validaciones completas para el pago"""
        cargo = self.context.get('cargo')
        usuario = self.context.get('usuario')
        
        if not cargo:
            raise serializers.ValidationError("Cargo no encontrado")
        
        # Validar estado del cargo
        if cargo.estado != EstadoCargo.PENDIENTE:
            raise serializers.ValidationError({
                'estado': f"No se puede pagar un cargo en estado '{cargo.get_estado_display()}'"
            })
        
        # Validar confirmación
        if not data.get('confirmar_pago', True):
            raise serializers.ValidationError({
                'confirmar_pago': 'Debe confirmar que desea procesar el pago'
            })
        
        # Validar monto si se especifica
        monto_pagado = data.get('monto_pagado')
        if monto_pagado is not None:
            if monto_pagado <= 0:
                raise serializers.ValidationError({
                    'monto_pagado': 'El monto pagado debe ser mayor a 0'
                })
            
            # Para cargos vencidos, permitir pago con recargo
            monto_minimo = cargo.monto
            if cargo.esta_vencido and hasattr(cargo, 'calcular_monto_con_recargo'):
                monto_con_recargo = cargo.calcular_monto_con_recargo()
                if monto_pagado < monto_con_recargo:
                    raise serializers.ValidationError({
                        'monto_pagado': f'Para cargos vencidos el monto mínimo es ${monto_con_recargo} (incluye recargo)'
                    })
            elif monto_pagado < monto_minimo:
                raise serializers.ValidationError({
                    'monto_pagado': f'El monto pagado no puede ser menor al monto del cargo (${monto_minimo})'
                })
        
        # Validar método de pago según usuario
        metodo = data.get('metodo_pago', 'online')
        es_admin = hasattr(usuario, 'role') and usuario.role == 'admin'
        
        if not es_admin and metodo != 'online':
            raise serializers.ValidationError({
                'metodo_pago': 'Los residentes solo pueden usar pago en línea'
            })
        
        # Validar referencia para ciertos métodos de pago
        referencia = data.get('referencia_pago', '').strip()
        if metodo in ['transferencia', 'cheque'] and not referencia:
            raise serializers.ValidationError({
                'referencia_pago': f'Se requiere referencia de pago para método: {metodo}'
            })
        
        return data


class ResumenFinancieroSerializer(serializers.Serializer):
    """Serializer para resumen financiero de un residente"""
    
    residente_info = ResidenteBasicoSerializer(read_only=True)
    total_pendiente = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_vencido = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_pagado_mes = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    cantidad_cargos_pendientes = serializers.IntegerField(read_only=True)
    cantidad_cargos_vencidos = serializers.IntegerField(read_only=True)
    ultimo_pago = serializers.DateTimeField(read_only=True)


class EstadisticasFinancierasSerializer(serializers.Serializer):
    """Serializer para estadísticas financieras generales"""
    
    total_conceptos_activos = serializers.IntegerField(read_only=True)
    total_cargos_pendientes = serializers.IntegerField(read_only=True)
    monto_total_pendiente = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total_cargos_vencidos = serializers.IntegerField(read_only=True)
    monto_total_vencido = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    total_pagos_mes_actual = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    conceptos_mas_aplicados = serializers.ListField(read_only=True)


class AlertaEstadoCuentaSerializer(serializers.Serializer):
    """Serializer para alertas en el estado de cuenta"""
    
    tipo = serializers.CharField(max_length=50, read_only=True)
    severidad = serializers.ChoiceField(choices=[('baja', 'Baja'), ('media', 'Media'), ('alta', 'Alta')], read_only=True)
    titulo = serializers.CharField(max_length=200, read_only=True)
    mensaje = serializers.CharField(max_length=500, read_only=True)
    accion = serializers.CharField(max_length=200, read_only=True)


class ProximoVencimientoSerializer(serializers.Serializer):
    """Serializer para información del próximo vencimiento"""
    
    cargo = CargoFinancieroListSerializer(read_only=True)
    fecha = serializers.DateField(read_only=True)
    dias_restantes = serializers.IntegerField(read_only=True)


class UltimoPagoSerializer(serializers.Serializer):
    """Serializer para información del último pago"""
    
    cargo = CargoFinancieroListSerializer(read_only=True)
    fecha = serializers.DateTimeField(read_only=True)
    hace_dias = serializers.IntegerField(read_only=True)


class DesgloseTipoSerializer(serializers.Serializer):
    """Serializer para desglose por tipo de concepto"""
    
    concepto__tipo = serializers.CharField(max_length=30, read_only=True)
    concepto__nombre = serializers.CharField(max_length=100, read_only=True)
    cantidad = serializers.IntegerField(read_only=True)
    total = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)


class ResumenGeneralSerializer(serializers.Serializer):
    """Serializer para el resumen general del estado de cuenta"""
    
    total_pendiente = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_vencido = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_al_dia = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    cantidad_cargos_pendientes = serializers.IntegerField(read_only=True)
    cantidad_cargos_vencidos = serializers.IntegerField(read_only=True)
    total_pagado_mes_actual = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_pagado_6_meses = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)


class EstadoCuentaSerializer(serializers.Serializer):
    """
    Serializer para el estado de cuenta completo
    T2: Consultar estado de cuenta - Módulo 2 Gestión Financiera Básica
    
    Proporciona una vista completa del estado financiero de un residente
    incluyendo cargos pendientes, vencidos, historial de pagos y alertas.
    """
    
    residente_info = ResidenteBasicoSerializer(read_only=True)
    fecha_consulta = serializers.DateField(read_only=True)
    resumen_general = ResumenGeneralSerializer(read_only=True)
    cargos_pendientes = CargoFinancieroListSerializer(many=True, read_only=True)
    cargos_vencidos = CargoFinancieroListSerializer(many=True, read_only=True)
    historial_pagos = CargoFinancieroListSerializer(many=True, read_only=True)
    desglose_por_tipo = DesgloseTipoSerializer(many=True, read_only=True)
    proximo_vencimiento = ProximoVencimientoSerializer(read_only=True)
    ultimo_pago = UltimoPagoSerializer(read_only=True)
    alertas = AlertaEstadoCuentaSerializer(many=True, read_only=True)
    
    class Meta:
        """Metadatos para documentación del serializer"""
        fields = [
            'residente_info', 'fecha_consulta', 'resumen_general',
            'cargos_pendientes', 'cargos_vencidos', 'historial_pagos',
            'desglose_por_tipo', 'proximo_vencimiento', 'ultimo_pago', 'alertas'
        ]