#!/usr/bin/env python
"""
Script de debug para probar la creación de reservas directamente
"""

import os
import sys
import django
from datetime import datetime, timedelta

# Configurar Django
sys.path.append('c:\\Users\\PG\\Desktop\\Materias\\Sistemas de informacion 2\\Proyectos\\Parcial 1\\Backend_Django')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from backend.apps.reservations.models import AreaComun, Reserva, HorarioDisponible, EstadoReserva
from django.utils import timezone

User = get_user_model()

def debug_reserva():
    print("🔍 DEBUG: Probando creación de reserva directamente")
    print("=" * 60)

    # Obtener usuario residente
    try:
        residente = User.objects.get(username='prueba')
        print(f"✅ Usuario encontrado: {residente.username} (role: {residente.role})")
    except User.DoesNotExist:
        print("❌ Usuario 'prueba' no encontrado")
        return

    # Obtener primera área común
    try:
        area = AreaComun.objects.filter(estado='activa').first()
        if not area:
            print("❌ No hay áreas comunes activas")
            return
        print(f"✅ Área encontrada: {area.nombre} (ID: {area.id})")
    except Exception as e:
        print(f"❌ Error obteniendo área: {e}")
        return

    # Calcular fecha para mañana
    fecha_manana = (datetime.now() + timedelta(days=1)).date()
    print(f"📅 Fecha para reserva: {fecha_manana}")

    # Verificar horarios disponibles
    dia_semana = ['lunes', 'martes', 'miercoles', 'jueves', 'viernes', 'sabado', 'domingo'][fecha_manana.weekday()]
    print(f"📅 Día de la semana: {dia_semana}")

    try:
        horario = HorarioDisponible.objects.get(
            area_comun=area,
            dia_semana=dia_semana,
            activo=True
        )
        print(f"✅ Horario encontrado: {horario.hora_apertura} - {horario.hora_cierre}")
    except HorarioDisponible.DoesNotExist:
        print(f"❌ No hay horario disponible para {dia_semana}")
        return

    # Generar slots disponibles
    slots_disponibles = []
    hora_actual = horario.hora_apertura

    while hora_actual < horario.hora_cierre:
        hora_fin_slot = (datetime.combine(fecha_manana, hora_actual) + timedelta(hours=area.tiempo_minimo_reserva)).time()

        if hora_fin_slot <= horario.hora_cierre:
            disponible = area.esta_disponible_en_fecha(fecha_manana, hora_actual, hora_fin_slot)
            slots_disponibles.append({
                'hora_inicio': hora_actual,
                'hora_fin': hora_fin_slot,
                'disponible': disponible
            })

        hora_actual = (datetime.combine(fecha_manana, hora_actual) + timedelta(minutes=30)).time()

    print(f"📋 Slots generados: {len(slots_disponibles)}")
    disponibles = [s for s in slots_disponibles if s['disponible']]
    print(f"📋 Slots disponibles: {len(disponibles)}")

    if not disponibles:
        print("❌ No hay slots disponibles")
        return

    # Usar primer slot disponible
    slot = disponibles[0]
    hora_inicio = slot['hora_inicio']
    hora_fin = slot['hora_fin']

    print(f"🎯 Intentando reservar: {hora_inicio} - {hora_fin}")

    # Verificar disponibilidad nuevamente
    disponible = area.esta_disponible_en_fecha(fecha_manana, hora_inicio, hora_fin)
    print(f"🔍 Disponibilidad verificada: {disponible}")

    if not disponible:
        print("❌ El slot no está disponible")
        return

    # Verificar permisos
    puede_reservar = area.puede_reservar_usuario(residente)
    print(f"🔍 Usuario puede reservar: {puede_reservar}")

    if not puede_reservar:
        print("❌ Usuario no tiene permisos para reservar")
        return

    # Calcular duración y costo
    inicio = datetime.combine(fecha_manana, hora_inicio)
    fin = datetime.combine(fecha_manana, hora_fin)
    duracion = (fin - inicio).total_seconds() / 3600
    costo_total = area.calcular_costo_total(duracion)

    print(f"💰 Duración: {duracion} horas, Costo: ${costo_total}")

    # Intentar crear la reserva
    try:
        reserva = Reserva.objects.create(
            area_comun=area,
            usuario=residente,
            fecha=fecha_manana,
            hora_inicio=hora_inicio,
            hora_fin=hora_fin,
            duracion_horas=duracion,
            costo_total=costo_total,
            numero_personas=5,
            observaciones='Reserva de debug',
            estado=EstadoReserva.PENDIENTE if area.requiere_aprobacion else EstadoReserva.CONFIRMADA
        )
        print(f"✅ Reserva creada exitosamente! ID: {reserva.id}")
        print(f"   Estado: {reserva.estado}")
        print(f"   Costo: ${reserva.costo_total}")

    except Exception as e:
        print(f"❌ Error creando reserva: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_reserva()