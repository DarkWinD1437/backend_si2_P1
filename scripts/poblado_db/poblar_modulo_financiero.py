#!/usr/bin/env python
"""
Script para poblar el módulo financiero con datos de prueba
Módulo 2: Gestión Financiera Básica - T2: Consultar estado de cuenta

Este script crea:
- Conceptos financieros (cuotas y multas)
- Cargos aplicados a residentes
- Datos realistas para validar el endpoint de estado de cuenta

Ejecutar desde la raíz del proyecto Django:
python manage.py shell < scripts/poblado_db/poblar_modulo_financiero.py
"""

import os
import sys
import django
from decimal import Decimal
from datetime import date, timedelta
from django.utils import timezone

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from backend.apps.finances.models import (
    ConceptoFinanciero, CargoFinanciero, TipoConcepto, 
    EstadoConcepto, EstadoCargo
)

User = get_user_model()

def poblar_conceptos_financieros():
    """Crear conceptos financieros básicos"""
    print("📋 Creando conceptos financieros...")
    
    # Buscar un usuario admin
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        admin_user = User.objects.filter(username='admin').first()
    
    if not admin_user:
        print("❌ Error: No se encontró un usuario administrador")
        return
    
    conceptos = [
        {
            'nombre': 'Cuota de Mantenimiento Mensual',
            'descripcion': 'Cuota mensual para gastos de mantenimiento del condominio',
            'tipo': TipoConcepto.CUOTA_MENSUAL,
            'monto': Decimal('150000.00'),
            'es_recurrente': True,
            'aplica_a_todos': True,
            'fecha_vigencia_desde': date(2024, 1, 1)
        },
        {
            'nombre': 'Cuota Extraordinaria - Mejoras Área Social',
            'descripcion': 'Cuota extraordinaria para mejoras en áreas sociales',
            'tipo': TipoConcepto.CUOTA_EXTRAORDINARIA,
            'monto': Decimal('75000.00'),
            'es_recurrente': False,
            'aplica_a_todos': True,
            'fecha_vigencia_desde': date(2024, 10, 1),
            'fecha_vigencia_hasta': date(2024, 12, 31)
        },
        {
            'nombre': 'Multa por Ruido Nocturno',
            'descripcion': 'Multa aplicada por generar ruido después de las 10 PM',
            'tipo': TipoConcepto.MULTA_RUIDO,
            'monto': Decimal('50000.00'),
            'es_recurrente': False,
            'aplica_a_todos': False
        },
        {
            'nombre': 'Multa por Uso Indebido de Áreas Comunes',
            'descripcion': 'Multa por hacer uso inadecuado de áreas comunes',
            'tipo': TipoConcepto.MULTA_AREAS_COMUNES,
            'monto': Decimal('40000.00'),
            'es_recurrente': False,
            'aplica_a_todos': False
        },
        {
            'nombre': 'Multa por Parqueo en Lugar Prohibido',
            'descripcion': 'Multa por parquear en zonas no autorizadas',
            'tipo': TipoConcepto.MULTA_ESTACIONAMIENTO,
            'monto': Decimal('30000.00'),
            'es_recurrente': False,
            'aplica_a_todos': False
        },
        {
            'nombre': 'Multa por Mascota sin Registro',
            'descripcion': 'Multa por tener mascota sin registro en administración',
            'tipo': TipoConcepto.MULTA_MASCOTA,
            'monto': Decimal('25000.00'),
            'es_recurrente': False,
            'aplica_a_todos': False
        },
        {
            'nombre': 'Cuota por Reposición de Tarjeta de Acceso',
            'descripcion': 'Costo de reposición de tarjeta de acceso perdida o dañada',
            'tipo': TipoConcepto.OTROS,
            'monto': Decimal('15000.00'),
            'es_recurrente': False,
            'aplica_a_todos': False
        }
    ]
    
    conceptos_creados = []
    for concepto_data in conceptos:
        concepto, created = ConceptoFinanciero.objects.get_or_create(
            nombre=concepto_data['nombre'],
            defaults={
                **concepto_data,
                'creado_por': admin_user,
                'estado': EstadoConcepto.ACTIVO
            }
        )
        conceptos_creados.append(concepto)
        status = "✅ Creado" if created else "📝 Ya existe"
        print(f"   {status}: {concepto.nombre} - ${concepto.monto}")
    
    print(f"✅ {len(conceptos_creados)} conceptos financieros procesados")
    return conceptos_creados

def poblar_cargos_residentes():
    """Aplicar cargos a residentes existentes"""
    print("\n💰 Aplicando cargos a residentes...")
    
    # Obtener residentes
    residentes = User.objects.filter(
        role='resident'
    ).exclude(username__in=['admin', 'security'])[:5]  # Máximo 5 residentes
    
    if not residentes.exists():
        residentes = User.objects.exclude(
            username__in=['admin', 'security']
        )[:5]
    
    if not residentes.exists():
        print("❌ No se encontraron residentes para aplicar cargos")
        return
    
    # Obtener conceptos
    conceptos = ConceptoFinanciero.objects.filter(estado=EstadoConcepto.ACTIVO)
    admin_user = User.objects.filter(is_superuser=True).first() or User.objects.filter(username='admin').first()
    
    if not admin_user:
        print("❌ No se encontró usuario administrador")
        return
    
    cargos_creados = 0
    hoy = date.today()
    
    for residente in residentes:
        print(f"\n👤 Aplicando cargos a: {residente.username}")
        
        # 1. Cuotas mensuales (últimos 3 meses)
        cuota_mensual = conceptos.filter(tipo=TipoConcepto.CUOTA_MENSUAL).first()
        if cuota_mensual:
            for mes_atras in [3, 2, 1]:  # Últimos 3 meses
                fecha_aplicacion = hoy - timedelta(days=mes_atras * 30)
                fecha_vencimiento = fecha_aplicacion + timedelta(days=15)
                
                cargo, created = CargoFinanciero.objects.get_or_create(
                    concepto=cuota_mensual,
                    residente=residente,
                    fecha_aplicacion=fecha_aplicacion,
                    defaults={
                        'monto': cuota_mensual.monto,
                        'fecha_vencimiento': fecha_vencimiento,
                        'estado': EstadoCargo.PAGADO if mes_atras > 1 else EstadoCargo.PENDIENTE,
                        'aplicado_por': admin_user,
                        'observaciones': f'Cuota mensual {fecha_aplicacion.strftime("%B %Y")}'
                    }
                )
                
                # Simular pagos para meses anteriores
                if cargo.estado == EstadoCargo.PAGADO and not cargo.fecha_pago:
                    cargo.fecha_pago = timezone.make_aware(
                        timezone.datetime.combine(
                            fecha_vencimiento - timedelta(days=5),
                            timezone.datetime.now().time()
                        )
                    )
                    cargo.referencia_pago = f'TXN{cargo.id:06d}'
                    cargo.save()
                
                if created:
                    cargos_creados += 1
                    estado_desc = "💚 Pagado" if cargo.estado == EstadoCargo.PAGADO else "⏳ Pendiente"
                    print(f"   ✅ {cuota_mensual.nombre}: ${cargo.monto} - {estado_desc}")
        
        # 2. Cuota extraordinaria (si aplica)
        cuota_extra = conceptos.filter(tipo=TipoConcepto.CUOTA_EXTRAORDINARIA).first()
        if cuota_extra and cargos_creados % 2 == 0:  # Solo a algunos residentes
            cargo, created = CargoFinanciero.objects.get_or_create(
                concepto=cuota_extra,
                residente=residente,
                fecha_aplicacion=hoy - timedelta(days=45),
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
                print(f"   ✅ {cuota_extra.nombre}: ${cargo.monto} - ⏳ Pendiente")
        
        # 3. Multas ocasionales (solo a algunos residentes)
        multas = conceptos.filter(tipo__startswith='multa_')
        if len(residentes.filter(id__lte=residente.id)) % 3 == 0 and multas.exists():  # Solo 1 de cada 3
            multa = multas.order_by('?').first()  # Multa aleatoria
            
            cargo, created = CargoFinanciero.objects.get_or_create(
                concepto=multa,
                residente=residente,
                fecha_aplicacion=hoy - timedelta(days=20),
                defaults={
                    'monto': multa.monto,
                    'fecha_vencimiento': hoy - timedelta(days=5),  # Vencida
                    'estado': EstadoCargo.VENCIDO,
                    'aplicado_por': admin_user,
                    'observaciones': f'Infracción reportada por seguridad'
                }
            )
            if created:
                cargos_creados += 1
                print(f"   ⚠️ {multa.nombre}: ${cargo.monto} - 🔴 Vencido")
    
    print(f"\n✅ {cargos_creados} cargos aplicados exitosamente")

def poblar_historial_pagos():
    """Simular historial de pagos más extenso"""
    print("\n📊 Generando historial de pagos adicional...")
    
    # Obtener cargos pagados
    cargos_pagados = CargoFinanciero.objects.filter(estado=EstadoCargo.PAGADO)
    
    # Asegurar que tienen referencias de pago
    for cargo in cargos_pagados:
        if not cargo.referencia_pago:
            cargo.referencia_pago = f'PAY{cargo.id:06d}'
            cargo.save()
    
    print(f"✅ {cargos_pagados.count()} pagos en historial")

def mostrar_resumen():
    """Mostrar resumen del poblado"""
    print("\n" + "="*60)
    print("📊 RESUMEN DEL POBLADO DEL MÓDULO FINANCIERO")
    print("="*60)
    
    # Conceptos
    conceptos_por_tipo = ConceptoFinanciero.objects.values(
        'tipo'
    ).distinct().count()
    print(f"📋 Conceptos financieros: {ConceptoFinanciero.objects.count()} ({conceptos_por_tipo} tipos)")
    
    # Cargos por estado
    cargos_pendientes = CargoFinanciero.objects.filter(estado=EstadoCargo.PENDIENTE).count()
    cargos_pagados = CargoFinanciero.objects.filter(estado=EstadoCargo.PAGADO).count()
    cargos_vencidos = CargoFinanciero.objects.filter(estado=EstadoCargo.VENCIDO).count()
    
    print(f"💰 Cargos totales: {CargoFinanciero.objects.count()}")
    print(f"   - Pendientes: {cargos_pendientes}")
    print(f"   - Pagados: {cargos_pagados}")
    print(f"   - Vencidos: {cargos_vencidos}")
    
    # Residentes con cargos
    residentes_con_cargos = CargoFinanciero.objects.values('residente').distinct().count()
    print(f"👥 Residentes con cargos: {residentes_con_cargos}")
    
    # Montos
    total_pendiente = CargoFinanciero.objects.filter(
        estado=EstadoCargo.PENDIENTE
    ).aggregate(total=django.db.models.Sum('monto'))['total'] or 0
    
    total_pagado = CargoFinanciero.objects.filter(
        estado=EstadoCargo.PAGADO
    ).aggregate(total=django.db.models.Sum('monto'))['total'] or 0
    
    print(f"💵 Total pendiente: ${total_pendiente:,.2f}")
    print(f"💚 Total pagado: ${total_pagado:,.2f}")
    
    print("\n🎯 Endpoints para probar:")
    print("   GET /api/finances/cargos/estado_cuenta/")
    print("   GET /api/finances/cargos/estado_cuenta/?residente=USER_ID (admin)")
    print("   GET /api/finances/cargos/mis_cargos/")
    print("   GET /api/finances/conceptos/vigentes/")

def main():
    """Ejecutar poblado completo"""
    print("🚀 INICIANDO POBLADO DEL MÓDULO FINANCIERO")
    print("="*60)
    
    try:
        # 1. Crear conceptos financieros
        conceptos = poblar_conceptos_financieros()
        
        # 2. Aplicar cargos a residentes
        poblar_cargos_residentes()
        
        # 3. Generar historial de pagos
        poblar_historial_pagos()
        
        # 4. Mostrar resumen
        mostrar_resumen()
        
        print("\n✅ POBLADO COMPLETADO EXITOSAMENTE")
        
    except Exception as e:
        print(f"\n❌ ERROR DURANTE EL POBLADO: {str(e)}")
        import traceback
        traceback.print_exc()
        
    print("\n" + "="*60)

if __name__ == "__main__":
    main()