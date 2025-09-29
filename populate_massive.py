"""
Script de población masiva para todos los endpoints del sistema Smart Condominium
Puebla aproximadamente 30+ casos por endpoint con datos realistas
"""

import os
import sys
import django
import random
from datetime import datetime, timedelta, date, time
from decimal import Decimal
from pathlib import Path

# Configurar Django
BASE_DIR = Path(__file__).parent.parent.parent
BACKEND_DIR = BASE_DIR / 'Backend_Django'
sys.path.insert(0, str(BACKEND_DIR))
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import transaction
from django.core.files.base import ContentFile

# Importar todos los modelos necesarios
from backend.apps.users.models import User
from backend.apps.finances.models import ConceptoFinanciero, CargoFinanciero
from backend.apps.communications.models import Aviso
from backend.apps.reservations.models import AreaComun, Reserva, HorarioDisponible
from backend.apps.analytics.models import (
    ReporteFinanciero, ReporteSeguridad, ReporteUsoAreas, PrediccionMorosidad
)
from backend.apps.maintenance.models import SolicitudMantenimiento, TareaMantenimiento
from backend.apps.modulo_notificaciones.models import (
    Dispositivo, PreferenciasNotificacion, Notificacion
)
from backend.apps.modulo_ia.models import (
    RostroRegistrado, VehiculoRegistrado, Acceso
)
from backend.apps.audit.models import RegistroAuditoria, SesionUsuario

User = get_user_model()


def populate_all_endpoints():
    """
    Función principal para poblar todos los endpoints del sistema
    """
    print("🚀 Iniciando población masiva de todos los endpoints...")
    print("=" * 80)

    try:
        with transaction.atomic():
            results = {}

            # 1. Usuarios (extender los existentes)
            print("👥 Poblando usuarios...")
            results['usuarios'] = populate_users()

            # 2. Finanzas
            print("💰 Poblando finanzas...")
            results['finanzas'] = populate_finances()

            # 3. Comunicaciones
            print("📢 Poblando comunicaciones...")
            results['comunicaciones'] = populate_communications()

            # 4. Reservas
            print("📅 Poblando reservas...")
            results['reservas'] = populate_reservations()

            # 5. Analytics
            print("📊 Poblando analytics...")
            results['analytics'] = populate_analytics()

            # 6. Mantenimiento
            print("🔧 Poblando mantenimiento...")
            results['mantenimiento'] = populate_maintenance()

            # 7. Notificaciones
            print("🔔 Poblando notificaciones...")
            results['notificaciones'] = populate_notifications()

            # 8. Módulo IA
            print("🤖 Poblando módulo IA...")
            results['modulo_ia'] = populate_ai_module()

            # 9. Auditoría
            print("📋 Poblando auditoría...")
            results['auditoria'] = populate_audit()

            # Resumen final
            print("\n" + "=" * 80)
            print("✅ POBLACIÓN COMPLETADA EXITOSAMENTE")
            print("=" * 80)

            total_records = 0
            for category, data in results.items():
                if isinstance(data, dict):
                    category_total = sum(data.values())
                    print(f"📁 {category.upper()}: {category_total} registros")
                    total_records += category_total
                else:
                    print(f"📁 {category.upper()}: {data} registros")
                    total_records += data

            print(f"\n🎯 TOTAL DE REGISTROS CREADOS: {total_records}")
            print("\n💡 El sistema Smart Condominium está completamente poblado y listo para pruebas!")

            return results

    except Exception as e:
        print(f"❌ Error durante la población: {e}")
        import traceback
        traceback.print_exc()
        return None


def populate_users():
    """Poblar usuarios adicionales (total: 50+ usuarios)"""
    # Datos para generar usuarios realistas
    first_names_male = [
        'Carlos', 'Juan', 'Diego', 'Miguel', 'Luis', 'Pedro', 'José', 'Daniel', 'David', 'Mario',
        'Roberto', 'Fernando', 'Eduardo', 'Andrés', 'Ricardo', 'Antonio', 'Francisco', 'Javier', 'Manuel', 'Alejandro',
        'Sergio', 'Rafael', 'Alberto', 'Adrián', 'Pablo', 'Rubén', 'Ángel', 'Jesús', 'Óscar', 'Iván'
    ]

    first_names_female = [
        'María', 'Ana', 'Carmen', 'Laura', 'Isabel', 'Patricia', 'Sofía', 'Lucía', 'Mónica', 'Elena',
        'Andrea', 'Claudia', 'Paola', 'Alejandra', 'Valentina', 'Gabriela', 'Natalia', 'Verónica', 'Cristina', 'Silvia',
        'Pilar', 'Teresa', 'Dolores', 'Celia', 'Rosa', 'Mercedes', 'Raquel', 'Beatriz', 'Julia', 'Victoria'
    ]

    last_names = [
        'García', 'Rodríguez', 'González', 'Hernández', 'López', 'Martínez', 'Pérez', 'Sánchez', 'Ramírez', 'Torres',
        'Flores', 'Gómez', 'Díaz', 'Morales', 'Jiménez', 'Muñoz', 'Álvarez', 'Romero', 'Herrera', 'Medina',
        'Castro', 'Vargas', 'Fernández', 'Guerrero', 'Mendoza', 'Ortiz', 'Delgado', 'Pena', 'Reyes', 'Cruz'
    ]

    addresses = [
        'Calle 123 #45-67', 'Carrera 89 #12-34', 'Avenida Principal #56-78', 'Diagonal 34 #90-12',
        'Transversal 67 #23-45', 'Circunvalar #89-01', 'Calle Real #45-67', 'Plaza Central #12-34'
    ]

    users_created = {'admin': 0, 'security': 0, 'resident': 0}

    # Crear administradores adicionales (total: 3)
    for i in range(2, 4):
        username = f'admin{i}'
        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(
                username=username,
                email=f'admin{i}@smartcondominium.com',
                password='admin123',
                first_name=f'Admin',
                last_name=f'Principal {i}',
                role='admin',
                phone=f'300123456{i}',
                address=random.choice(addresses)
            )
            users_created['admin'] += 1

    # Crear personal de seguridad adicional (total: 8)
    for i in range(6, 9):
        name = random.choice(first_names_male)
        last_name = random.choice(last_names)
        username = f'security{i}'
        if not User.objects.filter(username=username).exists():
            User.objects.create_user(
                username=username,
                email=f'security{i}@smartcondominium.com',
                password='security123',
                first_name=name,
                last_name=last_name,
                role='security',
                phone=f'301123456{i}',
                address=random.choice(addresses)
            )
            users_created['security'] += 1

    # Crear residentes adicionales (total: 60)
    for i in range(26, 61):
        # Alternar entre géneros
        if i % 2 == 0:
            first_name = random.choice(first_names_female)
        else:
            first_name = random.choice(first_names_male)

        last_name1 = random.choice(last_names)
        last_name2 = random.choice(last_names)
        username = f'resident{i:02d}'

        if not User.objects.filter(username=username).exists():
            User.objects.create_user(
                username=username,
                email=f'resident{i:02d}@smartcondominium.com',
                password='resident123',
                first_name=first_name,
                last_name=f'{last_name1} {last_name2}',
                role='resident',
                phone=f'31012345{i:02d}',
                address=random.choice(addresses)
            )
            users_created['resident'] += 1

    return users_created


def populate_finances():
    """Poblar conceptos financieros y cargos (30+ conceptos, 100+ cargos)"""
    concepts_created = 0
    charges_created = 0

    # Conceptos financieros
    conceptos_data = [
        # Cuotas mensuales
        {'nombre': 'Cuota Administración', 'tipo': 'cuota_mensual', 'monto_base': 180000.00, 'descripcion': 'Cuota mensual de administración'},
        {'nombre': 'Cuota Ascensor', 'tipo': 'cuota_mensual', 'monto_base': 25000.00, 'descripcion': 'Cuota mensual de ascensor'},
        {'nombre': 'Cuota Agua', 'tipo': 'cuota_mensual', 'monto_base': 35000.00, 'descripcion': 'Cuota mensual de agua'},
        {'nombre': 'Cuota Energía', 'tipo': 'cuota_mensual', 'monto_base': 45000.00, 'descripcion': 'Cuota mensual de energía'},
        {'nombre': 'Cuota Aseo', 'tipo': 'cuota_mensual', 'monto_base': 15000.00, 'descripcion': 'Cuota mensual de aseo'},
        {'nombre': 'Cuota Vigilancia', 'tipo': 'cuota_mensual', 'monto_base': 30000.00, 'descripcion': 'Cuota mensual de vigilancia'},

        # Multas
        {'nombre': 'Multa Ruido', 'tipo': 'multa', 'monto_base': 50000.00, 'descripcion': 'Multa por generar ruido excesivo'},
        {'nombre': 'Multa Mascotas', 'tipo': 'multa', 'monto_base': 100000.00, 'descripcion': 'Multa por no controlar mascotas'},
        {'nombre': 'Multa Estacionamiento', 'tipo': 'multa', 'monto_base': 75000.00, 'descripcion': 'Multa por estacionar en áreas no autorizadas'},
        {'nombre': 'Multa Basura', 'tipo': 'multa', 'monto_base': 25000.00, 'descripcion': 'Multa por mal manejo de basura'},

        # Servicios adicionales
        {'nombre': 'Servicio Internet', 'tipo': 'servicio_adicional', 'monto_base': 80000.00, 'descripcion': 'Servicio de internet comunitario'},
        {'nombre': 'Servicio Cable', 'tipo': 'servicio_adicional', 'monto_base': 60000.00, 'descripcion': 'Servicio de televisión por cable'},
        {'nombre': 'Servicio Portería', 'tipo': 'servicio_adicional', 'monto_base': 40000.00, 'descripcion': 'Servicio adicional de portería'},
        {'nombre': 'Servicio Lavandería', 'tipo': 'servicio_adicional', 'monto_base': 20000.00, 'descripcion': 'Servicio de lavandería comunitaria'},

        # Fondos especiales
        {'nombre': 'Fondo Pintura', 'tipo': 'fondo_especial', 'monto_base': 120000.00, 'descripcion': 'Fondo para pintura general'},
        {'nombre': 'Fondo Ascensor', 'tipo': 'fondo_especial', 'monto_base': 200000.00, 'descripcion': 'Fondo para mantenimiento de ascensor'},
        {'nombre': 'Fondo Jardinería', 'tipo': 'fondo_especial', 'monto_base': 80000.00, 'descripcion': 'Fondo para mantenimiento de jardines'},
        {'nombre': 'Fondo Seguridad', 'tipo': 'fondo_especial', 'monto_base': 150000.00, 'descripcion': 'Fondo para mejoras de seguridad'},

        # Otros conceptos
        {'nombre': 'Evento Social', 'tipo': 'evento', 'monto_base': 30000.00, 'descripcion': 'Contribución para eventos sociales'},
        {'nombre': 'Celebración Navidad', 'tipo': 'evento', 'monto_base': 50000.00, 'descripcion': 'Contribución para celebración navideña'},
        {'nombre': 'Mantenimiento General', 'tipo': 'mantenimiento', 'monto_base': 90000.00, 'descripcion': 'Mantenimiento general del edificio'},
        {'nombre': 'Reparación Techo', 'tipo': 'mantenimiento', 'monto_base': 300000.00, 'descripcion': 'Reparación del techo'},
        {'nombre': 'Instalación Cámaras', 'tipo': 'seguridad', 'monto_base': 500000.00, 'descripcion': 'Instalación de sistema de cámaras'},
        {'nombre': 'Actualización Ascensor', 'tipo': 'mantenimiento', 'monto_base': 800000.00, 'descripcion': 'Actualización del sistema de ascensor'},
        {'nombre': 'Renovación Fachada', 'tipo': 'mantenimiento', 'monto_base': 1200000.00, 'descripcion': 'Renovación completa de la fachada'},
        {'nombre': 'Sistema Solar', 'tipo': 'energia', 'monto_base': 1500000.00, 'descripcion': 'Instalación de sistema de energía solar'},
        {'nombre': 'Piscina Climatizada', 'tipo': 'mejora', 'monto_base': 2000000.00, 'descripcion': 'Construcción de piscina climatizada'},
        {'nombre': 'Gimnasio Equipado', 'tipo': 'mejora', 'monto_base': 1000000.00, 'descripcion': 'Equipamiento completo del gimnasio'},
        {'nombre': 'Sala de Juegos', 'tipo': 'mejora', 'monto_base': 800000.00, 'descripcion': 'Construcción de sala de juegos infantiles'},
        {'nombre': 'Área BBQ', 'tipo': 'mejora', 'monto_base': 400000.00, 'descripcion': 'Construcción de área de barbacoa'},
        {'nombre': 'Jardín Vertical', 'tipo': 'mejora', 'monto_base': 600000.00, 'descripcion': 'Instalación de jardín vertical'},
        {'nombre': 'Bicicletero', 'tipo': 'mejora', 'monto_base': 150000.00, 'descripcion': 'Instalación de bicicletero seguro'},
    ]

    for concepto_data in conceptos_data:
        # Obtener un admin para crear el concepto
        admin_user = User.objects.filter(role='admin').first()
        if not admin_user:
            # Si no hay admin, crear uno temporal
            admin_user = User.objects.create_superuser(
                username='temp_admin',
                email='temp@admin.com',
                password='temp123',
                first_name='Temp',
                last_name='Admin',
                role='admin'
            )

        concepto, created = ConceptoFinanciero.objects.get_or_create(
            nombre=concepto_data['nombre'],
            defaults={
                'descripcion': concepto_data['descripcion'],
                'tipo': concepto_data['tipo'],
                'monto': concepto_data['monto_base'],
                'estado': 'activo',
                'creado_por': admin_user,
                'es_recurrente': True if 'mensual' in concepto_data['tipo'] else False,
                'aplica_a_todos': True
            }
        )
        if created:
            concepts_created += 1

    # Crear cargos financieros (100+)
    residents = User.objects.filter(role='resident')
    conceptos = ConceptoFinanciero.objects.filter(estado='activo')

    for i in range(120):  # 120 cargos
        resident = random.choice(residents)
        concepto = random.choice(conceptos)

        # Fecha aleatoria en los últimos 12 meses
        months_ago = random.randint(0, 11)
        charge_date = datetime.now() - timedelta(days=30 * months_ago)

        # Algunos cargos ya pagados, otros pendientes
        is_paid = random.random() > 0.3  # 70% pagados

        # Monto con variación del 10%
        monto_variation = random.uniform(0.9, 1.1)
        monto = concepto.monto * Decimal(str(monto_variation))

        # Obtener admin para aplicar el cargo
        admin_user = User.objects.filter(role='admin').first()

        cargo = CargoFinanciero.objects.create(
            residente=resident,
            concepto=concepto,
            monto=monto,
            fecha_vencimiento=charge_date.date(),
            fecha_aplicacion=charge_date.date() - timedelta(days=random.randint(1, 15)),
            estado='pagado' if is_paid else 'pendiente',
            observaciones=f'Cargo generado automáticamente - Ref: {random.randint(100000, 999999)}',
            aplicado_por=admin_user
        )

        if is_paid:
            cargo.marcar_como_pagado(
                referencia_pago=f'REF{random.randint(1000000, 9999999)}',
                usuario_proceso=admin_user
            )

        charges_created += 1

    return {'conceptos': concepts_created, 'cargos': charges_created}


def populate_communications():
    """Poblar avisos de comunicaciones (30+ avisos)"""
    avisos_created = 0

    titulos_avisos = [
        'Mantenimiento programado de ascensores',
        'Nueva normativa de horarios de ruido',
        'Reunión extraordinaria de copropietarios',
        'Cambio en el servicio de recolección de basura',
        'Instalación de nuevas cámaras de seguridad',
        'Actualización del reglamento interno',
        'Suspensión temporal del servicio de agua',
        'Evento social: Día del Niño',
        'Campaña de reciclaje comunitaria',
        'Revisión anual de extintores',
        'Pintura general del edificio',
        'Instalación de sistema de energía solar',
        'Renovación de áreas verdes',
        'Actualización del gimnasio',
        'Nuevo servicio de lavandería',
        'Campaña de vacunación para mascotas',
        'Taller de primeros auxilios',
        'Celebración del aniversario del condominio',
        'Revisión de tuberías principales',
        'Instalación de nuevos contenedores de basura',
        'Actualización del sistema de iluminación',
        'Campaña de ahorro energético',
        'Nuevo proveedor de internet',
        'Revisión de la piscina comunitaria',
        'Taller de convivencia vecinal',
        'Campaña contra el dengue',
        'Instalación de portería electrónica',
        'Actualización del sistema de alarmas',
        'Campaña de adopción responsable',
        'Fiesta de fin de año',
        'Revisión anual de gasodomésticos',
        'Nuevo servicio de estacionamiento',
        'Campaña de limpieza comunitaria',
        'Taller de manualidades para niños',
        'Actualización del sistema de riego'
    ]

    prioridades = ['baja', 'media', 'alta']
    admins = User.objects.filter(role='admin')

    for titulo in titulos_avisos:
        # Crear aviso con datos aleatorios
        dias_publicacion = random.randint(-30, 30)  # Últimos 30 días o próximos 30
        fecha_publicacion = date.today() + timedelta(days=dias_publicacion)
        dias_duracion = random.randint(7, 90)  # Duración entre 1 semana y 3 meses
        fecha_vencimiento = fecha_publicacion + timedelta(days=dias_duracion)

        aviso = Aviso.objects.create(
            titulo=titulo,
            contenido=f"""Estimados residentes,

{titulo.lower()}. {'Este es un aviso importante que requiere su atención inmediata.' if random.random() > 0.7 else 'Le informamos sobre esta actualización en nuestros servicios.'}

Para más información, contacte a la administración.

Atentamente,
Administración del Condominio
""",
            prioridad=random.choice(prioridades),
            fecha_publicacion=fecha_publicacion,
            fecha_vencimiento=fecha_vencimiento,
            autor=random.choice(admins),
            estado='publicado' if random.random() > 0.2 else 'borrador',
            tipo_destinatario='todos',
            requiere_confirmacion=random.random() > 0.8  # 20% requieren confirmación
        )
        avisos_created += 1

    return avisos_created


def populate_reservations():
    """Poblar áreas comunes, reservas y horarios (10+ áreas, 50+ reservas, 100+ horarios)"""
    areas_created = 0
    reservations_created = 0
    schedules_created = 0

    # Áreas comunes
    areas_data = [
        {'nombre': 'Salón de Eventos Principal', 'tipo': 'salon_eventos', 'capacidad': 120, 'precio_hora': 75000.00, 'descripcion': 'Salón principal para eventos grandes'},
        {'nombre': 'Salón de Eventos Pequeño', 'tipo': 'salon_eventos', 'capacidad': 40, 'precio_hora': 35000.00, 'descripcion': 'Salón pequeño para reuniones'},
        {'nombre': 'Gimnasio Principal', 'tipo': 'gimnasio', 'capacidad': 25, 'precio_hora': 0.00, 'descripcion': 'Gimnasio completamente equipado'},
        {'nombre': 'Gimnasio al Aire Libre', 'tipo': 'gimnasio', 'capacidad': 15, 'precio_hora': 0.00, 'descripcion': 'Área de ejercicios al aire libre'},
        {'nombre': 'Piscina Adultos', 'tipo': 'piscina', 'capacidad': 30, 'precio_hora': 0.00, 'descripcion': 'Piscina para adultos'},
        {'nombre': 'Piscina Niños', 'tipo': 'piscina', 'capacidad': 20, 'precio_hora': 0.00, 'descripcion': 'Piscina para niños'},
        {'nombre': 'Cancha de Squash', 'tipo': 'deportiva', 'capacidad': 4, 'precio_hora': 25000.00, 'descripcion': 'Cancha de squash profesional'},
        {'nombre': 'Cancha de Tenis', 'tipo': 'deportiva', 'capacidad': 4, 'precio_hora': 30000.00, 'descripcion': 'Cancha de tenis con iluminación'},
        {'nombre': 'Área de BBQ 1', 'tipo': 'bbq', 'capacidad': 20, 'precio_hora': 40000.00, 'descripcion': 'Primera zona de barbacoa'},
        {'nombre': 'Área de BBQ 2', 'tipo': 'bbq', 'capacidad': 15, 'precio_hora': 35000.00, 'descripcion': 'Segunda zona de barbacoa'},
        {'nombre': 'Sala de Juegos', 'tipo': 'juegos', 'capacidad': 12, 'precio_hora': 15000.00, 'descripcion': 'Sala de juegos para niños'},
        {'nombre': 'Sala de Estudio', 'tipo': 'estudio', 'capacidad': 8, 'precio_hora': 0.00, 'descripcion': 'Sala para estudio y trabajo'},
        {'nombre': 'Terraza Comunitaria', 'tipo': 'terraza', 'capacidad': 50, 'precio_hora': 20000.00, 'descripcion': 'Terraza con vista panorámica'},
        {'nombre': 'Jardín Interior', 'tipo': 'jardin', 'capacidad': 25, 'precio_hora': 10000.00, 'descripcion': 'Jardín interior climatizado'},
    ]

    for area_data in areas_data:
        area, created = AreaComun.objects.get_or_create(
            nombre=area_data['nombre'],
            defaults={
                'descripcion': area_data['descripcion'],
                'tipo': area_data['tipo'],
                'capacidad_maxima': area_data['capacidad'],
                'costo_por_hora': area_data['precio_hora'],
                'estado': 'activa',
                'requiere_aprobacion': random.random() > 0.7,  # 30% requieren aprobación
                'tiempo_minimo_reserva': 1,
                'tiempo_maximo_reserva': random.randint(2, 8),
                'anticipo_minimo_horas': random.randint(2, 24)
            }
        )
        if created:
            areas_created += 1

    # Horarios disponibles (100+)
    areas = AreaComun.objects.all()
    days_of_week = ['monday', 'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday']

    for area in areas:
        for day in days_of_week:
            # Crear múltiples slots por día
            slots_per_day = random.randint(3, 8)
            for slot in range(slots_per_day):
                start_hour = random.randint(6, 20)  # 6 AM a 8 PM
                duration = random.randint(1, 4)  # 1-4 horas

                horario, created = HorarioDisponible.objects.get_or_create(
                    area_comun=area,
                    dia_semana=day,
                    defaults={
                        'hora_apertura': time(start_hour, 0),
                        'hora_cierre': time(min(start_hour + duration, 23), 0),
                        'activo': True
                    }
                )
                if created:
                    schedules_created += 1

    # Reservas (50+)
    residents = User.objects.filter(role='resident')
    areas_with_price = AreaComun.objects.filter(costo_por_hora__gt=0)

    for i in range(60):
        resident = random.choice(residents)
        area = random.choice(list(areas_with_price) + list(areas))  # Incluir áreas gratuitas también

        # Fecha aleatoria en próximos 60 días
        days_ahead = random.randint(1, 60)
        reservation_date = date.today() + timedelta(days=days_ahead)

        # Hora aleatoria
        start_hour = random.randint(8, 20)
        duration = random.randint(1, area.tiempo_maximo_reserva)

        reserva = Reserva.objects.create(
            usuario=resident,
            area_comun=area,
            fecha=reservation_date,
            hora_inicio=time(start_hour, 0),
            hora_fin=time(min(start_hour + duration, 23), 0),
            estado=random.choice(['pendiente', 'confirmada', 'cancelada', 'pagada']),
            observaciones=f'Reserva automática #{i+1}',
            numero_personas=random.randint(1, area.capacidad_maxima)
        )
        reservations_created += 1

    return {'areas': areas_created, 'reservas': reservations_created, 'horarios': schedules_created}


def populate_analytics():
    """Poblar reportes financieros, seguridad, uso áreas y predicciones (30+ cada tipo)"""
    reports_created = {'financieros': 0, 'seguridad': 0, 'uso_areas': 0, 'predicciones': 0}

    admins = User.objects.filter(role='admin')

    # Reportes Financieros (30+)
    tipos_financieros = ['ingresos', 'egresos', 'balance', 'estado_cuenta', 'morosidad', 'presupuesto']
    formatos = ['json', 'pdf', 'excel']

    for i in range(35):
        admin = random.choice(admins)
        tipo = random.choice(tipos_financieros)
        formato = random.choice(formatos)

        # Fechas aleatorias en últimos 6 meses
        months_ago = random.randint(0, 5)
        fecha_inicio = (datetime.now() - timedelta(days=30 * (months_ago + 1))).replace(day=1)
        fecha_fin = (datetime.now() - timedelta(days=30 * months_ago)).replace(day=1) - timedelta(days=1)

        reporte = ReporteFinanciero.objects.create(
            titulo=f'Reporte {tipo.title()} - {fecha_inicio.strftime("%B %Y")}',
            descripcion=f'Análisis detallado de {tipo} para el período {fecha_inicio.strftime("%B %Y")}',
            tipo=tipo,
            periodo='mensual',
            formato=formato,
            fecha_inicio=fecha_inicio.date(),
            fecha_fin=fecha_fin.date(),
            generado_por=admin,
            datos={
                'resumen': {
                    'total_ingresos': random.randint(15000000, 25000000),
                    'total_egresos': random.randint(12000000, 20000000),
                    'beneficio_neto': random.randint(2000000, 8000000),
                    'morosidad': random.uniform(2.0, 8.0)
                },
                'detalles': {
                    'pagos_pendientes': random.randint(500000, 2000000),
                    'pagos_vencidos': random.randint(200000, 1000000),
                    'reservas_pagadas': random.randint(20, 50)
                }
            },
            total_registros=random.randint(100, 500),
            filtros_aplicados={'periodo': 'mensual', 'tipo': tipo}
        )
        reports_created['financieros'] += 1

    # Reportes de Seguridad (30+)
    tipos_seguridad = ['accesos', 'incidentes', 'alertas', 'patrones', 'auditoria']

    for i in range(32):
        admin = random.choice(admins)
        tipo = random.choice(tipos_seguridad)

        # Fechas aleatorias
        days_ago = random.randint(1, 30)
        fecha_inicio = datetime.now() - timedelta(days=days_ago + 7)
        fecha_fin = datetime.now() - timedelta(days=days_ago)

        reporte = ReporteSeguridad.objects.create(
            titulo=f'Reporte de Seguridad: {tipo.title()}',
            descripcion=f'Análisis de eventos de seguridad - {tipo}',
            tipo=tipo,
            periodo='semanal',
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin,
            generado_por=admin,
            datos={
                'estadisticas': {
                    'total_eventos': random.randint(50, 200),
                    'eventos_criticos': random.randint(0, 10),
                    'alertas_generadas': random.randint(5, 25),
                    'accesos_autorizados': random.randint(500, 2000),
                    'accesos_denegados': random.randint(10, 50)
                },
                'incidentes': [
                    {'tipo': 'acceso_no_autorizado', 'cantidad': random.randint(1, 5)},
                    {'tipo': 'alerta_sospechosa', 'cantidad': random.randint(0, 3)},
                    {'tipo': 'mantenimiento_sistema', 'cantidad': random.randint(0, 2)}
                ]
            },
            total_eventos=random.randint(50, 200),
            eventos_criticos=random.randint(0, 10),
            alertas_generadas=random.randint(5, 25),
            filtros_aplicados={'tipo': tipo, 'periodo': 'semanal'}
        )
        reports_created['seguridad'] += 1

    # Reportes de Uso de Áreas (30+)
    areas_comunes = AreaComun.objects.all()
    metricas = ['ocupacion', 'reservas', 'tiempo_promedio', 'patrones_horarios', 'comparativo']
    areas_opciones = ['gimnasio', 'piscina', 'salon_eventos', 'estacionamiento', 'areas_verdes', 'todas']

    for i in range(33):
        admin = random.choice(admins)
        area = random.choice(areas_opciones)
        metrica = random.choice(metricas)

        # Fechas aleatorias
        months_ago = random.randint(0, 3)
        fecha_inicio = (datetime.now() - timedelta(days=30 * (months_ago + 1))).replace(day=1)
        fecha_fin = (datetime.now() - timedelta(days=30 * months_ago)).replace(day=1) - timedelta(days=1)

        reporte = ReporteUsoAreas.objects.create(
            titulo=f'Reporte de Uso: {area.title() if area != "todas" else "Todas las Áreas"}',
            descripcion=f'Análisis de uso de áreas comunes - Métrica: {metrica}',
            area=area,
            periodo='mensual',
            metrica_principal=metrica,
            fecha_inicio=fecha_inicio.date(),
            fecha_fin=fecha_fin.date(),
            generado_por=admin,
            datos={
                'estadisticas_uso': {
                    'total_reservas': random.randint(20, 100),
                    'horas_ocupacion': random.randint(100, 500),
                    'tasa_ocupacion_promedio': random.uniform(40.0, 90.0),
                    'reservas_canceladas': random.randint(1, 10),
                    'ingresos_generados': random.randint(500000, 3000000)
                },
                'patrones_horarios': {
                    'hora_pico_manana': '08:00-10:00',
                    'hora_pico_tarde': '18:00-20:00',
                    'dia_mas_activo': random.choice(['lunes', 'viernes', 'sabado'])
                }
            },
            total_reservas=random.randint(20, 100),
            horas_ocupacion=random.randint(100, 500),
            tasa_ocupacion_promedio=random.uniform(40.0, 90.0),
            filtros_aplicados={'area': area, 'metrica': metrica}
        )
        reports_created['uso_areas'] += 1

    # Predicciones de Morosidad (30+)
    modelos = ['regresion_logistica', 'random_forest', 'xgboost', 'red_neuronal', 'ensemble']

    for i in range(31):
        admin = random.choice(admins)
        modelo = random.choice(modelos)

        prediccion = PrediccionMorosidad.objects.create(
            titulo=f'Predicción de Morosidad #{i+1}',
            descripcion=f'Análisis predictivo usando modelo {modelo}',
            modelo_usado=modelo,
            nivel_confianza=random.choice(['bajo', 'medio', 'alto', 'muy_alto']),
            periodo_predicho=f'Próximos {random.randint(1, 6)} meses',
            generado_por=admin,
            datos_entrada={
                'residentes_analizados': random.randint(20, 60),
                'variables_consideradas': ['pagos_atrasados', 'ingresos', 'uso_servicios', 'tiempo_residencia'],
                'periodo_analisis': '12_meses'
            },
            resultados={
                'predicciones': {
                    'riesgo_bajo': random.randint(10, 30),
                    'riesgo_medio': random.randint(5, 15),
                    'riesgo_alto': random.randint(1, 8)
                },
                'factores_principales': [
                    'Historial de pagos',
                    'Cambios en ingresos',
                    'Uso de servicios adicionales'
                ]
            },
            total_residentes_analizados=random.randint(20, 60),
            residentes_riesgo_alto=random.randint(1, 8),
            residentes_riesgo_medio=random.randint(5, 15),
            precision_modelo=random.uniform(75.0, 95.0),
            parametros_modelo={
                'max_depth': random.randint(5, 15),
                'n_estimators': random.randint(50, 200),
                'learning_rate': random.uniform(0.01, 0.3)
            },
            metricas_evaluacion={
                'accuracy': random.uniform(0.75, 0.95),
                'precision': random.uniform(0.70, 0.90),
                'recall': random.uniform(0.65, 0.85),
                'f1_score': random.uniform(0.75, 0.92),
                'auc_roc': random.uniform(0.80, 0.96)
            }
        )
        reports_created['predicciones'] += 1

    return reports_created


def populate_maintenance():
    """Poblar solicitudes y tareas de mantenimiento (30+ solicitudes, 50+ tareas)"""
    requests_created = 0
    tasks_created = 0

    residents = User.objects.filter(role='resident')
    security_staff = User.objects.filter(role='security')

    # Tipos de solicitudes
    tipos_solicitud = [
        'eléctrica', 'plomeria', 'carpinteria', 'pintura', 'jardineria',
        'ascensor', 'seguridad', 'limpieza', 'mecanica', 'electronica'
    ]

    prioridades = ['baja', 'media', 'alta', 'urgente']

    # Solicitudes de mantenimiento (30+)
    for i in range(35):
        resident = random.choice(residents)
        tipo = random.choice(tipos_solicitud)
        prioridad = random.choice(prioridades)

        solicitud = SolicitudMantenimiento.objects.create(
            solicitante=resident,
            descripcion=f'Solicitud de mantenimiento: {tipo.title()}. Problema reportado por residente en unidad {random.randint(101, 160)}.',
            ubicacion=f'Unidad {random.randint(101, 160)} - {random.choice(["Interior", "Exterior", "Común"])}',
            prioridad=prioridad,
            estado=random.choice(['pendiente', 'asignada', 'en_progreso', 'completada', 'cancelada']),
            fecha_solicitud=datetime.now() - timedelta(days=random.randint(1, 30))
        )
        requests_created += 1

    # Tareas de mantenimiento (una por solicitud)
    solicitudes = SolicitudMantenimiento.objects.all()

    for solicitud in solicitudes:
        # Solo crear una tarea por solicitud si no existe
        asignado_a = random.choice(security_staff) if security_staff else None

        tarea, created = TareaMantenimiento.objects.get_or_create(
            solicitud=solicitud,
            defaults={
                'descripcion_tarea': f'Tarea asignada para solicitud #{solicitud.id}: {solicitud.descripcion[:50]}...',
                'asignado_a': asignado_a,
                'estado': random.choice(['pendiente', 'asignada', 'en_progreso', 'completada', 'cancelada']),
                'fecha_asignacion': datetime.now() - timedelta(days=random.randint(0, 15)),
                'notas': f'Tarea asignada automáticamente para solicitud de mantenimiento #{solicitud.id}'
            }
        )
        if created:
            tasks_created += 1

    return {'solicitudes': requests_created, 'tareas': tasks_created}


def populate_notifications():
    """Poblar dispositivos, preferencias y notificaciones (30+ dispositivos, 100+ notificaciones)"""
    devices_created = 0
    preferences_created = 0
    notifications_created = 0

    users = User.objects.all()

    # Dispositivos (30+)
    tipos_dispositivo = ['web', 'android', 'ios', 'flutter_web']

    for i in range(35):
        user = random.choice(users)
        tipo = random.choice(tipos_dispositivo)

        dispositivo = Dispositivo.objects.create(
            usuario=user,
            token_push=f'token_{random.randint(1000000000, 9999999999)}',
            tipo_dispositivo=tipo,
            nombre_dispositivo=f'Dispositivo {tipo.title()} #{i+1}',
            activo=random.random() > 0.2,  # 80% activos
            ultima_actividad=datetime.now() - timedelta(hours=random.randint(1, 168))  # Última semana
        )
        devices_created += 1

    # Preferencias de notificación (una por tipo por usuario)
    tipos_notificacion = [
        'acceso_permitido', 'acceso_denegado', 'nuevo_mensaje',
        'pago_realizado', 'pago_pendiente', 'mantenimiento',
        'emergencia', 'recordatorio'
    ]

    usuarios_activos = users.filter(is_active=True)
    for user in usuarios_activos:
        for tipo in tipos_notificacion:
            preferencias, created = PreferenciasNotificacion.objects.get_or_create(
                usuario=user,
                tipo_notificacion=tipo,
                defaults={
                    'push_enabled': random.random() > 0.3,  # 70% habilitadas
                    'email_enabled': random.random() > 0.7,  # 30% habilitadas
                    'sms_enabled': random.random() > 0.9     # 10% habilitadas
                }
            )
            if created:
                preferences_created += 1

    # Notificaciones (100+)
    tipos_notificacion = [
        'aviso_mantenimiento', 'alerta_seguridad', 'recordatorio_reserva',
        'aviso_financiero', 'evento_social', 'actualizacion_sistema',
        'recordatorio_pago', 'alerta_emergencia', 'noticia_condominio'
    ]

    prioridades = ['baja', 'media', 'alta', 'urgente']

    for i in range(120):
        user = random.choice(users)
        tipo = random.choice(tipos_notificacion)
        prioridad = random.randint(1, 5)  # Prioridad numérica 1-5

        # Determinar estado basado en lógica
        estado = random.choice(['pendiente', 'enviada', 'fallida', 'leida'])

        notificacion = Notificacion.objects.create(
            usuario=user,
            tipo=tipo,
            titulo=f'Notificación: {tipo.replace("_", " ").title()}',
            mensaje=f'Mensaje de notificación #{i+1} del tipo {tipo}.',
            prioridad=prioridad,
            estado=estado,
            fecha_envio=datetime.now() - timedelta(hours=random.randint(1, 720)) if estado in ['enviada', 'leida', 'fallida'] else None,
            fecha_lectura=datetime.now() - timedelta(hours=random.randint(0, 168)) if estado == 'leida' else None,
            push_enviado=random.random() > 0.3,
            email_enviado=random.random() > 0.2,
            sms_enviado=random.random() > 0.8,  # SMS menos frecuente
            datos_extra={
                'referencia': f'REF-{random.randint(10000, 99999)}',
                'categoria': tipo.split('_')[0],
                'accion_requerida': random.choice([None, 'revisar', 'confirmar', 'contactar_admin'])
            }
        )
        notifications_created += 1

    return {'dispositivos': devices_created, 'preferencias': preferences_created, 'notificaciones': notifications_created}


def populate_ai_module():
    """Poblar rostros, vehículos y accesos del módulo IA (30+ rostros, 20+ vehículos, 100+ accesos)"""
    faces_created = 0
    vehicles_created = 0
    accesses_created = 0

    residents = User.objects.filter(role='resident')

    # Rostros registrados (30+)
    for i in range(35):
        resident = random.choice(residents)

        rostro = RostroRegistrado.objects.create(
            usuario=resident,
            nombre_identificador=f'Rostro {resident.username} #{i+1}',
            imagen_rostro=f'rostro_{resident.username}_{i+1}.jpg',
            embedding_ia=[random.uniform(-1, 1) for _ in range(128)],  # Vector de 128 dimensiones
            activo=random.random() > 0.1,  # 90% activos
            confianza_minima=round(random.uniform(0.85, 0.98), 2)
        )
        faces_created += 1

    # Vehículos registrados (20+)
    marcas = ['Toyota', 'Honda', 'Nissan', 'Chevrolet', 'Mazda', 'Hyundai', 'Kia', 'Ford', 'BMW', 'Mercedes']
    colores = ['Blanco', 'Negro', 'Gris', 'Azul', 'Rojo', 'Plateado', 'Verde', 'Amarillo']

    for i in range(25):
        resident = random.choice(residents)

        # Generar placa válida (3-4 dígitos + 3 letras)
        num_digits = random.choice([3, 4])
        digits = ''.join(str(random.randint(0, 9)) for _ in range(num_digits))
        letters = ''.join(random.choice('ABCDEFGHIJKLMNOPQRSTUVWXYZ') for _ in range(3))
        placa = f'{digits}{letters}'

        vehiculo = VehiculoRegistrado.objects.create(
            usuario=resident,
            placa=placa,
            marca=random.choice(marcas),
            modelo=f'Modelo {random.randint(2015, 2024)}',
            color=random.choice(colores),
            descripcion=f'Vehículo registrado: {random.choice(["Principal", "Secundario", "De visita"])}',
            activo=random.random() > 0.05,  # 95% activos
        )
        vehicles_created += 1

    # Accesos (100+)
    rostros = RostroRegistrado.objects.filter(activo=True)
    vehiculos = VehiculoRegistrado.objects.filter(activo=True)
    tipos_acceso = ['facial', 'placa', 'manual', 'codigo']
    estados_acceso = ['permitido', 'denegado', 'pendiente']

    for i in range(150):
        tipo_acceso = random.choice(tipos_acceso)
        estado = random.choice(estados_acceso)

        # Determinar el objeto relacionado según el tipo
        usuario = None
        rostro = None
        vehiculo = None

        if tipo_acceso == 'facial' and rostros:
            rostro = random.choice(rostros)
            usuario = rostro.usuario
        elif tipo_acceso == 'placa' and vehiculos:
            vehiculo = random.choice(vehiculos)
            usuario = vehiculo.usuario
        else:
            usuario = random.choice(residents)

        acceso = Acceso.objects.create(
            usuario=usuario,
            tipo_acceso=tipo_acceso,
            estado=estado,
            ubicacion=random.choice(['Puerta Principal', 'Entrada Garage', 'Entrada Pedestal', 'Entrada Servicio']),
            rostro_detectado=rostro,
            vehiculo_detectado=vehiculo,
            confianza_ia=round(random.uniform(0.70, 0.99), 2) if random.random() > 0.2 else None,
            datos_ia={
                'temperatura': round(random.uniform(36.0, 37.5), 1) if random.random() > 0.3 else None,
                'hora_dia': random.choice(['mañana', 'tarde', 'noche']),
                'dia_semana': random.choice(['lunes', 'martes', 'miércoles', 'jueves', 'viernes', 'sábado', 'domingo'])
            } if random.random() > 0.4 else None,
            observaciones=f'Acceso #{i+1} - {tipo_acceso} - Estado: {estado}',
            autorizado_por=random.choice(residents) if estado == 'permitido' and random.random() > 0.5 else None
        )
        accesses_created += 1

    return {'rostros': faces_created, 'vehiculos': vehicles_created, 'accesos': accesses_created}


def populate_audit():
    """Poblar registros de auditoría y sesiones (100+ registros, 50+ sesiones)"""
    records_created = 0
    sessions_created = 0

    users = User.objects.all()
    acciones = [
        'login', 'logout', 'crear', 'actualizar', 'eliminar', 'ver', 'pago',
        'asignar_rol', 'cambiar_password', 'acceso_denegado', 'error_sistema',
        'exportar', 'importar', 'configurar'
    ]

    modulos = [
        'auth', 'finances', 'reservations', 'maintenance', 'communications',
        'security', 'notifications', 'analytics', 'audit', 'admin'
    ]

    # Registros de auditoría (100+)
    for i in range(120):
        user = random.choice(users)
        tipo_actividad = random.choice(acciones)
        modulo = random.choice(modulos)

        registro = RegistroAuditoria.objects.create(
            usuario=user,
            tipo_actividad=tipo_actividad,
            descripcion=f'{tipo_actividad.title().replace("_", " ")} en módulo {modulo} por {user.username}',
            nivel_importancia=random.choice(['bajo', 'medio', 'alto', 'critico']),
            timestamp=datetime.now() - timedelta(hours=random.randint(1, 720)),  # Último mes
            ip_address=f'192.168.1.{random.randint(1, 255)}',
            user_agent=f'Mozilla/5.0 ({random.choice(["Windows", "Mac", "Linux"])}; {random.choice(["Chrome", "Firefox", "Safari"])})',
            es_exitoso=random.random() > 0.05,  # 95% exitosos
            datos_adicionales={
                'endpoint': f'/api/{modulo}/{tipo_actividad}/',
                'method': random.choice(['GET', 'POST', 'PUT', 'DELETE']),
                'response_status': random.choice([200, 201, 400, 401, 403, 404, 500]),
                'processing_time_ms': random.randint(50, 2000),
                'session_id': f'session_{random.randint(1000000, 9999999)}',
                'location': f'{random.choice(["Oficina", "Casa", "Móvil"])} - {random.choice(["Bogotá", "Medellín", "Cali", "Barranquilla"])}'
            }
        )
        records_created += 1

    # Sesiones de usuario (50+)
    for i in range(60):
        user = random.choice(users)

        sesion = SesionUsuario.objects.create(
            usuario=user,
            token_session=f'session_{random.randint(1000000000, 9999999999)}',
            fecha_inicio=datetime.now() - timedelta(hours=random.randint(1, 168)),  # Última semana
            fecha_cierre=None if random.random() > 0.3 else datetime.now() - timedelta(hours=random.randint(0, 24)),
            ip_address=f'192.168.1.{random.randint(1, 255)}',
            user_agent=f'Mozilla/5.0 ({random.choice(["Windows NT 10.0", "Mac OS X 10_15", "Linux x86_64"])}; {random.choice(["Chrome/91", "Firefox/89", "Safari/14"])})',
            esta_activa=not random.random() > 0.7  # 30% activas
        )
        sessions_created += 1

    return {'registros': records_created, 'sesiones': sessions_created}


if __name__ == '__main__':
    try:
        populate_all_endpoints()
    except Exception as e:
        print(f"❌ Error durante la ejecución del script: {e}")
        import traceback
        traceback.print_exc()