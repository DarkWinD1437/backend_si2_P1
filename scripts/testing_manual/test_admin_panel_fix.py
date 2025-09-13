#!/usr/bin/env python
"""
Script para verificar que el error del admin panel está corregido
"""
import os
import sys
import django

# Configurar Django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from backend.apps.finances.models import CargoFinanciero, ConceptoFinanciero
from backend.apps.users.models import User

def test_admin_panel_fix():
    """
    Test para verificar que las propiedades del modelo funcionan 
    correctamente cuando fecha_vencimiento es None
    """
    print("🧪 Verificando corrección del error en admin panel...")
    
    try:
        # Crear un cargo con fecha_vencimiento None para simular el error
        print("\n✅ Creando cargo temporal con fecha_vencimiento = None...")
        
        # Obtener un concepto y usuario existente
        concepto = ConceptoFinanciero.objects.first()
        usuario = User.objects.filter(is_superuser=False).first()
        
        if not concepto or not usuario:
            print("❌ No hay conceptos o usuarios disponibles para la prueba")
            return False
        
        # Crear cargo temporal sin guardar en DB
        cargo_temp = CargoFinanciero(
            concepto=concepto,
            residente=usuario,
            monto=100.00,
            fecha_vencimiento=None  # Esto causaba el error
        )
        
        # Probar las propiedades que causaban el error
        print(f"✅ Probando propiedad 'esta_vencido': {cargo_temp.esta_vencido}")
        print(f"✅ Probando propiedad 'dias_para_vencimiento': {cargo_temp.dias_para_vencimiento}")
        
        # Si llegamos aquí sin errores, la corrección funciona
        print("\n🎉 ¡Corrección exitosa! Las propiedades manejan correctamente fecha_vencimiento = None")
        
        # Probar también con fecha válida
        from datetime import date, timedelta
        cargo_temp.fecha_vencimiento = date.today() + timedelta(days=5)
        print(f"✅ Con fecha válida - esta_vencido: {cargo_temp.esta_vencido}")
        print(f"✅ Con fecha válida - dias_para_vencimiento: {cargo_temp.dias_para_vencimiento}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        return False

def test_admin_panel_simulation():
    """
    Simular el comportamiento del admin panel
    """
    print("\n🏢 Simulando comportamiento del admin panel...")
    
    try:
        # Obtener un concepto y usuario
        concepto = ConceptoFinanciero.objects.first()
        usuario = User.objects.filter(is_superuser=False).first()
        
        if not concepto or not usuario:
            print("❌ No hay datos para la simulación")
            return False
        
        # Simular creación desde admin (formulario vacío inicialmente)
        print("✅ Simulando formulario vacío del admin panel...")
        
        cargo_vacio = CargoFinanciero()
        
        # Estas propiedades se evalúan cuando Django renderiza el admin
        print(f"✅ Propiedad 'esta_vencido' en formulario vacío: {cargo_vacio.esta_vencido}")
        print(f"✅ Propiedad 'dias_para_vencimiento' en formulario vacío: {cargo_vacio.dias_para_vencimiento}")
        
        print("\n🎉 ¡Admin panel funcionará correctamente!")
        return True
        
    except Exception as e:
        print(f"❌ Error en simulación del admin: {e}")
        return False

if __name__ == "__main__":
    print("🔧 VERIFICACIÓN DE CORRECCIÓN - ERROR ADMIN PANEL")
    print("=" * 50)
    
    success1 = test_admin_panel_fix()
    success2 = test_admin_panel_simulation()
    
    if success1 and success2:
        print("\n🎯 RESULTADO: ¡CORRECCIÓN EXITOSA!")
        print("✅ El admin panel ahora funcionará correctamente")
        print("✅ Las propiedades manejan correctamente valores None")
        print("✅ Puedes agregar cargos desde /admin/finances/cargofinanciero/add/")
    else:
        print("\n❌ RESULTADO: Aún hay problemas que resolver")