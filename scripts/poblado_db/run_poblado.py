"""
Script de poblado directo para modulo financiero
Ejecutar con: python scripts/poblado_db/run_poblado.py
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

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

def create_conceptos():
    print("Creando conceptos financieros...")
    
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        admin_user = User.objects.filter(username='admin').first()
    
    if not admin_user:
        print("Error: No hay usuario administrador")
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
        }
    ]
    
    created_conceptos = []
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
        created_conceptos.append(concepto)
        status = "Creado" if created else "Ya existe"
        print(f"  {status}: {concepto.nombre} - ${concepto.monto}")
    
    return created_conceptos

def create_cargos():
    print("\nCreando cargos para residentes...")
    
    # Obtener residentes
    residentes = User.objects.exclude(username__in=['admin', 'security']).exclude(is_superuser=True)[:3]
    
    if not residentes.exists():
        print("Error: No hay residentes")
        return
    
    admin_user = User.objects.filter(is_superuser=True).first()
    conceptos = ConceptoFinanciero.objects.filter(estado=EstadoConcepto.ACTIVO)
    
    if not admin_user or not conceptos.exists():
        print("Error: Faltan admin o conceptos")
        return
    
    hoy = date.today()
    cargos_creados = 0
    
    for residente in residentes:
        print(f"\n  Aplicando cargos a: {residente.username}")
        
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
                print(f"    Cuota mensual: ${cargo.monto} - Pendiente")
        
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
                print(f"    Cuota anterior: ${cargo_pagado.monto} - Pagada")
        
        # Multa ocasional (solo al primer residente)
        if residente == residentes.first():
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
                    print(f"    Multa: ${cargo_multa.monto} - Vencida")
    
    print(f"\n  Total cargos creados: {cargos_creados}")

def show_summary():
    print("\n" + "="*50)
    print("RESUMEN DEL POBLADO")
    print("="*50)
    
    conceptos_count = ConceptoFinanciero.objects.count()
    cargos_count = CargoFinanciero.objects.count()
    residentes_count = CargoFinanciero.objects.values('residente').distinct().count()
    
    pendientes = CargoFinanciero.objects.filter(estado=EstadoCargo.PENDIENTE).count()
    pagados = CargoFinanciero.objects.filter(estado=EstadoCargo.PAGADO).count()
    vencidos = CargoFinanciero.objects.filter(estado=EstadoCargo.VENCIDO).count()
    
    total_pendiente = CargoFinanciero.objects.filter(
        estado=EstadoCargo.PENDIENTE
    ).aggregate(total=Sum('monto'))['total'] or Decimal('0')
    
    print(f"Conceptos financieros: {conceptos_count}")
    print(f"Cargos totales: {cargos_count}")
    print(f"  - Pendientes: {pendientes}")
    print(f"  - Pagados: {pagados}")
    print(f"  - Vencidos: {vencidos}")
    print(f"Residentes con cargos: {residentes_count}")
    print(f"Total pendiente: ${total_pendiente}")
    
    print("\nEndpoints para probar:")
    print("  GET /api/finances/cargos/estado_cuenta/")
    print("  GET /api/finances/cargos/mis_cargos/")

def main():
    print("POBLANDO MODULO FINANCIERO")
    print("="*50)
    
    try:
        create_conceptos()
        create_cargos()
        show_summary()
        print("\nPOBLADO COMPLETADO EXITOSAMENTE!")
        
    except Exception as e:
        print(f"\nError: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()