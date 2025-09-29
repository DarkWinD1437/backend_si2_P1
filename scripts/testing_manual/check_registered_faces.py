#!/usr/bin/env python
"""
Script para consultar la información de rostros registrados
"""

import os
import sys
import django

# Configurar Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from backend.apps.modulo_ia.models import RostroRegistrado, Acceso

def main():
    print("🔍 CONSULTANDO INFORMACIÓN DE ROSTROS REGISTRADOS")
    print("=" * 60)

    # Consultar rostros
    rostros = RostroRegistrado.objects.filter(activo=True)
    print(f"\n📸 Total de rostros registrados activos: {rostros.count()}")

    for i, rostro in enumerate(rostros, 1):
        print(f"\n👤 Rostro #{i}")
        print(f"   ID: {rostro.id}")
        print(f"   Usuario: {rostro.usuario.username} ({rostro.usuario.get_full_name()})")
        print(f"   Nombre identificador: {rostro.nombre_identificador}")
        print(f"   Confianza mínima: {rostro.confianza_minima}")
        print(f"   Fecha registro: {rostro.fecha_registro}")
        print(f"   Activo: {rostro.activo}")

        if rostro.embedding_ia:
            print("   🤖 Embedding IA guardado: Sí")
            if isinstance(rostro.embedding_ia, dict):
                modelo = rostro.embedding_ia.get('modelo', 'N/A')
                timestamp = rostro.embedding_ia.get('timestamp', 'N/A')
                confidence = rostro.embedding_ia.get('confidence', 'N/A')
                description = rostro.embedding_ia.get('description', 'N/A')
                print(f"      Modelo: {modelo}")
                print(f"      Timestamp: {timestamp}")
                print(f"      Confianza: {confidence}")
                print(f"      Descripción: {description}")

                if 'vector' in rostro.embedding_ia:
                    vector = rostro.embedding_ia['vector']
                    if isinstance(vector, list):
                        print(f"      Vector: {len(vector)} dimensiones")
                    else:
                        print(f"      Vector: {type(vector)}")
        else:
            print("   ❌ No hay embedding IA guardado")

    # Consultar accesos recientes
    print(f"\n🔐 HISTORIAL DE ACCESOS RECIENTES")
    accesos = Acceso.objects.all().order_by('-fecha_hora')[:10]  # Últimos 10

    for acceso in accesos:
        print(f"\n⏰ {acceso.fecha_hora}")
        print(f"   Tipo: {acceso.tipo_acceso}")
        print(f"   Estado: {acceso.estado}")
        print(f"   Ubicación: {acceso.ubicacion}")
        if acceso.usuario:
            print(f"   Usuario: {acceso.usuario.username}")
        if acceso.confianza_ia is not None:
            print(f"   Confianza IA: {acceso.confianza_ia}")
        if acceso.observaciones:
            print(f"   Observaciones: {acceso.observaciones}")

if __name__ == '__main__':
    main()