#!/usr/bin/env python
"""
Scri        print(f"Tipo actual: '{concepto.tipo}'")

        # Datos de prueba para actualizar
        update_data = {
            'nombre': concepto.nombre,
            'descripcion': 'Descripción de prueba actualizada',
            'tipo': 'cuota_mensual',  # Usar un tipo válido
            'monto': str(concepto.monto),
            'estado': concepto.estado,
            'fecha_vigencia_desde': concepto.fecha_vigencia_desde.isoformat(),
            'fecha_vigencia_hasta': concepto.fecha_vigencia_hasta.isoformat() if concepto.fecha_vigencia_hasta else None,
            'es_recurrente': concepto.es_recurrente,
            'aplica_a_todos': concepto.aplica_a_todos
        }ara verificar la API de conceptos financieros
"""
import os
import sys
import django
from django.conf import settings

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
django.setup()

from backend.apps.finances.models import ConceptoFinanciero
from backend.apps.finances.serializers import ConceptoFinancieroSerializer
from django.contrib.auth import get_user_model

User = get_user_model()

def test_concepto_update():
    """Prueba la actualización de un concepto financiero"""
    print("=== PRUEBA DE ACTUALIZACIÓN DE CONCEPTO FINANCIERO ===")

    # Obtener un concepto existente
    try:
        concepto = ConceptoFinanciero.objects.first()
        if not concepto:
            print("❌ No hay conceptos en la base de datos")
            return

        print(f"Concepto encontrado: {concepto.nombre}")
        print(f"Descripción actual: '{concepto.descripcion}'")
        print(f"Tipo actual: '{concepto.tipo}'")

        # Verificar opciones válidas del tipo
        from backend.apps.finances.models import TipoConcepto
        print(f"Opciones válidas de tipo: {list(TipoConcepto.choices)}")

        # Datos de prueba para actualizar
        update_data = {
            'nombre': concepto.nombre,
            'descripcion': 'Descripción de prueba actualizada',
            'tipo': 'otros',  # Usar un tipo válido
            'monto': str(concepto.monto),
            'estado': concepto.estado,
            'fecha_vigencia_desde': concepto.fecha_vigencia_desde.isoformat(),
            'fecha_vigencia_hasta': concepto.fecha_vigencia_hasta.isoformat() if concepto.fecha_vigencia_hasta else None,
            'es_recurrente': concepto.es_recurrente,
            'aplica_a_todos': concepto.aplica_a_todos
        }

        print(f"Datos a actualizar: {update_data}")

        # Crear serializer con datos de actualización
        serializer = ConceptoFinancieroSerializer(concepto, data=update_data, partial=True)
        if serializer.is_valid():
            print("✅ Serializer válido")
            concepto_actualizado = serializer.save()
            print(f"✅ Concepto actualizado exitosamente")
            print(f"Descripción nueva: '{concepto_actualizado.descripcion}'")

            # Verificar que se guardó en la base de datos
            concepto_verificado = ConceptoFinanciero.objects.get(id=concepto.id)
            print(f"Descripción en BD: '{concepto_verificado.descripcion}'")

            if concepto_verificado.descripcion == 'Descripción de prueba actualizada':
                print("✅ ¡La descripción se guardó correctamente!")
            else:
                print("❌ La descripción no se guardó correctamente")

        else:
            print("❌ Serializer inválido:")
            print(serializer.errors)

    except Exception as e:
        print(f"❌ Error durante la prueba: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_concepto_update()