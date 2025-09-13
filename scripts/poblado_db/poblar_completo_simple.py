#!/usr/bin/env python3
"""
Script COMPLETO para poblar Smart Condominium - Solo ejecutar SQL
SIN dependencias de Django
"""

import os
import psycopg2
import random
from datetime import datetime, timedelta

# Configuración de la base de datos
DB_CONFIG = {
    'host': 'localhost',
    'database': 'Smart_Condominium',
    'user': 'postgres',
    'password': 'admin',
    'port': '5432'
}

def conectar_db():
    """Conectar a la base de datos PostgreSQL"""
    try:
        # Configuración exacta del settings.py de Django
        conn = psycopg2.connect(
            host='localhost',
            database='Smart_Condominium',
            user='postgres',
            password='123456',  # Según settings.py
            port='5432',
            client_encoding='UTF8'
        )
        return conn
    except psycopg2.Error as e:
        print(f"❌ Error de PostgreSQL: {e}")
        return None
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        return None

def contar_registros(conn, tabla):
    """Contar registros en una tabla"""
    try:
        cursor = conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
        result = cursor.fetchone()[0]
        cursor.close()
        return result
    except:
        return 0

def ejecutar_sql_seguro(conn, sql, descripcion):
    """Ejecutar SQL de forma segura"""
    try:
        cursor = conn.cursor()
        cursor.execute(sql)
        affected = cursor.rowcount
        conn.commit()
        cursor.close()
        
        if affected > 0:
            print(f"    ✅ {descripcion}: {affected} registros insertados")
        else:
            print(f"    ⚠️ {descripcion}: 0 registros (posiblemente ya existen)")
        return affected
    except Exception as e:
        error_str = str(e).lower()
        if any(keyword in error_str for keyword in ["duplicate", "duplicada", "unique", "already exists"]):
            print(f"    ⚠️ {descripcion}: Datos ya existen")
            conn.rollback()
            return 0
        else:
            print(f"    ❌ {descripcion}: Error - {str(e)[:100]}...")
            conn.rollback()
            raise e

def mostrar_estado_db(conn):
    """Mostrar estado de la base de datos"""
    print("\n📊 ESTADO ACTUAL DE LA BASE DE DATOS:")
    print("=" * 50)
    
    tablas = [
        'rol', 'usuario', 'usuario_rol', 'area_comun', 'zona', 
        'camara', 'tipo_evento', 'vehiculo_autorizado', 'persona_autorizada',
        'unidad_habitacional', 'reserva', 'cuota', 'pago', 
        'aviso', 'evento_seguridad', 'mantenimiento', 'reporte'
    ]
    
    total = 0
    for tabla in tablas:
        count = contar_registros(conn, tabla)
        total += count
        status = "✅" if count > 0 else "🔹"
        print(f"  {status} {tabla:20} : {count:4} registros")
    
    print("=" * 50)
    print(f"📈 TOTAL DE REGISTROS: {total}")
    return total

def poblar_todos_los_datos(conn):
    """Poblar TODOS los datos completos"""
    print("🚀 INICIANDO POBLADO COMPLETO DE SMART CONDOMINIUM")
    print(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    
    total_insertados = 0
    
    # 1. ROLES
    print("\n👥 POBLANDO ROLES...")
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
    total_insertados += ejecutar_sql_seguro(conn, sql_roles, "Roles del sistema (6)")
    
    # 2. USUARIOS COMPLETOS
    print("\n👤 POBLANDO USUARIOS COMPLETOS...")
    sql_admin = """
    INSERT INTO usuario (nombre, email, password, telefono, tipo, activo) VALUES
    ('Administrador Principal', 'admin@smartcondominium.com', crypt('admin123', gen_salt('bf')), '+1234567890', 'administrador', TRUE)
    ON CONFLICT (email) DO NOTHING;
    """
    total_insertados += ejecutar_sql_seguro(conn, sql_admin, "Usuario administrador")
    
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
    ('Ricardo Vargas', 'ricardo.vargas@email.com', crypt('password123', gen_salt('bf')), '+1234567803', 'seguridad', TRUE),
    ('Isabel Castro', 'isabel.castro@email.com', crypt('password123', gen_salt('bf')), '+1234567804', 'seguridad', TRUE),
    ('Fernando Ruiz', 'fernando.ruiz@email.com', crypt('password123', gen_salt('bf')), '+1234567805', 'seguridad', TRUE),
    ('Gabriela Morales', 'gabriela.morales@email.com', crypt('password123', gen_salt('bf')), '+1234567806', 'seguridad', TRUE),
    ('Roberto Silva', 'roberto.silva@email.com', crypt('password123', gen_salt('bf')), '+1234567807', 'administrador', TRUE),
    ('Carmen Ortega', 'carmen.ortega@email.com', crypt('password123', gen_salt('bf')), '+1234567808', 'propietario', TRUE),
    ('Miguel Mendoza', 'miguel.mendoza@email.com', crypt('password123', gen_salt('bf')), '+1234567809', 'propietario', TRUE)
    ON CONFLICT (email) DO NOTHING;
    """
    total_insertados += ejecutar_sql_seguro(conn, sql_usuarios, "Usuarios completos (19)")
    
    # 3. USUARIO_ROL (Usando los IDs reales de usuarios y roles)
    print("\n🔗 ASIGNANDO ROLES...")
    
    # Obtener los IDs reales de usuarios y roles
    cursor_temp = conn.cursor()
    cursor_temp.execute("SELECT id_usuario, nombre, tipo FROM usuario ORDER BY id_usuario")
    usuarios_completos = cursor_temp.fetchall()
    usuarios_reales = [row[0] for row in usuarios_completos]  # Solo los IDs para usar después
    
    cursor_temp.execute("SELECT id_rol, nombre FROM rol ORDER BY id_rol")
    roles_reales = cursor_temp.fetchall()
    cursor_temp.close()
    
    # Crear mapa de roles nombre -> id
    mapa_roles = {
        'Administrador': None,
        'Propietario': None, 
        'Inquilino': None,
        'Seguridad': None
    }
    
    for id_rol, nombre_rol in roles_reales:
        if nombre_rol in mapa_roles:
            mapa_roles[nombre_rol] = id_rol
    
    print(f"    📋 Encontrados {len(usuarios_completos)} usuarios y {len(roles_reales)} roles")
    
    # Crear asignaciones dinámicas
    asignaciones = []
    for usuario in usuarios_completos:  # Usar usuarios_completos
        id_usuario, nombre, tipo = usuario
        rol_id = None
        
        if tipo == 'administrador' and mapa_roles['Administrador']:
            rol_id = mapa_roles['Administrador']
        elif tipo == 'propietario' and mapa_roles['Propietario']:
            rol_id = mapa_roles['Propietario']
        elif tipo == 'inquilino' and mapa_roles['Inquilino']:
            rol_id = mapa_roles['Inquilino']
        elif tipo == 'seguridad' and mapa_roles['Seguridad']:
            rol_id = mapa_roles['Seguridad']
        else:
            rol_id = mapa_roles['Propietario']  # Por defecto
            
        if rol_id:
            asignaciones.append(f"({id_usuario}, {rol_id})")
    
    if asignaciones:
        sql_roles_usuarios = f"""
        INSERT INTO usuario_rol (id_usuario, id_rol) VALUES
        {', '.join(asignaciones)}
        ON CONFLICT DO NOTHING;
        """
        total_insertados += ejecutar_sql_seguro(conn, sql_roles_usuarios, f"Asignación roles ({len(asignaciones)})")
    else:
        print("    ⚠️ No se pudieron crear asignaciones de roles")
    
    # 4. AREAS COMUNES
    print("\n🏛️ POBLANDO ÁREAS COMUNES...")
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
    total_insertados += ejecutar_sql_seguro(conn, sql_areas, "Áreas comunes (10)")
    
    # 5. ZONAS (Usando IDs reales de áreas comunes)
    print("\n📍 POBLANDO ZONAS...")
    
    # Obtener los IDs reales de las áreas comunes
    cursor_temp = conn.cursor()
    cursor_temp.execute("SELECT id_areaComun, nombre FROM area_comun ORDER BY id_areaComun")
    areas_reales = cursor_temp.fetchall()
    cursor_temp.close()
    
    print(f"    📋 Encontradas {len(areas_reales)} áreas comunes para crear zonas")
    
    # Crear zonas basadas en las áreas reales
    zonas_sql_parts = []
    for id_area, nombre_area in areas_reales:
        if 'Salón de Eventos' in nombre_area:
            zonas_sql_parts.extend([
                f"({id_area}, 'Área Principal', 'Salón')",
                f"({id_area}, 'Cocina Annex', 'Cocina')"
            ])
        elif 'Piscina' in nombre_area:
            zonas_sql_parts.extend([
                f"({id_area}, 'Piscina Principal', 'Piscina')",
                f"({id_area}, 'Área de Descanso', 'Descanso')"
            ])
        elif 'Gimnasio' in nombre_area:
            zonas_sql_parts.extend([
                f"({id_area}, 'Zona Cardio', 'Gimnasio')",
                f"({id_area}, 'Zona Pesas', 'Gimnasio')"
            ])
        elif 'Cancha' in nombre_area:
            zonas_sql_parts.extend([
                f"({id_area}, 'Cancha Norte', 'Tenis')",
                f"({id_area}, 'Cancha Sur', 'Tenis')"
            ])
        elif 'Juegos' in nombre_area:
            zonas_sql_parts.extend([
                f"({id_area}, 'Mesa de Billar', 'Juegos')",
                f"({id_area}, 'Mesa de Ping Pong', 'Juegos')"
            ])
        elif 'Jardín' in nombre_area:
            zonas_sql_parts.extend([
                f"({id_area}, 'Jardín Central', 'Jardín')",
                f"({id_area}, 'Área de Picnic', 'Jardín')"
            ])
        elif 'Terraza' in nombre_area:
            zonas_sql_parts.extend([
                f"({id_area}, 'Terraza Oeste', 'Terraza')",
                f"({id_area}, 'Zona de Asadores', 'Terraza')"
            ])
        elif 'Reuniones' in nombre_area:
            zonas_sql_parts.extend([
                f"({id_area}, 'Sala Ejecutiva', 'Reuniones')",
                f"({id_area}, 'Sala de Conferencias', 'Reuniones')"
            ])
        elif 'Biblioteca' in nombre_area:
            zonas_sql_parts.extend([
                f"({id_area}, 'Área de Lectura', 'Biblioteca')",
                f"({id_area}, 'Estudio Grupal', 'Biblioteca')"
            ])
        elif 'Cine' in nombre_area:
            zonas_sql_parts.extend([
                f"({id_area}, 'Sala de Proyección', 'Entretenimiento')",
                f"({id_area}, 'Área de Espera', 'Entretenimiento')"
            ])
    
    if zonas_sql_parts:
        sql_zonas = f"""
        INSERT INTO zona (id_areaComun, nombre, tipo) VALUES
        {', '.join(zonas_sql_parts)};
        """
        total_insertados += ejecutar_sql_seguro(conn, sql_zonas, f"Zonas ({len(zonas_sql_parts)})")
    else:
        print("    ⚠️ No se pudieron crear zonas")
    
    # 6. CÁMARAS DE SEGURIDAD (Usando IDs reales de zonas)
    print("\n📹 POBLANDO CÁMARAS DE SEGURIDAD...")
    
    # Obtener los IDs reales de las zonas creadas
    cursor_temp = conn.cursor()
    cursor_temp.execute("SELECT id_zona, nombre FROM zona ORDER BY id_zona")
    zonas_reales = cursor_temp.fetchall()
    cursor_temp.close()
    
    print(f"    📋 Encontradas {len(zonas_reales)} zonas para crear cámaras")
    
    # Crear cámaras basadas en las zonas reales
    camaras_sql_parts = []
    for i, (id_zona, nombre_zona) in enumerate(zonas_reales[:10]):  # Usar las primeras 10 zonas
        camaras_sql_parts.append(
            f"({id_zona}, 'CAM-{nombre_zona}', '{nombre_zona} - Cámara Principal', 'http://192.168.1.{100+i}/stream', TRUE)"
        )
    
    if camaras_sql_parts:
        sql_camaras = f"""
        INSERT INTO camara (id_zona, nombre, ubicacion, url_stream, activa) VALUES
        {', '.join(camaras_sql_parts)};
        """
        total_insertados += ejecutar_sql_seguro(conn, sql_camaras, f"Cámaras ({len(camaras_sql_parts)})")
    else:
        print("    ⚠️ No se pudieron crear cámaras")

    # 7. VEHÍCULOS AUTORIZADOS (Usando IDs reales de usuarios)
    print("\n🚗 POBLANDO VEHÍCULOS AUTORIZADOS...")
    
    vehiculos_sql_parts = []
    placas = ['ABC-123', 'XYZ-789', 'DEF-456', 'GHI-101', 'JKL-202', 'MNO-303', 'PQR-404', 'STU-505']
    modelos = ['Corolla 2020', 'Civic 2021', 'Focus 2019', 'Cruze 2022', 'Sentra 2020', 'Elantra 2021', 'Rio 2019', 'Mazda3 2022']
    colores = ['Blanco', 'Negro', 'Gris', 'Azul', 'Rojo', 'Plata', 'Verde', 'Amarillo']
    
    for i, id_usuario in enumerate(usuarios_reales[:8]):  # Primeros 8 usuarios
        vehiculos_sql_parts.append(
            f"({id_usuario}, '{placas[i]}', '{modelos[i]}', '{colores[i]}', CURRENT_TIMESTAMP, TRUE)"
        )
    
    if vehiculos_sql_parts:
        sql_vehiculos = f"""
        INSERT INTO vehiculo_autorizado (id_usuario, placa, modelo, color, fecha_registro, activo) VALUES
        {', '.join(vehiculos_sql_parts)};
        """
        total_insertados += ejecutar_sql_seguro(conn, sql_vehiculos, f"Vehículos ({len(vehiculos_sql_parts)})")
    else:
        print("    ⚠️ No se pudieron crear vehículos")

    # 8. PERSONAS AUTORIZADAS (Usando IDs reales de usuarios)
    print("\n👥 POBLANDO PERSONAS AUTORIZADAS...")
    
    personas_sql_parts = []
    urls_biometricos = [
        'http://biometricos.com/user1_data.json',
        'http://biometricos.com/user2_data.json',
        'http://biometricos.com/user3_data.json',
        'http://biometricos.com/user4_data.json',
        'http://biometricos.com/user5_data.json',
        'http://biometricos.com/user6_data.json',
        'http://biometricos.com/user7_data.json',
        'http://biometricos.com/user8_data.json'
    ]
    
    for i, id_usuario in enumerate(usuarios_reales[:8]):  # Primeros 8 usuarios
        personas_sql_parts.append(
            f"({id_usuario}, '{urls_biometricos[i]}', CURRENT_TIMESTAMP, TRUE)"
        )
    
    if personas_sql_parts:
        sql_personas = f"""
        INSERT INTO persona_autorizada (id_usuario, datosbiometricosurl, fecha_registro, activa) VALUES
        {', '.join(personas_sql_parts)};
        """
        total_insertados += ejecutar_sql_seguro(conn, sql_personas, f"Personas autorizadas ({len(personas_sql_parts)})")
    else:
        print("    ⚠️ No se pudieron crear personas autorizadas")
    
    # 9. UNIDADES HABITACIONALES
    print("\n🏠 POBLANDO UNIDADES HABITACIONALES...")
    
    unidades_sql_parts = []
    torres = ['A', 'B', 'C']
    tipos = ['apartamento', 'penthouse', 'local']
    
    contador = 1
    for torre in torres:
        for piso in range(1, 11):  # 10 pisos por torre
            for apto in range(1, 5):  # 4 apartamentos por piso
                tipo = tipos[contador % 3]
                metros = 85 + (contador % 50)  # Área variable
                
                # Asignar propietario (usuarios con ID >= 8 son propietarios/inquilinos)
                id_propietario = usuarios_reales[(contador % len(usuarios_reales))]
                id_inquilino = usuarios_reales[((contador + 5) % len(usuarios_reales))] if contador % 3 == 0 else 'NULL'
                
                identificador = f"{torre}{piso:02d}{apto:02d}"
                
                if id_inquilino == 'NULL':
                    unidades_sql_parts.append(
                        f"({id_propietario}, NULL, '{identificador}', '{tipo}', {metros}, TRUE)"
                    )
                else:
                    unidades_sql_parts.append(
                        f"({id_propietario}, {id_inquilino}, '{identificador}', '{tipo}', {metros}, TRUE)"
                    )
                
                contador += 1
                
                if contador > 30:  # Limitar a 30 unidades
                    break
            if contador > 30:
                break
        if contador > 30:
            break
    
    if unidades_sql_parts:
        sql_unidades = f"""
        INSERT INTO unidad_habitacional (id_usuariopropietario, id_usuarioinquilino, identificador, tipo, metros_cuadrados, activo) VALUES
        {', '.join(unidades_sql_parts)};
        """
        total_insertados += ejecutar_sql_seguro(conn, sql_unidades, f"Unidades habitacionales ({len(unidades_sql_parts)})")
    else:
        print("    ⚠️ No se pudieron crear unidades habitacionales")

    # 10. RESERVAS (usando áreas y usuarios reales)
    print("\n📅 POBLANDO RESERVAS...")
    
    # Obtener IDs de áreas comunes
    cursor_temp = conn.cursor()
    cursor_temp.execute("SELECT id_areaComun FROM area_comun")
    areas_ids = [row[0] for row in cursor_temp.fetchall()]
    cursor_temp.close()
    
    reservas_sql_parts = []
    estados = ['confirmada', 'pendiente', 'cancelada']
    
    for i in range(15):  # 15 reservas
        id_usuario = usuarios_reales[i % len(usuarios_reales)]
        id_area = areas_ids[i % len(areas_ids)]
        
        # Fechas futuras aleatorias
        fecha_base = datetime.now() + timedelta(days=random.randint(1, 30))
        hora_inicio = random.choice([8, 10, 14, 16, 18, 20])
        duracion = random.choice([2, 3, 4])  # 2-4 horas
        hora_fin = hora_inicio + duracion
        
        fecha_inicio = f"{fecha_base.strftime('%Y-%m-%d')} {hora_inicio:02d}:00:00"
        fecha_fin_str = f"{fecha_base.strftime('%Y-%m-%d')} {hora_fin:02d}:00:00"
        
        monto_total = 25.00 + (i * 5)  # Montos variables
        estado = estados[i % 3]
        
        reservas_sql_parts.append(
            f"({id_area}, {id_usuario}, '{fecha_inicio}', '{fecha_fin_str}', {monto_total}, '{estado}', CURRENT_TIMESTAMP)"
        )
    
    if reservas_sql_parts:
        sql_reservas = f"""
        INSERT INTO reserva (id_areacomun, id_usuario, fecha_inicio, fecha_fin, monto_total, estado, fecha_creacion) VALUES
        {', '.join(reservas_sql_parts)};
        """
        total_insertados += ejecutar_sql_seguro(conn, sql_reservas, f"Reservas ({len(reservas_sql_parts)})")
    else:
        print("    ⚠️ No se pudieron crear reservas")

    # 11. TIPOS DE EVENTOS
    print("\n🚨 POBLANDO TIPOS DE EVENTOS...")
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
    total_insertados += ejecutar_sql_seguro(conn, sql_tipos, "Tipos de eventos (20)")

    # 12. CUOTAS (para las unidades habitacionales)
    print("\n💰 POBLANDO CUOTAS...")
    
    # Obtener IDs de unidades habitacionales recién creadas
    cursor_temp = conn.cursor()
    cursor_temp.execute("SELECT id_unidadhabitacional FROM unidad_habitacional LIMIT 20")
    unidades_ids = [row[0] for row in cursor_temp.fetchall()]
    cursor_temp.close()
    
    if unidades_ids:
        cuotas_sql_parts = []
        conceptos = ['Administración', 'Mantenimiento', 'Servicios Públicos', 'Parqueadero', 'Seguridad']
        estados = ['pendiente', 'pagada', 'vencida']
        
        for i, id_unidad in enumerate(unidades_ids[:15]):  # 15 unidades
            # Crear 2-3 cuotas por unidad
            for mes in range(1, 4):  # 3 cuotas por unidad
                concepto = conceptos[i % len(conceptos)]
                monto = 150.00 + (i * 10)  # Montos variables
                
                fecha_emision = f"2025-{mes:02d}-01"
                fecha_vencimiento = f"2025-{mes:02d}-15"
                estado = estados[mes % 3]
                
                fecha_pago = f"2025-{mes:02d}-{10 + (i % 15)}" if estado == 'pagada' else 'NULL'
                
                if fecha_pago == 'NULL':
                    cuotas_sql_parts.append(
                        f"({id_unidad}, '{concepto}', {monto}, '{fecha_emision}', '{fecha_vencimiento}', '{estado}', NULL)"
                    )
                else:
                    cuotas_sql_parts.append(
                        f"({id_unidad}, '{concepto}', {monto}, '{fecha_emision}', '{fecha_vencimiento}', '{estado}', '{fecha_pago}')"
                    )
        
        if cuotas_sql_parts:
            sql_cuotas = f"""
            INSERT INTO cuota (id_unidadhabitacional, concepto, monto, fecha_emision, fecha_vencimiento, estado, fecha_pago) VALUES
            {', '.join(cuotas_sql_parts[:30])};
            """  # Limitar a 30 cuotas
            total_insertados += ejecutar_sql_seguro(conn, sql_cuotas, f"Cuotas ({len(cuotas_sql_parts[:30])})")
    else:
        print("    ⚠️ No hay unidades habitacionales para crear cuotas")

    # 13. PAGOS (para algunas cuotas)
    print("\n💳 POBLANDO PAGOS...")
    
    # Obtener IDs de cuotas pagadas
    cursor_temp = conn.cursor()
    cursor_temp.execute("SELECT id_cuota, monto FROM cuota WHERE estado = 'pagada' LIMIT 15")
    cuotas_pagadas = cursor_temp.fetchall()
    cursor_temp.close()
    
    if cuotas_pagadas:
        pagos_sql_parts = []
        metodos_pago = ['efectivo', 'tarjeta_credito', 'transferencia', 'digital']
        estados = ['completado', 'pendiente']
        
        for i, (id_cuota, monto) in enumerate(cuotas_pagadas):
            metodo = metodos_pago[i % 4]
            estado = estados[i % 2]
            fecha_pago = f"2025-{(i % 4) + 1:02d}-{15 + (i % 10)}"
            comprobante = f"https://comprobantes.com/pago_{1000 + i}.pdf"
            
            pagos_sql_parts.append(
                f"({id_cuota}, {monto}, '{fecha_pago}', '{metodo}', '{comprobante}', '{estado}')"
            )
        
        if pagos_sql_parts:
            sql_pagos = f"""
            INSERT INTO pago (id_cuota, monto, fecha_pago, metodo_pago, comprobante_url, estado) VALUES
            {', '.join(pagos_sql_parts)};
            """
            total_insertados += ejecutar_sql_seguro(conn, sql_pagos, f"Pagos ({len(pagos_sql_parts)})")
    else:
        print("    ⚠️ No hay cuotas pagadas para crear registros de pago")

    # 14. AVISOS
    print("\n📢 POBLANDO AVISOS...")
    
    avisos_sql_parts = []
    avisos_data = [
        ('Mantenimiento de Ascensores', 'Se realizará mantenimiento preventivo de todos los ascensores el próximo martes', 'alta'),
        ('Reunión Mensual', 'Convocatoria a reunión de copropietarios para el día 15 del mes actual', 'media'),
        ('Corte de Agua', 'Suspensión temporal del servicio de agua de 8:00 AM a 12:00 PM', 'alta'),
        ('Nuevas Normas', 'Actualización del reglamento interno de convivencia', 'media'),
        ('Evento Social', 'Celebración del día de la familia en el salón comunal', 'baja'),
        ('Seguridad', 'Refuerzo de medidas de seguridad en horas nocturnas', 'alta'),
        ('Área de Juegos', 'Renovación completa del área infantil de juegos', 'baja'),
        ('Pago de Cuotas', 'Recordatorio: vencimiento de cuotas el día 15', 'media'),
        ('WiFi Comunitario', 'Nueva red wifi gratuita en todas las áreas comunes', 'baja'),
        ('Parqueaderos', 'Asignación de nuevos espacios de parqueadero', 'media')
    ]
    
    for i, (titulo, contenido, prioridad) in enumerate(avisos_data):
        id_usuario_publicador = usuarios_reales[0]  # Administrador publica
        fecha_publicacion = datetime.now() - timedelta(days=random.randint(1, 30))
        fecha_expiracion = fecha_publicacion + timedelta(days=30)
        
        avisos_sql_parts.append(
            f"({id_usuario_publicador}, '{titulo}', '{contenido}', '{fecha_publicacion.strftime('%Y-%m-%d %H:%M:%S')}', '{fecha_expiracion.strftime('%Y-%m-%d %H:%M:%S')}', '{prioridad}')"
        )
    
    if avisos_sql_parts:
        sql_avisos = f"""
        INSERT INTO aviso (id_usuario, titulo, contenido, fecha_publicacion, fecha_expiracion, prioridad) VALUES
        {', '.join(avisos_sql_parts)};
        """
        total_insertados += ejecutar_sql_seguro(conn, sql_avisos, f"Avisos ({len(avisos_sql_parts)})")

    print(f"\n🎉 POBLADO COMPLETADO - {total_insertados} registros insertados")
    return total_insertados

def main():
    """Función principal"""
    print("🏢 SMART CONDOMINIUM - POBLADO COMPLETO")
    print("=" * 50)
    
    # Conectar a la base
    conn = conectar_db()
    if not conn:
        print("❌ No se pudo conectar a la base de datos")
        return
    
    print("✅ Conectado a PostgreSQL")
    
    # Mostrar estado inicial
    registros_iniciales = mostrar_estado_db(conn)
    
    # Poblar datos
    registros_insertados = poblar_todos_los_datos(conn)
    
    # Mostrar estado final
    print("\n📊 ESTADO FINAL:")
    registros_finales = mostrar_estado_db(conn)
    
    # Cerrar conexión
    conn.close()
    
    # Mostrar credenciales
    print("\n🔑 CREDENCIALES DEL ADMINISTRADOR:")
    print("📧 Email: admin@smartcondominium.com")
    print("🔒 Password: admin123")
    
    print(f"\n🎉 ¡LISTO! Base de datos poblada correctamente")

if __name__ == "__main__":
    main()
