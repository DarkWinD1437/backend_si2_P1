#!/usr/bin/env python3
"""
Script de población de datos para el Módulo 2: Gestión Financiera
Crea conceptos y cargos de ejemplo para probar el sistema
"""

import os
import sys
import django
from datetime import date, timedelta
from decimal import Decimal

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
django.setup()

from django.contrib.auth import get_user_model
from backend.apps.finances.models import ConceptoFinanciero, CargoFinanciero, TipoConcepto, EstadoConcepto, EstadoCargo

User = get_user_model()

def poblar_conceptos_financieros():
    """Crear conceptos financieros de ejemplo"""
    print("📋 Creando conceptos financieros...")
    
    # Obtener usuario admin para crear los conceptos
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        admin_user = User.objects.filter(username='admin').first()
    
    if not admin_user:
        print("❌ No se encontró usuario administrador")
        return []
    
    conceptos_data = [
        {
            'nombre': 'Cuota de Mantenimiento Mensual',
            'descripcion': 'Cuota mensual para mantenimiento de áreas comunes, limpieza y servicios básicos',
            'tipo': TipoConcepto.CUOTA_MENSUAL,
            'monto': Decimal('180.00'),
            'es_recurrente': True,
            'aplica_a_todos': True,
            'fecha_vigencia_desde': date(2025, 1, 1),
            'fecha_vigencia_hasta': date(2025, 12, 31),
        },
        {
            'nombre': 'Cuota Extraordinaria - Remodelación Salón',
            'descripcion': 'Cuota extraordinaria para la remodelación del salón de eventos',
            'tipo': TipoConcepto.CUOTA_EXTRAORDINARIA,
            'monto': Decimal('250.00'),
            'es_recurrente': False,
            'aplica_a_todos': True,
            'fecha_vigencia_desde': date.today(),
            'fecha_vigencia_hasta': date.today() + timedelta(days=90),
        },
        {
            'nombre': 'Multa por Ruido Excesivo',
            'descripcion': 'Multa aplicada por generar ruido excesivo en horarios de descanso',
            'tipo': TipoConcepto.MULTA_RUIDO,
            'monto': Decimal('50.00'),
            'es_recurrente': False,
            'aplica_a_todos': False,
            'fecha_vigencia_desde': date.today(),
        },
        {
            'nombre': 'Multa por Mal Uso de Áreas Comunes',
            'descripcion': 'Multa por dejar basura o dañar áreas comunes',
            'tipo': TipoConcepto.MULTA_AREAS_COMUNES,
            'monto': Decimal('75.00'),
            'es_recurrente': False,
            'aplica_a_todos': False,
            'fecha_vigencia_desde': date.today(),
        },
        {
            'nombre': 'Multa por Estacionamiento Indebido',
            'descripcion': 'Multa por estacionar en lugares no autorizados o de visitantes',
            'tipo': TipoConcepto.MULTA_ESTACIONAMIENTO,
            'monto': Decimal('30.00'),
            'es_recurrente': False,
            'aplica_a_todos': False,
            'fecha_vigencia_desde': date.today(),
        },
        {
            'nombre': 'Multa por Mascota sin Correa',
            'descripcion': 'Multa por permitir que mascotas circulen sin correa en áreas comunes',
            'tipo': TipoConcepto.MULTA_MASCOTA,
            'monto': Decimal('25.00'),
            'es_recurrente': False,
            'aplica_a_todos': False,
            'fecha_vigencia_desde': date.today(),
        }
    ]
    
    conceptos_creados = []
    for concepto_data in conceptos_data:
        concepto, created = ConceptoFinanciero.objects.get_or_create(
            nombre=concepto_data['nombre'],
            defaults={**concepto_data, 'creado_por': admin_user}
        )
        if created:
            print(f"   ✅ {concepto.nombre} - ${concepto.monto}")
        else:
            print(f"   ⚠️  {concepto.nombre} ya existe")
        conceptos_creados.append(concepto)
    
    return conceptos_creados

def poblar_cargos_financieros(conceptos):
    """Crear cargos financieros de ejemplo"""
    print("\n💰 Aplicando cargos financieros...")
    
    # Obtener usuarios residentes
    residentes = User.objects.filter(role='resident').exclude(is_superuser=True)[:4]
    if not residentes:
        # Si no hay residentes con role, usar usuarios normales
        residentes = User.objects.filter(is_superuser=False)[:4]
    
    if not residentes:
        print("❌ No se encontraron usuarios residentes")
        return
    
    admin_user = User.objects.filter(is_superuser=True).first()
    if not admin_user:
        admin_user = User.objects.filter(username='admin').first()
    
    # Aplicar cuota mensual a todos los residentes
    cuota_mensual = next((c for c in conceptos if c.tipo == TipoConcepto.CUOTA_MENSUAL), None)
    if cuota_mensual:
        for residente in residentes:
            cargo, created = CargoFinanciero.objects.get_or_create(
                concepto=cuota_mensual,
                residente=residente,
                fecha_aplicacion=date.today(),
                defaults={
                    'monto': cuota_mensual.monto,
                    'fecha_vencimiento': date.today() + timedelta(days=30),
                    'observaciones': f'Cuota mensual aplicada automáticamente',
                    'aplicado_por': admin_user
                }
            )
            if created:
                print(f"   ✅ {cuota_mensual.nombre} aplicada a {residente.username} - ${cargo.monto}")
    
    # Aplicar cuota extraordinaria a algunos residentes
    cuota_extra = next((c for c in conceptos if c.tipo == TipoConcepto.CUOTA_EXTRAORDINARIA), None)
    if cuota_extra and len(residentes) >= 2:
        for residente in residentes[:2]:
            cargo, created = CargoFinanciero.objects.get_or_create(
                concepto=cuota_extra,
                residente=residente,
                fecha_aplicacion=date.today(),
                defaults={
                    'monto': cuota_extra.monto,
                    'fecha_vencimiento': date.today() + timedelta(days=60),
                    'observaciones': f'Cuota extraordinaria aplicada',
                    'aplicado_por': admin_user
                }
            )
            if created:
                print(f"   ✅ {cuota_extra.nombre} aplicada a {residente.username} - ${cargo.monto}")
    
    # Aplicar algunas multas
    multa_ruido = next((c for c in conceptos if c.tipo == TipoConcepto.MULTA_RUIDO), None)
    multa_estacionamiento = next((c for c in conceptos if c.tipo == TipoConcepto.MULTA_ESTACIONAMIENTO), None)
    
    if multa_ruido and len(residentes) >= 1:
        residente = residentes[0]
        cargo, created = CargoFinanciero.objects.get_or_create(
            concepto=multa_ruido,
            residente=residente,
            fecha_aplicacion=date.today() - timedelta(days=5),
            defaults={
                'monto': multa_ruido.monto,
                'fecha_vencimiento': date.today() + timedelta(days=15),
                'observaciones': f'Multa por ruido excesivo reportado por vecinos',
                'aplicado_por': admin_user
            }
        )
        if created:
            print(f"   ⚠️  {multa_ruido.nombre} aplicada a {residente.username} - ${cargo.monto}")
    
    if multa_estacionamiento and len(residentes) >= 2:
        residente = residentes[1]
        cargo, created = CargoFinanciero.objects.get_or_create(
            concepto=multa_estacionamiento,
            residente=residente,
            fecha_aplicacion=date.today() - timedelta(days=3),
            defaults={
                'monto': multa_estacionamiento.monto,
                'fecha_vencimiento': date.today() + timedelta(days=10),
                'observaciones': f'Multa por estacionar en lugar de visitantes',
                'aplicado_por': admin_user,
                'estado': EstadoCargo.VENCIDO  # Simular un cargo vencido
            }
        )
        if created:
            print(f"   ⚠️  {multa_estacionamiento.nombre} aplicada a {residente.username} - ${cargo.monto} (VENCIDO)")

def simular_algunos_pagos():
    """Simular algunos pagos para tener datos variados"""
    print("\n💳 Simulando algunos pagos...")
    
    # Marcar algunos cargos como pagados
    cargos_pendientes = CargoFinanciero.objects.filter(estado=EstadoCargo.PENDIENTE)[:2]
    
    for i, cargo in enumerate(cargos_pendientes):
        cargo.marcar_como_pagado(
            referencia_pago=f'PAGO-SIM-{date.today().strftime("%Y%m%d")}-{i+1:03d}',
            usuario_proceso=cargo.aplicado_por
        )
        cargo.observaciones += f"\n✅ Pago simulado el {date.today()}"
        cargo.save()
        print(f"   ✅ {cargo.concepto.nombre} pagado por {cargo.residente.username} - ${cargo.monto}")

def mostrar_resumen():
    """Mostrar resumen de datos creados"""
    print("\n" + "="*60)
    print("📊 RESUMEN DE DATOS CREADOS")
    print("="*60)
    
    total_conceptos = ConceptoFinanciero.objects.count()
    conceptos_activos = ConceptoFinanciero.objects.filter(estado=EstadoConcepto.ACTIVO).count()
    
    total_cargos = CargoFinanciero.objects.count()
    cargos_pendientes = CargoFinanciero.objects.filter(estado=EstadoCargo.PENDIENTE).count()
    cargos_pagados = CargoFinanciero.objects.filter(estado=EstadoCargo.PAGADO).count()
    cargos_vencidos = CargoFinanciero.objects.filter(estado=EstadoCargo.VENCIDO).count()
    
    monto_pendiente = CargoFinanciero.objects.filter(estado=EstadoCargo.PENDIENTE).aggregate(
        total=django.db.models.Sum('monto')
    )['total'] or Decimal('0.00')
    
    monto_pagado = CargoFinanciero.objects.filter(estado=EstadoCargo.PAGADO).aggregate(
        total=django.db.models.Sum('monto')
    )['total'] or Decimal('0.00')
    
    print(f"📋 CONCEPTOS FINANCIEROS:")
    print(f"   Total: {total_conceptos}")
    print(f"   Activos: {conceptos_activos}")
    print(f"\n💰 CARGOS FINANCIEROS:")
    print(f"   Total: {total_cargos}")
    print(f"   Pendientes: {cargos_pendientes} (${monto_pendiente})")
    print(f"   Pagados: {cargos_pagados} (${monto_pagado})")
    print(f"   Vencidos: {cargos_vencidos}")
    
    print(f"\n👥 RESIDENTES CON CARGOS:")
    residentes_con_cargos = User.objects.filter(cargos_financieros__isnull=False).distinct()
    for residente in residentes_con_cargos:
        total_cargos_residente = residente.cargos_financieros.count()
        total_pendiente_residente = residente.cargos_financieros.filter(
            estado=EstadoCargo.PENDIENTE
        ).aggregate(total=django.db.models.Sum('monto'))['total'] or Decimal('0.00')
        print(f"   {residente.username}: {total_cargos_residente} cargos, ${total_pendiente_residente} pendiente")
    
    print("\n✅ POBLACIÓN DE DATOS COMPLETADA")
    print("🚀 El módulo de finanzas está listo para pruebas")

def main():
    print("🏗️  POBLANDO MÓDULO 2: GESTIÓN FINANCIERA BÁSICA")
    print("="*60)
    
    try:
        conceptos = poblar_conceptos_financieros()
        poblar_cargos_financieros(conceptos)
        simular_algunos_pagos()
        mostrar_resumen()
    except Exception as e:
        print(f"❌ Error durante la población: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()