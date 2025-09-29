#!/usr/bin/env python
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from backend.apps.modulo_ia.models import RostroRegistrado

def verificar_rostros():
    print("=== VERIFICACIÓN DE ROSTROS REGISTRADOS ===")

    rostros = RostroRegistrado.objects.filter(activo=True)
    print(f"Total de rostros registrados activos: {rostros.count()}")

    if rostros.count() == 0:
        print("❌ No hay rostros registrados en el sistema")
        return

    for rostro in rostros:
        modelo = rostro.embedding_ia.get('modelo', 'Sin modelo') if rostro.embedding_ia else 'Sin embedding'
        confianza_min = getattr(rostro, 'confianza_minima', 'No definida')
        print(f"👤 {rostro.nombre_identificador}")
        print(f"   Usuario: {rostro.usuario.username}")
        print(f"   Modelo: {modelo}")
        print(f"   Confianza mínima: {confianza_min}")
        print(f"   Fecha registro: {rostro.fecha_registro}")
        print()

if __name__ == "__main__":
    verificar_rostros()