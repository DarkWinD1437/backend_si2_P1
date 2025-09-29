#!/usr/bin/env python3
"""
Script para debug del problema de rostros registrados en login facial
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(__file__))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from backend.apps.modulo_ia.models import RostroRegistrado

def debug_rostros_registrados():
    """Debug de rostros registrados"""
    print("🔍 DEBUG: Verificando rostros registrados en base de datos")
    print("=" * 60)

    try:
        # Consulta básica
        all_rostros = RostroRegistrado.objects.all()
        print(f"📊 Total de rostros en BD: {all_rostros.count()}")

        # Consulta filtrada como en el login
        rostros_activos = RostroRegistrado.objects.filter(activo=True)
        print(f"📊 Rostros activos: {rostros_activos.count()}")

        # Detalles de cada rostro
        for rostro in rostros_activos:
            print(f"\n  👤 {rostro.nombre_identificador}")
            print(f"     Usuario: {rostro.usuario.username}")
            print(f"     Activo: {rostro.activo}")
            print(f"     Embedding IA presente: {bool(rostro.embedding_ia)}")

            if rostro.embedding_ia:
                embedding_ia = rostro.embedding_ia
                modelo = embedding_ia.get('modelo', 'N/A')
                vector = embedding_ia.get('vector', [])
                confidence = embedding_ia.get('confidence', 'N/A')

                print(f"     Modelo: {modelo}")
                print(f"     Longitud vector: {len(vector) if vector else 0}")
                print(f"     Confianza: {confidence}")

                # Verificar si el vector es válido
                if vector and len(vector) == 128 and modelo == 'opencv_detected_opencv':
                    print("     ✅ Embedding válido")
                else:
                    print("     ❌ Embedding inválido")
            else:
                print("     ❌ Sin embedding IA")

        # Verificar si hay rostros con problemas
        rostros_sin_embedding = RostroRegistrado.objects.filter(activo=True, embedding_ia__isnull=True)
        print(f"\n⚠️  Rostros activos sin embedding: {rostros_sin_embedding.count()}")

        rostros_con_embedding_vacio = RostroRegistrado.objects.filter(activo=True, embedding_ia__vector__isnull=True)
        print(f"⚠️  Rostros activos con vector vacío: {rostros_con_embedding_vacio.count()}")

    except Exception as e:
        print(f"❌ Error en debug: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_rostros_registrados()