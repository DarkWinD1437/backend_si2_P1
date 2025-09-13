"""
Management command para poblar datos financieros
"""

from django.core.management.base import BaseCommand
from decimal import Decimal
from datetime import date, timedelta
from django.utils import timezone
from django.db.models import Sum
from django.contrib.auth import get_user_model
from backend.apps.finances.models import (
    ConceptoFinanciero, CargoFinanciero, TipoConcepto, 
    EstadoConcepto, EstadoCargo
)

User = get_user_model()

class Command(BaseCommand):
    help = 'Poblar módulo financiero con datos de prueba'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('🚀 POBLANDO MÓDULO FINANCIERO'))
        self.stdout.write('='*50)
        
        try:
            self.create_conceptos()
            self.create_cargos()
            self.show_summary()
            self.stdout.write(self.style.SUCCESS('\n✅ POBLADO COMPLETADO EXITOSAMENTE!'))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ Error: {str(e)}'))
            import traceback
            traceback.print_exc()

    def create_conceptos(self):
        self.stdout.write('📋 Creando conceptos financieros...')
        
        admin_user = User.objects.filter(is_superuser=True).first()
        if not admin_user:
            admin_user = User.objects.filter(username='admin').first()
        
        if not admin_user:
            self.stdout.write(self.style.ERROR('❌ No hay usuario administrador'))
            return []
        
        conceptos_data = [
            {
                'nombre': 'Cuota de Mantenimiento Mensual',
                'descripcion': 'Cuota mensual para gastos de mantenimiento del condominio',
                'tipo': TipoConcepto.CUOTA_MENSUAL,
                'monto': Decimal('150000.00'),
                'es_recurrente': True,
                'aplica_a_todos': True
            },
            {
                'nombre': 'Cuota Extraordinaria - Mejoras',
                'descripcion': 'Cuota extraordinaria para mejoras en areas sociales',
                'tipo': TipoConcepto.CUOTA_EXTRAORDINARIA,
                'monto': Decimal('75000.00'),
                'es_recurrente': False,
                'aplica_a_todos': True
            },
            {
                'nombre': 'Multa por Ruido Nocturno',
                'descripcion': 'Multa aplicada por generar ruido despues de las 10 PM',
                'tipo': TipoConcepto.MULTA_RUIDO,
                'monto': Decimal('50000.00'),
                'es_recurrente': False,
                'aplica_a_todos': False
            },
            {
                'nombre': 'Multa por Parqueo Prohibido',
                'descripcion': 'Multa por parquear en zonas no autorizadas',
                'tipo': TipoConcepto.MULTA_ESTACIONAMIENTO,
                'monto': Decimal('30000.00'),
                'es_recurrente': False,
                'aplica_a_todos': False
            },
            {
                'nombre': 'Multa por Mascota sin Registro',
                'descripcion': 'Multa por tener mascota sin registro',
                'tipo': TipoConcepto.MULTA_MASCOTA,
                'monto': Decimal('25000.00'),
                'es_recurrente': False,
                'aplica_a_todos': False
            }
        ]
        
        created_count = 0
        for data in conceptos_data:
            concepto, created = ConceptoFinanciero.objects.get_or_create(
                nombre=data['nombre'],
                defaults={
                    **data,
                    'creado_por': admin_user,
                    'estado': EstadoConcepto.ACTIVO,
                    'fecha_vigencia_desde': date.today()
                }
            )
            
            status = "✅ Creado" if created else "📝 Ya existe"
            self.stdout.write(f"   {status}: {concepto.nombre} - ${concepto.monto}")
            if created:
                created_count += 1
        
        self.stdout.write(f'✅ {created_count} conceptos nuevos creados')

    def create_cargos(self):
        self.stdout.write('\n💰 Creando cargos para residentes...')
        
        # Buscar residentes (excluyendo admin y security)
        residentes = User.objects.exclude(username__in=['admin', 'security']).exclude(is_superuser=True)[:4]
        
        if not residentes.exists():
            self.stdout.write(self.style.WARNING('⚠️ No hay residentes, usando cualquier usuario'))
            residentes = User.objects.all()[:3]
        
        admin_user = User.objects.filter(is_superuser=True).first() or User.objects.first()
        conceptos = ConceptoFinanciero.objects.filter(estado=EstadoConcepto.ACTIVO)
        
        if not conceptos.exists():
            self.stdout.write(self.style.ERROR('❌ No hay conceptos financieros'))
            return
        
        hoy = date.today()
        cargos_creados = 0
        
        for i, residente in enumerate(residentes):
            self.stdout.write(f'\n👤 Aplicando cargos a: {residente.username}')
            
            # Cuota mensual actual (pendiente)
            cuota_mensual = conceptos.filter(tipo=TipoConcepto.CUOTA_MENSUAL).first()
            if cuota_mensual:
                cargo, created = CargoFinanciero.objects.get_or_create(
                    concepto=cuota_mensual,
                    residente=residente,
                    fecha_aplicacion=hoy - timedelta(days=10),
                    defaults={
                        'monto': cuota_mensual.monto,
                        'fecha_vencimiento': hoy + timedelta(days=10),
                        'estado': EstadoCargo.PENDIENTE,
                        'aplicado_por': admin_user,
                        'observaciones': 'Cuota mensual actual'
                    }
                )
                if created:
                    cargos_creados += 1
                    self.stdout.write(f"   ✅ Cuota mensual: ${cargo.monto} - ⏳ Pendiente")
            
            # Cuota pagada anterior
            if cuota_mensual:
                cargo_pagado, created = CargoFinanciero.objects.get_or_create(
                    concepto=cuota_mensual,
                    residente=residente,
                    fecha_aplicacion=hoy - timedelta(days=40),
                    defaults={
                        'monto': cuota_mensual.monto,
                        'fecha_vencimiento': hoy - timedelta(days=25),
                        'estado': EstadoCargo.PAGADO,
                        'aplicado_por': admin_user,
                        'fecha_pago': timezone.now() - timedelta(days=28),
                        'referencia_pago': f'TXN{residente.id:03d}001',
                        'observaciones': 'Cuota mensual anterior'
                    }
                )
                if created:
                    cargos_creados += 1
                    self.stdout.write(f"   ✅ Cuota anterior: ${cargo_pagado.monto} - 💚 Pagada")
            
            # Cuota extraordinaria (solo a algunos)
            cuota_extra = conceptos.filter(tipo=TipoConcepto.CUOTA_EXTRAORDINARIA).first()
            if cuota_extra and i % 2 == 0:  # Solo a residentes pares
                cargo_extra, created = CargoFinanciero.objects.get_or_create(
                    concepto=cuota_extra,
                    residente=residente,
                    fecha_aplicacion=hoy - timedelta(days=20),
                    defaults={
                        'monto': cuota_extra.monto,
                        'fecha_vencimiento': hoy + timedelta(days=15),
                        'estado': EstadoCargo.PENDIENTE,
                        'aplicado_por': admin_user,
                        'observaciones': 'Cuota extraordinaria para mejoras'
                    }
                )
                if created:
                    cargos_creados += 1
                    self.stdout.write(f"   ✅ Cuota extra: ${cargo_extra.monto} - ⏳ Pendiente")
            
            # Multa (solo al primer residente)
            if i == 0:
                multa = conceptos.filter(tipo__startswith='multa_').first()
                if multa:
                    cargo_multa, created = CargoFinanciero.objects.get_or_create(
                        concepto=multa,
                        residente=residente,
                        fecha_aplicacion=hoy - timedelta(days=15),
                        defaults={
                            'monto': multa.monto,
                            'fecha_vencimiento': hoy - timedelta(days=2),  # Vencida
                            'estado': EstadoCargo.VENCIDO,
                            'aplicado_por': admin_user,
                            'observaciones': 'Infraccion reportada por seguridad'
                        }
                    )
                    if created:
                        cargos_creados += 1
                        self.stdout.write(f"   ⚠️ Multa: ${cargo_multa.monto} - 🔴 Vencida")
        
        self.stdout.write(f'\n✅ {cargos_creados} cargos nuevos creados')

    def show_summary(self):
        self.stdout.write('\n' + '='*60)
        self.stdout.write('📊 RESUMEN DEL POBLADO')
        self.stdout.write('='*60)
        
        conceptos_count = ConceptoFinanciero.objects.count()
        cargos_count = CargoFinanciero.objects.count()
        residentes_count = CargoFinanciero.objects.values('residente').distinct().count()
        
        pendientes = CargoFinanciero.objects.filter(estado=EstadoCargo.PENDIENTE).count()
        pagados = CargoFinanciero.objects.filter(estado=EstadoCargo.PAGADO).count()
        vencidos = CargoFinanciero.objects.filter(estado=EstadoCargo.VENCIDO).count()
        
        total_pendiente = CargoFinanciero.objects.filter(
            estado=EstadoCargo.PENDIENTE
        ).aggregate(total=Sum('monto'))['total'] or Decimal('0')
        
        total_pagado = CargoFinanciero.objects.filter(
            estado=EstadoCargo.PAGADO
        ).aggregate(total=Sum('monto'))['total'] or Decimal('0')
        
        self.stdout.write(f'📋 Conceptos financieros: {conceptos_count}')
        self.stdout.write(f'💰 Cargos totales: {cargos_count}')
        self.stdout.write(f'   - Pendientes: {pendientes}')
        self.stdout.write(f'   - Pagados: {pagados}')
        self.stdout.write(f'   - Vencidos: {vencidos}')
        self.stdout.write(f'👥 Residentes con cargos: {residentes_count}')
        self.stdout.write(f'💵 Total pendiente: ${total_pendiente}')
        self.stdout.write(f'💚 Total pagado: ${total_pagado}')
        
        self.stdout.write('\n🎯 Endpoints para probar:')
        self.stdout.write('   GET /api/finances/cargos/estado_cuenta/')
        self.stdout.write('   GET /api/finances/cargos/estado_cuenta/?residente=USER_ID (admin)')
        self.stdout.write('   GET /api/finances/cargos/mis_cargos/')
        self.stdout.write('   GET /api/finances/conceptos/vigentes/')