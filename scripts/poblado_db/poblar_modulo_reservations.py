#!/usr/bin/env python3
"""
Script para poblar datos del Módulo de Reservas de Áreas Comunes
"""

import os
import sys
import django
from datetime import time

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from backend.apps.reservations.models import AreaComun, HorarioDisponible, TipoAreaComun, EstadoAreaComun

def poblar_areas_comunes():
    """Poblar áreas comunes para pruebas"""

    areas_data = [
        {
            'nombre': 'Salón de Eventos',
            'descripcion': 'Amplio salón para eventos sociales',
            'tipo': TipoAreaComun.SALON_EVENTOS,
            'capacidad_maxima': 100,
            'costo_por_hora': 50.00,
            'costo_reserva': 0.00,
            'estado': EstadoAreaComun.ACTIVA,
            'requiere_aprobacion': False,
            'tiempo_minimo_reserva': 2,
            'tiempo_maximo_reserva': 8,
            'anticipo_minimo_horas': 24,
        },
        {
            'nombre': 'Piscina',
            'descripcion': 'Piscina climatizada con área de descanso',
            'tipo': TipoAreaComun.PISCINA,
            'capacidad_maxima': 30,
            'costo_por_hora': 20.00,
            'costo_reserva': 0.00,
            'estado': EstadoAreaComun.ACTIVA,
            'requiere_aprobacion': False,
            'tiempo_minimo_reserva': 1,
            'tiempo_maximo_reserva': 4,
            'anticipo_minimo_horas': 12,
        },
        {
            'nombre': 'Gimnasio',
            'descripcion': 'Gimnasio equipado con máquinas de última generación',
            'tipo': TipoAreaComun.GIMNASIO,
            'capacidad_maxima': 15,
            'costo_por_hora': 10.00,
            'costo_reserva': 0.00,
            'estado': EstadoAreaComun.ACTIVA,
            'requiere_aprobacion': False,
            'tiempo_minimo_reserva': 1,
            'tiempo_maximo_reserva': 3,
            'anticipo_minimo_horas': 6,
        },
        {
            'nombre': 'Cancha de Tenis',
            'descripcion': 'Cancha de tenis con superficie profesional',
            'tipo': TipoAreaComun.CANCHA_TENIS,
            'capacidad_maxima': 4,
            'costo_por_hora': 15.00,
            'costo_reserva': 5.00,
            'estado': EstadoAreaComun.ACTIVA,
            'requiere_aprobacion': False,
            'tiempo_minimo_reserva': 1,
            'tiempo_maximo_reserva': 2,
            'anticipo_minimo_horas': 12,
        },
        {
            'nombre': 'Sala de Juegos',
            'descripcion': 'Sala con mesa de billar, ping pong y juegos de mesa',
            'tipo': TipoAreaComun.OTROS,
            'capacidad_maxima': 20,
            'costo_por_hora': 8.00,
            'costo_reserva': 0.00,
            'estado': EstadoAreaComun.ACTIVA,
            'requiere_aprobacion': False,
            'tiempo_minimo_reserva': 1,
            'tiempo_maximo_reserva': 4,
            'anticipo_minimo_horas': 6,
        },
    ]

    areas_creadas = []
    for area_data in areas_data:
        area, created = AreaComun.objects.get_or_create(
            nombre=area_data['nombre'],
            defaults=area_data
        )
        if created:
            print(f"✅ Área creada: {area.nombre}")
        else:
            print(f"⚠️ Área ya existe: {area.nombre}")
        areas_creadas.append(area)

    return areas_creadas

def poblar_horarios_disponibles(areas):
    """Poblar horarios disponibles para las áreas"""

    dias_semana = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

    horarios_data = [
        # Lunes a Viernes
        {'hora_apertura': time(8, 0), 'hora_cierre': time(22, 0)},
        # Sábado
        {'hora_apertura': time(9, 0), 'hora_cierre': time(23, 0)},
        # Domingo
        {'hora_apertura': time(10, 0), 'hora_cierre': time(20, 0)},
    ]

    for area in areas:
        for dia in dias_semana:
            # Determinar horario según el día
            if dia in ['monday', 'tuesday', 'wednesday', 'thursday', 'friday']:
                horario = horarios_data[0]  # L-V
            elif dia == 'saturday':
                horario = horarios_data[1]  # Sábado
            else:
                horario = horarios_data[2]  # Domingo

            horario_obj, created = HorarioDisponible.objects.get_or_create(
                area_comun=area,
                dia_semana=dia,
                defaults={
                    'hora_apertura': horario['hora_apertura'],
                    'hora_cierre': horario['hora_cierre'],
                    'activo': True
                }
            )
            if created:
                print(f"✅ Horario creado: {area.nombre} - {dia}")

def main():
    """Función principal"""
    print("🏢 POBLANDO DATOS DEL MÓDULO DE RESERVAS")
    print("=" * 50)

    try:
        # Poblar áreas comunes
        print("\n🏛️ Poblando áreas comunes...")
        areas = poblar_areas_comunes()

        # Poblar horarios disponibles
        print("\n📅 Poblando horarios disponibles...")
        poblar_horarios_disponibles(areas)

        print("\n🎉 ¡DATOS DEL MÓDULO DE RESERVAS POBLADOS CORRECTAMENTE!")
        print(f"📊 Áreas comunes: {len(areas)}")
        print(f"📊 Horarios disponibles: {HorarioDisponible.objects.count()}")

    except Exception as e:
        print(f"❌ Error poblando datos: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()