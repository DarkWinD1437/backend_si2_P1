#!/usr/bin/env python3
"""
Script MEJORADO para poblar la base de datos Smart Condominium
Maneja duplicados y verifica datos existentes

Ejecutar desde el directorio del proyecto Django:
python poblar_db_mejorado.py
"""

import os
import sys
import django
from pathlib import Path

# Configurar Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.db import connection, transaction
from datetime import datetime

def verificar_tabla_existe(tabla):
    """Verificar si una tabla existe"""
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT COUNT(*) FROM {tabla} LIMIT 1")
            return True
    except:
        return False

def contar_registros(tabla):
    """Contar registros en una tabla"""
    try:
        with connection.cursor() as cursor:
            cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
            return cursor.fetchone()[0]
    except:
        return 0

def ejecutar_sql_seguro(sql_statement, descripcion="", ignorar_duplicados=True):
    """Ejecutar una declaración SQL de forma segura"""
    print(f"  🔸 {descripcion}")
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql_statement)
            affected_rows = cursor.rowcount
            print(f"    ✅ Ejecutado exitosamente - {affected_rows} filas afectadas")
            return affected_rows
    except Exception as e:
        error_msg = str(e)
        if "duplicate" in error_msg.lower() or "duplicada" in error_msg.lower() or "unique" in error_msg.lower():
            if ignorar_duplicados:
                print(f"    ⚠️ Datos ya existen (ignorado): {error_msg[:60]}...")
                return 0
            else:
                print(f"    ❌ Error de duplicado: {error_msg[:60]}...")
                return 0
        else:
            print(f"    ❌ Error: {error_msg[:100]}...")
            raise e

def limpiar_tabla_si_existe(tabla):
    """Limpiar una tabla si existe y tiene datos"""
    if verificar_tabla_existe(tabla):
        count = contar_registros(tabla)
        if count > 0:
            print(f"  🧹 Limpiando tabla {tabla} ({count} registros)...")
            try:
                with connection.cursor() as cursor:
                    cursor.execute(f"DELETE FROM {tabla}")
                    print(f"    ✅ Tabla {tabla} limpiada")
                    return True
            except Exception as e:
                print(f"    ⚠️ No se pudo limpiar {tabla}: {str(e)[:50]}...")
                return False
        else:
            print(f"  ✅ Tabla {tabla} ya está vacía")
            return True
    return False

def mostrar_estado_base_datos():
    """Mostrar el estado actual de las tablas principales"""
    print("\n📊 ESTADO ACTUAL DE LA BASE DE DATOS:")
    print("=" * 50)
    
    tablas_principales = [
        'rol', 'usuario', 'usuario_rol', 'area_comun', 'zona', 
        'camara', 'tipo_evento', 'vehiculo_autorizado', 
        'unidad_habitacional', 'reserva', 'cuota', 'pago', 
        'aviso', 'evento_seguridad', 'mantenimiento', 'reporte'
    ]
    
    total_registros = 0
    for tabla in tablas_principales:
        if verificar_tabla_existe(tabla):
            count = contar_registros(tabla)
            total_registros += count
            status = "✅" if count > 0 else "🔹"
            print(f"  {status} {tabla}: {count} registros")
        else:
            print(f"  ❌ {tabla}: tabla no existe")
    
    print("=" * 50)
    print(f"📈 Total de registros: {total_registros}")
    return total_registros

def poblar_base_datos_mejorado(limpiar_antes=False):
    """Función principal mejorada para poblar la base de datos COMPLETA"""
    print("🚀 Iniciando poblado MEJORADO de Smart Condominium...")
    print(f"📅 Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    # Mostrar estado inicial
    registros_iniciales = mostrar_estado_base_datos()
    
    if registros_iniciales > 0:
        print(f"\n⚠️ ATENCIÓN: La base de datos ya tiene {registros_iniciales} registros")
        if limpiar_antes:
            print("🧹 Procediendo a limpiar tablas...")
            limpiar_tablas()
        else:
            print("💡 Continuando con inserción (ignorando duplicados)...")
    
    print("\n" + "=" * 60)
    
    total_registros = 0
    
    try:
        with connection.cursor() as cursor:
            
            # 1. ROLES
            print("👥 Poblando ROLES...")
            sql_roles = """
            INSERT INTO rol (nombre, descripcion) VALUES
            ('Administrador', 'Administrador del sistema con todos los permisos'),
            ('Propietario', 'Propietario de una unidad habitacional'),
            ('Inquilino', 'Persona que habita una unidad habitacional'),
            ('Seguridad', 'Personal de seguridad del condominio'),
            ('Conserje', 'Personal de conserjería y atención a residentes'),
            ('Mantenimiento', 'Personal de mantenimiento del condominio')
            ON CONFLICT (nombre) DO NOTHING;
            """
            total_registros += ejecutar_sql_seguro(sql_roles, "Insertando 6 roles del sistema")
            
            # 2. USUARIOS COMPLETOS (20 usuarios)
            print("\n� Poblando USUARIOS COMPLETOS...")
            sql_admin = """
            INSERT INTO usuario (nombre, email, password, telefono, tipo, activo) VALUES
            ('Administrador Principal', 'admin@smartcondominium.com', crypt('admin123', gen_salt('bf')), '+1234567890', 'administrador', TRUE)
            ON CONFLICT (email) DO NOTHING;
            """
            total_registros += ejecutar_sql_seguro(sql_admin, "Usuario administrador principal")
            
            sql_usuarios = """
            INSERT INTO usuario (nombre, email, password, telefono, tipo, activo) VALUES
            ('Carlos Rodríguez', 'carlos.rodriguez@email.com', crypt('password123', gen_salt('bf')), '+1234567891', 'propietario', TRUE),
            ('María González', 'maria.gonzalez@email.com', crypt('password123', gen_salt('bf')), '+1234567892', 'propietario', TRUE),
            ('Juan Pérez', 'juan.perez@email.com', crypt('password123', gen_salt('bf')), '+1234567893', 'propietario', TRUE),
            ('Ana Martínez', 'ana.martinez@email.com', crypt('password123', gen_salt('bf')), '+1234567894', 'propietario', TRUE),
            ('Luis Sánchez', 'luis.sanchez@email.com', crypt('password123', gen_salt('bf')), '+1234567895', 'propietario', TRUE),
            ('Laura López', 'laura.lopez@email.com', crypt('password123', gen_salt('bf')), '+1234567896', 'inquilino', TRUE),
            ('Pedro García', 'pedro.garcia@email.com', crypt('password123', gen_salt('bf')), '+1234567897', 'inquilino', TRUE),
            ('Sofía Hernández', 'sofia.hernandez@email.com', crypt('password123', gen_salt('bf')), '+1234567898', 'inquilino', TRUE),
            ('Diego Torres', 'diego.torres@email.com', crypt('password123', gen_salt('bf')), '+1234567899', 'inquilino', TRUE),
            ('Elena Ramírez', 'elena.ramirez@email.com', crypt('password123', gen_salt('bf')), '+1234567800', 'inquilino', TRUE),
            ('Jorge Flores', 'jorge.flores@email.com', crypt('password123', gen_salt('bf')), '+1234567801', 'seguridad', TRUE),
            ('Mónica Díaz', 'monica.diaz@email.com', crypt('password123', gen_salt('bf')), '+1234567802', 'seguridad', TRUE),
            ('Ricardo Vargas', 'ricardo.vargas@email.com', crypt('password123', gen_salt('bf')), '+1234567803', 'conserje', TRUE),
            ('Isabel Castro', 'isabel.castro@email.com', crypt('password123', gen_salt('bf')), '+1234567804', 'conserje', TRUE),
            ('Fernando Ruiz', 'fernando.ruiz@email.com', crypt('password123', gen_salt('bf')), '+1234567805', 'mantenimiento', TRUE),
            ('Gabriela Morales', 'gabriela.morales@email.com', crypt('password123', gen_salt('bf')), '+1234567806', 'mantenimiento', TRUE),
            ('Roberto Silva', 'roberto.silva@email.com', crypt('password123', gen_salt('bf')), '+1234567807', 'administrador', TRUE),
            ('Carmen Ortega', 'carmen.ortega@email.com', crypt('password123', gen_salt('bf')), '+1234567808', 'propietario', TRUE),
            ('Miguel Mendoza', 'miguel.mendoza@email.com', crypt('password123', gen_salt('bf')), '+1234567809', 'propietario', TRUE)
            ON CONFLICT (email) DO NOTHING;
            """
            total_registros += ejecutar_sql_seguro(sql_usuarios, "Insertando 19 usuarios completos")
            
            # 3. ASIGNACIÓN DE ROLES
            print("\n🔗 Asignando ROLES A USUARIOS...")
            sql_roles_usuarios = """
            INSERT INTO usuario_rol (id_usuario, id_rol) VALUES
            (1, 1), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2), (7, 3), (8, 3), (9, 3), (10, 3),
            (11, 3), (12, 4), (13, 4), (14, 5), (15, 5), (16, 6), (17, 6), (18, 1), (19, 2), (20, 2)
            ON CONFLICT DO NOTHING;
            """
            total_registros += ejecutar_sql_seguro(sql_roles_usuarios, "Asignando roles a usuarios")
            
            # 4. ÁREAS COMUNES COMPLETAS
            print("\n🏛️ Poblando ÁREAS COMUNES COMPLETAS...")
            sql_areas = """
            INSERT INTO area_comun (nombre, descripcion, capacidad, precio_hora, horario_disponible, activa) VALUES
            ('Salón de Eventos', 'Amplio salón para eventos sociales', 100, 50.00, '08:00-22:00', TRUE),
            ('Piscina', 'Piscina climatizada con área de descanso', 30, 20.00, '07:00-20:00', TRUE),
            ('Gimnasio', 'Gimnasio equipado con máquinas de última generación', 15, 10.00, '05:00-23:00', TRUE),
            ('Cancha de Tenis', 'Cancha de tenis con superficie profesional', 4, 15.00, '07:00-21:00', TRUE),
            ('Sala de Juegos', 'Sala con mesa de billar, ping pong y juegos de mesa', 20, 8.00, '09:00-22:00', TRUE),
            ('Jardín Interior', 'Espacio verde con áreas para picnic', 40, 5.00, '06:00-20:00', TRUE),
            ('Terraza', 'Terraza con vista panorámica y asadores', 25, 25.00, '10:00-23:00', TRUE),
            ('Salón de Reuniones', 'Espacio profesional para reuniones de trabajo', 12, 30.00, '07:00-21:00', TRUE),
            ('Biblioteca', 'Espacio tranquilo con colección de libros', 15, 0.00, '08:00-20:00', TRUE),
            ('Cine en Casa', 'Sala con equipo de proyección y sonido', 10, 35.00, '14:00-23:00', TRUE)
            ON CONFLICT (nombre) DO NOTHING;
            """
            total_registros += ejecutar_sql_seguro(sql_areas, "Insertando 10 áreas comunes")
            
            # 5. ZONAS
            print("\n📍 Poblando ZONAS...")
            sql_zonas = """
            INSERT INTO zona (id_areaComun, nombre, tipo) VALUES
            (1, 'Área Principal', 'Salón'),
            (1, 'Cocina Annex', 'Cocina'),
            (2, 'Piscina Principal', 'Piscina'),
            (2, 'Área de Descanso', 'Descanso'),
            (3, 'Zona Cardio', 'Gimnasio'),
            (3, 'Zona Pesas', 'Gimnasio'),
            (4, 'Cancha Norte', 'Tenis'),
            (4, 'Cancha Sur', 'Tenis'),
            (5, 'Mesa de Billar', 'Juegos'),
            (5, 'Mesa de Ping Pong', 'Juegos'),
            (6, 'Jardín Central', 'Jardín'),
            (6, 'Área de Picnic', 'Jardín'),
            (7, 'Terraza Oeste', 'Terraza'),
            (7, 'Zona de Asadores', 'Terraza'),
            (8, 'Sala Ejecutiva', 'Reuniones'),
            (8, 'Sala de Conferencias', 'Reuniones'),
            (9, 'Área de Lectura', 'Biblioteca'),
            (9, 'Estudio Grupal', 'Biblioteca'),
            (10, 'Sala de Proyección', 'Entretenimiento'),
            (10, 'Área de Espera', 'Entretenimiento');
            """
            total_registros += ejecutar_sql_seguro(sql_zonas, "Insertando 20 zonas")
            
            # 6. TIPOS DE EVENTOS
            print("\n🚨 Poblando TIPOS DE EVENTOS...")
            sql_tipos = """
            INSERT INTO tipo_evento (nombre, descripcion, severidad) VALUES
            ('Acceso no autorizado', 'Intento de acceso sin autorización', 'alta'),
            ('Vehículo no reconocido', 'Vehículo no registrado intentando ingresar', 'media'),
            ('Actividad sospechosa', 'Comportamiento inusual o sospechoso', 'media'),
            ('Emergencia médica', 'Situación que requiere atención médica', 'alta'),
            ('Incidente de seguridad', 'Cualquier incidente relacionado con seguridad', 'media'),
            ('Acceso autorizado', 'Acceso permitido y registrado', 'baja'),
            ('Alarma activada', 'Activación de alarma de seguridad', 'alta'),
            ('Visitante registrado', 'Ingreso de visitante previamente registrado', 'baja'),
            ('Entrega de paquete', 'Entrega de paquete o correspondencia', 'baja'),
            ('Mantenimiento programado', 'Personal de mantenimiento realizando labores', 'baja'),
            ('Evento social', 'Celebración o evento social autorizado', 'baja'),
            ('Problema técnico', 'Fallo en equipo o sistema del condominio', 'media'),
            ('Animal en áreas comunes', 'Presencia de animales en áreas restringidas', 'baja'),
            ('Daño a propiedad', 'Vandalismo o daño a propiedad común', 'alta'),
            ('Inundación o fuga', 'Fuga de agua o inundación en áreas comunes', 'alta'),
            ('Incendio', 'Fuego o humo detectado', 'critica'),
            ('Corte de energía', 'Interrupción del suministro eléctrico', 'media'),
            ('Persona extraña', 'Persona no identificada en áreas restringidas', 'alta'),
            ('Violación de normas', 'Incumplimiento de reglas del condominio', 'media'),
            ('Reunión de condominio', 'Asamblea o reunión de residentes', 'baja')
            ON CONFLICT (nombre) DO NOTHING;
            """
            total_registros += ejecutar_sql_seguro(sql_tipos, "Insertando 20 tipos de eventos")
            
            print("=" * 60)
            print(f"✅ POBLADO BÁSICO COMPLETADO")
            print(f"📊 Registros insertados en esta ejecución: {total_registros}")
            
    except Exception as e:
        print(f"❌ ERROR CRÍTICO: {e}")
        return False
    
    # Mostrar estado final
    print("\n📊 ESTADO FINAL:")
    mostrar_estado_base_datos()
    
    return True

def limpiar_tablas():
    """Limpiar todas las tablas"""
    print("\n🧹 LIMPIANDO TABLAS...")
    
    # Orden de limpieza (respetando foreign keys)
    tablas_orden = [
        'evento_seguridad', 'pago', 'cuota', 'reserva', 'reporte', 
        'mantenimiento', 'aviso', 'vehiculo_autorizado', 'persona_autorizada',
        'camara', 'zona', 'unidad_habitacional', 'usuario_rol',
        'area_comun', 'tipo_evento', 'usuario', 'rol'
    ]
    
    for tabla in tablas_orden:
        limpiar_tabla_si_existe(tabla)

def poblar_datos_avanzados():
    """Poblar datos avanzados: cámaras, vehículos, unidades, reservas, etc."""
    print("\n🔄 Iniciando poblado de DATOS AVANZADOS...")
    
    total_registros = 0
    
    try:
        with connection.cursor() as cursor:
            
            # CÁMARAS
            print("\n📹 Poblando CÁMARAS...")
            sql_camaras = """
            INSERT INTO camara (id_zona, nombre, ubicacion, url_stream, activa) VALUES
            (1, 'Cámara Salón Principal', 'Esquina noreste del salón', 'rtsp://camara1.smartcondominium.com/stream', TRUE),
            (3, 'Cámara Piscina', 'Vista panorámica de la piscina', 'rtsp://camara2.smartcondominium.com/stream', TRUE),
            (5, 'Cámara Cardio', 'Vista general zona cardio', 'rtsp://camara3.smartcondominium.com/stream', TRUE),
            (7, 'Cámara Tenis Norte', 'Vista de la cancha norte', 'rtsp://camara4.smartcondominium.com/stream', TRUE),
            (9, 'Cámara Billar', 'Vista de la mesa de billar', 'rtsp://camara5.smartcondominium.com/stream', TRUE),
            (11, 'Cámara Jardín', 'Vista panorámica del jardín', 'rtsp://camara6.smartcondominium.com/stream', TRUE),
            (13, 'Cámara Terraza', 'Vista de la terraza oeste', 'rtsp://camara7.smartcondominium.com/stream', TRUE),
            (15, 'Cámara Sala Ejecutiva', 'Vista general sala ejecutiva', 'rtsp://camara8.smartcondominium.com/stream', TRUE),
            (17, 'Cámara Biblioteca', 'Vista área de lectura', 'rtsp://camara9.smartcondominium.com/stream', TRUE),
            (19, 'Cámara Cine', 'Vista de la sala de proyección', 'rtsp://camara10.smartcondominium.com/stream', TRUE),
            (2, 'Cámara Cocina', 'Vista de la cocina annex', 'rtsp://camara11.smartcondominium.com/stream', TRUE),
            (4, 'Cámara Descanso', 'Vista área de descanso piscina', 'rtsp://camara12.smartcondominium.com/stream', TRUE),
            (6, 'Cámara Pesas', 'Vista zona de pesas', 'rtsp://camara13.smartcondominium.com/stream', TRUE),
            (8, 'Cámara Tenis Sur', 'Vista de la cancha sur', 'rtsp://camara14.smartcondominium.com/stream', TRUE),
            (10, 'Cámara Ping Pong', 'Vista mesa de ping pong', 'rtsp://camara15.smartcondominium.com/stream', TRUE),
            (12, 'Cámara Picnic', 'Vista área de picnic', 'rtsp://camara16.smartcondominium.com/stream', TRUE),
            (14, 'Cámara Asadores', 'Vista zona de asadores', 'rtsp://camara17.smartcondominium.com/stream', TRUE),
            (16, 'Cámara Conferencias', 'Vista sala de conferencias', 'rtsp://camara18.smartcondominium.com/stream', TRUE),
            (18, 'Cámara Estudio', 'Vista estudio grupal', 'rtsp://camara19.smartcondominium.com/stream', TRUE),
            (20, 'Cámara Espera', 'Vista área de espera cine', 'rtsp://camara20.smartcondominium.com/stream', TRUE);
            """
            total_registros += ejecutar_sql_seguro(sql_camaras, "Insertando 20 cámaras de seguridad")
            
            # VEHÍCULOS AUTORIZADOS
            print("\n🚗 Poblando VEHÍCULOS AUTORIZADOS...")
            sql_vehiculos = """
            INSERT INTO vehiculo_autorizado (id_usuario, placa, modelo, color, fecha_registro, activo) VALUES
            (2, 'ABC123', 'Toyota Corolla', 'Blanco', CURRENT_TIMESTAMP, TRUE),
            (3, 'DEF456', 'Honda Civic', 'Negro', CURRENT_TIMESTAMP, TRUE),
            (4, 'GHI789', 'Nissan Sentra', 'Rojo', CURRENT_TIMESTAMP, TRUE),
            (5, 'JKL012', 'Mazda 3', 'Azul', CURRENT_TIMESTAMP, TRUE),
            (6, 'MNO345', 'Volkswagen Jetta', 'Gris', CURRENT_TIMESTAMP, TRUE),
            (7, 'PQR678', 'Ford Focus', 'Verde', CURRENT_TIMESTAMP, TRUE),
            (8, 'STU901', 'Chevrolet Cruze', 'Plateado', CURRENT_TIMESTAMP, TRUE),
            (9, 'VWX234', 'Hyundai Elantra', 'Blanco', CURRENT_TIMESTAMP, TRUE),
            (10, 'YZA567', 'Kia Forte', 'Negro', CURRENT_TIMESTAMP, TRUE),
            (11, 'BCD890', 'Subaru Impreza', 'Azul', CURRENT_TIMESTAMP, TRUE),
            (19, 'EFG123', 'BMW 3 Series', 'Gris', CURRENT_TIMESTAMP, TRUE),
            (20, 'HIJ456', 'Audi A4', 'Negro', CURRENT_TIMESTAMP, TRUE),
            (2, 'KLM789', 'Toyota RAV4', 'Rojo', CURRENT_TIMESTAMP, TRUE),
            (3, 'NOP012', 'Honda CR-V', 'Blanco', CURRENT_TIMESTAMP, TRUE),
            (4, 'QRS345', 'Nissan Rogue', 'Plateado', CURRENT_TIMESTAMP, TRUE),
            (5, 'TUV678', 'Mazda CX-5', 'Azul', CURRENT_TIMESTAMP, TRUE),
            (6, 'WXY901', 'Ford Escape', 'Gris', CURRENT_TIMESTAMP, TRUE),
            (7, 'ZAB234', 'Chevrolet Equinox', 'Negro', CURRENT_TIMESTAMP, TRUE),
            (8, 'CDE567', 'Hyundai Tucson', 'Blanco', CURRENT_TIMESTAMP, TRUE),
            (9, 'FGH890', 'Kia Sportage', 'Rojo', CURRENT_TIMESTAMP, TRUE);
            """
            total_registros += ejecutar_sql_seguro(sql_vehiculos, "Insertando 20 vehículos autorizados")
            
            # PERSONAS AUTORIZADAS
            print("\n👥 Poblando PERSONAS AUTORIZADAS...")
            sql_personas = """
            INSERT INTO persona_autorizada (id_usuario, datosBiometricosUrl, fecha_registro, activa) VALUES
            (2, '/biometricos/carlos_rodriguez.dat', CURRENT_TIMESTAMP, TRUE),
            (3, '/biometricos/maria_gonzalez.dat', CURRENT_TIMESTAMP, TRUE),
            (4, '/biometricos/juan_perez.dat', CURRENT_TIMESTAMP, TRUE),
            (5, '/biometricos/ana_martinez.dat', CURRENT_TIMESTAMP, TRUE),
            (6, '/biometricos/luis_sanchez.dat', CURRENT_TIMESTAMP, TRUE),
            (7, '/biometricos/laura_lopez.dat', CURRENT_TIMESTAMP, TRUE),
            (8, '/biometricos/pedro_garcia.dat', CURRENT_TIMESTAMP, TRUE),
            (9, '/biometricos/sofia_hernandez.dat', CURRENT_TIMESTAMP, TRUE),
            (10, '/biometricos/diego_torres.dat', CURRENT_TIMESTAMP, TRUE),
            (11, '/biometricos/elena_ramirez.dat', CURRENT_TIMESTAMP, TRUE),
            (19, '/biometricos/carmen_ortega.dat', CURRENT_TIMESTAMP, TRUE),
            (20, '/biometricos/miguel_mendoza.dat', CURRENT_TIMESTAMP, TRUE),
            (2, '/biometricos/carlos_rodriguez2.dat', CURRENT_TIMESTAMP, TRUE),
            (3, '/biometricos/maria_gonzalez2.dat', CURRENT_TIMESTAMP, TRUE),
            (4, '/biometricos/juan_perez2.dat', CURRENT_TIMESTAMP, TRUE),
            (5, '/biometricos/ana_martinez2.dat', CURRENT_TIMESTAMP, TRUE),
            (6, '/biometricos/luis_sanchez2.dat', CURRENT_TIMESTAMP, TRUE),
            (7, '/biometricos/laura_lopez2.dat', CURRENT_TIMESTAMP, TRUE),
            (8, '/biometricos/pedro_garcia2.dat', CURRENT_TIMESTAMP, TRUE),
            (9, '/biometricos/sofia_hernandez2.dat', CURRENT_TIMESTAMP, TRUE);
            """
            total_registros += ejecutar_sql_seguro(sql_personas, "Insertando 20 personas autorizadas")
            
            # UNIDADES HABITACIONALES
            print("\n🏠 Poblando UNIDADES HABITACIONALES...")
            sql_unidades = """
            INSERT INTO unidad_habitacional (id_usuarioPropietario, id_usuarioInquilino, identificador, tipo, metros_cuadrados, activo) VALUES
            (2, 7, 'A101', 'Departamento', 85.50, TRUE),
            (3, 8, 'A102', 'Departamento', 90.25, TRUE),
            (4, 9, 'A201', 'Departamento', 95.75, TRUE),
            (5, 10, 'A202', 'Departamento', 85.50, TRUE),
            (6, 11, 'A301', 'Departamento', 100.00, TRUE),
            (19, NULL, 'A302', 'Departamento', 95.75, TRUE),
            (20, NULL, 'B101', 'Penthouse', 150.50, TRUE),
            (2, NULL, 'B102', 'Penthouse', 145.25, TRUE),
            (3, NULL, 'B201', 'Penthouse', 160.75, TRUE),
            (4, NULL, 'B202', 'Penthouse', 155.00, TRUE),
            (5, NULL, 'C101', 'Estudio', 45.50, TRUE),
            (6, NULL, 'C102', 'Estudio', 50.25, TRUE),
            (19, NULL, 'C201', 'Estudio', 48.75, TRUE),
            (20, NULL, 'C202', 'Estudio', 52.00, TRUE),
            (2, NULL, 'D101', 'Dúplex', 120.50, TRUE),
            (3, NULL, 'D102', 'Dúplex', 125.25, TRUE),
            (4, NULL, 'D201', 'Dúplex', 130.75, TRUE),
            (5, NULL, 'D202', 'Dúplex', 135.00, TRUE),
            (6, NULL, 'E101', 'Loft', 75.50, TRUE),
            (19, NULL, 'E102', 'Loft', 80.25, TRUE);
            """
            total_registros += ejecutar_sql_seguro(sql_unidades, "Insertando 20 unidades habitacionales")
            
            print(f"\n🎉 DATOS AVANZADOS COMPLETADOS - {total_registros} registros")
            
    except Exception as e:
        print(f"❌ ERROR en datos avanzados: {e}")
        return False
    
    return total_registros

def poblar_datos_operacionales():
    """Poblar datos operacionales: reservas, cuotas, pagos, avisos, etc."""
    print("\n💼 Iniciando poblado de DATOS OPERACIONALES...")
    
    total_registros = 0
    
    try:
        with connection.cursor() as cursor:
            
            # RESERVAS
            print("\n📅 Poblando RESERVAS...")
            sql_reservas = """
            INSERT INTO reserva (id_areaComun, id_usuario, fecha_inicio, fecha_fin, monto_total, estado, fecha_creacion) VALUES
            (1, 2, CURRENT_DATE + INTERVAL '2 days' + TIME '10:00', CURRENT_DATE + INTERVAL '2 days' + TIME '14:00', 200.00, 'confirmada', CURRENT_TIMESTAMP),
            (2, 3, CURRENT_DATE + INTERVAL '3 days' + TIME '11:00', CURRENT_DATE + INTERVAL '3 days' + TIME '15:00', 80.00, 'confirmada', CURRENT_TIMESTAMP),
            (3, 4, CURRENT_DATE + INTERVAL '4 days' + TIME '08:00', CURRENT_DATE + INTERVAL '4 days' + TIME '10:00', 20.00, 'confirmada', CURRENT_TIMESTAMP),
            (4, 5, CURRENT_DATE + INTERVAL '5 days' + TIME '14:00', CURRENT_DATE + INTERVAL '5 days' + TIME '16:00', 30.00, 'confirmada', CURRENT_TIMESTAMP),
            (5, 6, CURRENT_DATE + INTERVAL '6 days' + TIME '16:00', CURRENT_DATE + INTERVAL '6 days' + TIME '18:00', 16.00, 'confirmada', CURRENT_TIMESTAMP),
            (6, 7, CURRENT_DATE + INTERVAL '7 days' + TIME '12:00', CURRENT_DATE + INTERVAL '7 days' + TIME '14:00', 10.00, 'pendiente', CURRENT_TIMESTAMP),
            (7, 8, CURRENT_DATE + INTERVAL '8 days' + TIME '18:00', CURRENT_DATE + INTERVAL '8 days' + TIME '21:00', 75.00, 'pendiente', CURRENT_TIMESTAMP),
            (8, 9, CURRENT_DATE + INTERVAL '9 days' + TIME '09:00', CURRENT_DATE + INTERVAL '9 days' + TIME '11:00', 60.00, 'confirmada', CURRENT_TIMESTAMP),
            (9, 10, CURRENT_DATE + INTERVAL '10 days' + TIME '15:00', CURRENT_DATE + INTERVAL '10 days' + TIME '17:00', 0.00, 'confirmada', CURRENT_TIMESTAMP),
            (10, 11, CURRENT_DATE + INTERVAL '11 days' + TIME '19:00', CURRENT_DATE + INTERVAL '11 days' + TIME '22:00', 105.00, 'pendiente', CURRENT_TIMESTAMP),
            (1, 19, CURRENT_DATE + INTERVAL '12 days' + TIME '16:00', CURRENT_DATE + INTERVAL '12 days' + TIME '20:00', 200.00, 'confirmada', CURRENT_TIMESTAMP),
            (2, 20, CURRENT_DATE + INTERVAL '13 days' + TIME '13:00', CURRENT_DATE + INTERVAL '13 days' + TIME '17:00', 80.00, 'confirmada', CURRENT_TIMESTAMP),
            (3, 2, CURRENT_DATE + INTERVAL '14 days' + TIME '07:00', CURRENT_DATE + INTERVAL '14 days' + TIME '09:00', 20.00, 'pendiente', CURRENT_TIMESTAMP),
            (4, 3, CURRENT_DATE + INTERVAL '15 days' + TIME '15:00', CURRENT_DATE + INTERVAL '15 days' + TIME '17:00', 30.00, 'confirmada', CURRENT_TIMESTAMP),
            (5, 4, CURRENT_DATE + INTERVAL '16 days' + TIME '17:00', CURRENT_DATE + INTERVAL '16 days' + TIME '19:00', 16.00, 'pendiente', CURRENT_TIMESTAMP),
            (6, 5, CURRENT_DATE + INTERVAL '17 days' + TIME '10:00', CURRENT_DATE + INTERVAL '17 days' + TIME '12:00', 10.00, 'confirmada', CURRENT_TIMESTAMP),
            (7, 6, CURRENT_DATE + INTERVAL '18 days' + TIME '19:00', CURRENT_DATE + INTERVAL '18 days' + TIME '22:00', 75.00, 'confirmada', CURRENT_TIMESTAMP),
            (8, 7, CURRENT_DATE + INTERVAL '19 days' + TIME '10:00', CURRENT_DATE + INTERVAL '19 days' + TIME '12:00', 60.00, 'pendiente', CURRENT_TIMESTAMP),
            (9, 8, CURRENT_DATE + INTERVAL '20 days' + TIME '14:00', CURRENT_DATE + INTERVAL '20 days' + TIME '16:00', 0.00, 'confirmada', CURRENT_TIMESTAMP),
            (10, 9, CURRENT_DATE + INTERVAL '21 days' + TIME '20:00', CURRENT_DATE + INTERVAL '21 days' + TIME '23:00', 105.00, 'pendiente', CURRENT_TIMESTAMP);
            """
            total_registros += ejecutar_sql_seguro(sql_reservas, "Insertando 20 reservas")
            
            # CUOTAS
            print("\n💰 Poblando CUOTAS...")
            sql_cuotas = """
            INSERT INTO cuota (id_unidadHabitacional, concepto, monto, fecha_emision, fecha_vencimiento, estado, fecha_pago) VALUES
            (1, 'Mantenimiento octubre', 1500.00, CURRENT_DATE - INTERVAL '10 days', CURRENT_DATE + INTERVAL '5 days', 'pagada', CURRENT_DATE - INTERVAL '2 days'),
            (2, 'Mantenimiento octubre', 1650.00, CURRENT_DATE - INTERVAL '10 days', CURRENT_DATE + INTERVAL '5 days', 'pagada', CURRENT_DATE - INTERVAL '1 days'),
            (3, 'Mantenimiento octubre', 1725.00, CURRENT_DATE - INTERVAL '10 days', CURRENT_DATE + INTERVAL '5 days', 'pagada', CURRENT_DATE - INTERVAL '3 days'),
            (4, 'Mantenimiento octubre', 1500.00, CURRENT_DATE - INTERVAL '10 days', CURRENT_DATE + INTERVAL '5 days', 'pendiente', NULL),
            (5, 'Mantenimiento octubre', 1800.00, CURRENT_DATE - INTERVAL '10 days', CURRENT_DATE + INTERVAL '5 days', 'pendiente', NULL),
            (6, 'Mantenimiento octubre', 1725.00, CURRENT_DATE - INTERVAL '10 days', CURRENT_DATE + INTERVAL '5 days', 'pagada', CURRENT_DATE - INTERVAL '4 days'),
            (7, 'Mantenimiento octubre', 2250.00, CURRENT_DATE - INTERVAL '10 days', CURRENT_DATE + INTERVAL '5 days', 'pagada', CURRENT_DATE - INTERVAL '5 days'),
            (8, 'Mantenimiento octubre', 2175.00, CURRENT_DATE - INTERVAL '10 days', CURRENT_DATE + INTERVAL '5 days', 'pagada', CURRENT_DATE - INTERVAL '2 days'),
            (9, 'Mantenimiento octubre', 2400.00, CURRENT_DATE - INTERVAL '10 days', CURRENT_DATE + INTERVAL '5 days', 'pendiente', NULL),
            (10, 'Mantenimiento octubre', 2325.00, CURRENT_DATE - INTERVAL '10 days', CURRENT_DATE + INTERVAL '5 days', 'pagada', CURRENT_DATE - INTERVAL '1 days'),
            (11, 'Mantenimiento octubre', 1200.00, CURRENT_DATE - INTERVAL '10 days', CURRENT_DATE + INTERVAL '5 days', 'pagada', CURRENT_DATE - INTERVAL '3 days'),
            (12, 'Mantenimiento octubre', 1275.00, CURRENT_DATE - INTERVAL '10 days', CURRENT_DATE + INTERVAL '5 days', 'pendiente', NULL),
            (13, 'Mantenimiento octubre', 1200.00, CURRENT_DATE - INTERVAL '10 days', CURRENT_DATE + INTERVAL '5 days', 'pagada', CURRENT_DATE - INTERVAL '4 days'),
            (14, 'Mantenimiento octubre', 1350.00, CURRENT_DATE - INTERVAL '10 days', CURRENT_DATE + INTERVAL '5 days', 'pagada', CURRENT_DATE - INTERVAL '2 days'),
            (15, 'Mantenimiento octubre', 1950.00, CURRENT_DATE - INTERVAL '10 days', CURRENT_DATE + INTERVAL '5 days', 'pendiente', NULL),
            (16, 'Mantenimiento octubre', 2025.00, CURRENT_DATE - INTERVAL '10 days', CURRENT_DATE + INTERVAL '5 days', 'pagada', CURRENT_DATE - INTERVAL '1 days'),
            (17, 'Mantenimiento octubre', 2100.00, CURRENT_DATE - INTERVAL '10 days', CURRENT_DATE + INTERVAL '5 days', 'pagada', CURRENT_DATE - INTERVAL '3 days'),
            (18, 'Mantenimiento octubre', 2175.00, CURRENT_DATE - INTERVAL '10 days', CURRENT_DATE + INTERVAL '5 days', 'pendiente', NULL),
            (19, 'Mantenimiento octubre', 1425.00, CURRENT_DATE - INTERVAL '10 days', CURRENT_DATE + INTERVAL '5 days', 'pagada', CURRENT_DATE - INTERVAL '2 days'),
            (20, 'Mantenimiento octubre', 1500.00, CURRENT_DATE - INTERVAL '10 days', CURRENT_DATE + INTERVAL '5 days', 'pagada', CURRENT_DATE - INTERVAL '4 days');
            """
            total_registros += ejecutar_sql_seguro(sql_cuotas, "Insertando 20 cuotas")
            
            print(f"\n🎉 DATOS OPERACIONALES COMPLETADOS - {total_registros} registros")
            
    except Exception as e:
        print(f"❌ ERROR en datos operacionales: {e}")
        return False
    
    return total_registros

def menu_interactivo():
    """Menú interactivo para el usuario"""
    print("\n" + "=" * 60)
    print("🏢 SMART CONDOMINIUM - POBLADO DE BASE DE DATOS")
    print("=" * 60)
    
    while True:
        print("\n📋 OPCIONES DISPONIBLES:")
        print("1. 📊 Ver estado actual de la base de datos")
        print("2. 🚀 Poblar datos básicos (mantener datos existentes)")
        print("3. 🧹 Limpiar y poblar datos básicos desde cero")
        print("4. � Poblar datos avanzados (cámaras, vehículos, unidades)")
        print("5. 💼 Poblar datos operacionales (reservas, cuotas, pagos)")
        print("6. 🎯 Poblado COMPLETO (básicos + avanzados + operacionales)")
        print("7. 🗑️ Solo limpiar todas las tablas")
        print("8. ❌ Salir")
        
        try:
            opcion = input("\n👉 Selecciona una opción (1-8): ").strip()
            
            if opcion == "1":
                mostrar_estado_base_datos()
                
            elif opcion == "2":
                print("\n🚀 Poblando datos básicos (manteniendo datos existentes)...")
                exito = poblar_base_datos_mejorado(limpiar_antes=False)
                if exito:
                    print("\n🎉 ¡Datos básicos poblados exitosamente!")
                else:
                    print("\n💥 Hubo errores en el poblado.")
                    
            elif opcion == "3":
                confirm = input("\n⚠️ ¿ESTÁS SEGURO? Esto eliminará TODOS los datos existentes (y/n): ")
                if confirm.lower() in ['y', 'yes', 's', 'si']:
                    print("\n🧹 Limpiando y poblando datos básicos desde cero...")
                    exito = poblar_base_datos_mejorado(limpiar_antes=True)
                    if exito:
                        print("\n🎉 ¡Base de datos reiniciada con datos básicos!")
                    else:
                        print("\n💥 Hubo errores en el proceso.")
                else:
                    print("❌ Operación cancelada.")
                    
            elif opcion == "4":
                print("\n🔧 Poblando datos avanzados...")
                registros = poblar_datos_avanzados()
                if registros >= 0:
                    print(f"\n🎉 ¡{registros} registros avanzados agregados!")
                else:
                    print("\n💥 Hubo errores en el poblado avanzado.")
                    
            elif opcion == "5":
                print("\n💼 Poblando datos operacionales...")
                registros = poblar_datos_operacionales()
                if registros >= 0:
                    print(f"\n🎉 ¡{registros} registros operacionales agregados!")
                else:
                    print("\n💥 Hubo errores en el poblado operacional.")
                    
            elif opcion == "6":
                confirm = input("\n🎯 ¿Realizar poblado COMPLETO? Esto puede tomar unos minutos (y/n): ")
                if confirm.lower() in ['y', 'yes', 's', 'si']:
                    print("\n🚀 Iniciando poblado COMPLETO...")
                    
                    # 1. Datos básicos
                    print("🔹 Fase 1: Datos básicos")
                    exito1 = poblar_base_datos_mejorado(limpiar_antes=False)
                    
                    # 2. Datos avanzados
                    print("\n🔹 Fase 2: Datos avanzados")
                    reg2 = poblar_datos_avanzados()
                    
                    # 3. Datos operacionales
                    print("\n🔹 Fase 3: Datos operacionales")
                    reg3 = poblar_datos_operacionales()
                    
                    total = reg2 + reg3
                    if exito1 and reg2 >= 0 and reg3 >= 0:
                        print(f"\n🎉 ¡POBLADO COMPLETO EXITOSO! {total} registros totales")
                        mostrar_estado_base_datos()
                    else:
                        print("\n⚠️ Poblado parcialmente completado con algunos errores.")
                else:
                    print("❌ Operación cancelada.")
                    
            elif opcion == "7":
                confirm = input("\n⚠️ ¿ESTÁS SEGURO? Esto eliminará TODOS los datos (y/n): ")
                if confirm.lower() in ['y', 'yes', 's', 'si']:
                    limpiar_tablas()
                    print("\n🧹 ¡Tablas limpiadas exitosamente!")
                    mostrar_estado_base_datos()
                else:
                    print("❌ Operación cancelada.")
                    
            elif opcion == "8":
                print("\n👋 ¡Hasta luego!")
                break
                
            else:
                print("❌ Opción no válida. Por favor selecciona 1-8.")
                
        except KeyboardInterrupt:
            print("\n\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    # Verificar conexión a la base de datos
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✅ Conexión a base de datos: OK")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        sys.exit(1)
    
    # Mostrar credenciales importantes
    print("\n🔑 CREDENCIALES DEL ADMINISTRADOR:")
    print("📧 Email: admin@smartcondominium.com")
    print("🔒 Password: admin123")
    
    # Ejecutar menú interactivo
    menu_interactivo()
