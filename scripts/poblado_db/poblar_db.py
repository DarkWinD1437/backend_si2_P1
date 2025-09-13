#!/usr/bin/env python3
"""
Script para poblar la base de datos Smart Condominium
Ejecutar desde el directorio del proyecto Django:

python poblar_db.py

o

python manage.py runscript poblar_db
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

def ejecutar_sql(sql_statement, descripcion=""):
    """Ejecutar una declaración SQL"""
    print(f"  🔸 {descripcion}")
    try:
        with connection.cursor() as cursor:
            cursor.execute(sql_statement)
            affected_rows = cursor.rowcount
            print(f"    ✅ Ejecutado exitosamente - {affected_rows} filas afectadas")
            return affected_rows
    except Exception as e:
        print(f"    ❌ Error: {str(e)[:100]}")
        return 0

def poblar_base_datos():
    """Función principal para poblar la base de datos"""
    print("🚀 Iniciando poblado de Smart Condominium...")
    print(f"📅 Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 60)
    
    total_registros = 0
    
    try:
        with transaction.atomic():
            # 1. Roles
            print("👥 Poblando ROLES...")
            sql_roles = """
            INSERT INTO rol (nombre, descripcion) VALUES
            ('Administrador', 'Administrador del sistema con todos los permisos'),
            ('Propietario', 'Propietario de una unidad habitacional'),
            ('Inquilino', 'Persona que habita una unidad habitacional'),
            ('Seguridad', 'Personal de seguridad del condominio'),
            ('Conserje', 'Personal de conserjería y atención a residentes'),
            ('Mantenimiento', 'Personal de mantenimiento del condominio');
            """
            total_registros += ejecutar_sql(sql_roles, "Insertando 6 roles del sistema")
            
            # 2. Usuario Administrador
            print("\n🔐 Poblando USUARIO ADMINISTRADOR...")
            sql_admin = """
            INSERT INTO usuario (nombre, email, password, telefono, tipo, activo) VALUES
            ('Administrador Principal', 'admin@smartcondominium.com', crypt('admin123', gen_salt('bf')), '+1234567890', 'administrador', TRUE);
            """
            total_registros += ejecutar_sql(sql_admin, "Creando usuario administrador principal")
            
            # 3. Usuarios regulares (primera parte)
            print("\n👤 Poblando USUARIOS (Parte 1 - Propietarios)...")
            sql_usuarios_1 = """
            INSERT INTO usuario (nombre, email, password, telefono, tipo, activo) VALUES
            ('Carlos Rodríguez', 'carlos.rodriguez@email.com', crypt('password123', gen_salt('bf')), '+1234567891', 'propietario', TRUE),
            ('María González', 'maria.gonzalez@email.com', crypt('password123', gen_salt('bf')), '+1234567892', 'propietario', TRUE),
            ('Juan Pérez', 'juan.perez@email.com', crypt('password123', gen_salt('bf')), '+1234567893', 'propietario', TRUE),
            ('Ana Martínez', 'ana.martinez@email.com', crypt('password123', gen_salt('bf')), '+1234567894', 'propietario', TRUE),
            ('Luis Sánchez', 'luis.sanchez@email.com', crypt('password123', gen_salt('bf')), '+1234567895', 'propietario', TRUE),
            ('Carmen Ortega', 'carmen.ortega@email.com', crypt('password123', gen_salt('bf')), '+1234567808', 'propietario', TRUE),
            ('Miguel Mendoza', 'miguel.mendoza@email.com', crypt('password123', gen_salt('bf')), '+1234567809', 'propietario', TRUE);
            """
            total_registros += ejecutar_sql(sql_usuarios_1, "Insertando propietarios")
            
            # 4. Usuarios inquilinos
            print("\n🏠 Poblando USUARIOS (Parte 2 - Inquilinos)...")
            sql_usuarios_2 = """
            INSERT INTO usuario (nombre, email, password, telefono, tipo, activo) VALUES
            ('Laura López', 'laura.lopez@email.com', crypt('password123', gen_salt('bf')), '+1234567896', 'inquilino', TRUE),
            ('Pedro García', 'pedro.garcia@email.com', crypt('password123', gen_salt('bf')), '+1234567897', 'inquilino', TRUE),
            ('Sofía Hernández', 'sofia.hernandez@email.com', crypt('password123', gen_salt('bf')), '+1234567898', 'inquilino', TRUE),
            ('Diego Torres', 'diego.torres@email.com', crypt('password123', gen_salt('bf')), '+1234567899', 'inquilino', TRUE),
            ('Elena Ramírez', 'elena.ramirez@email.com', crypt('password123', gen_salt('bf')), '+1234567800', 'inquilino', TRUE);
            """
            total_registros += ejecutar_sql(sql_usuarios_2, "Insertando inquilinos")
            
            # 5. Personal del condominio
            print("\n👷 Poblando USUARIOS (Parte 3 - Personal)...")
            sql_usuarios_3 = """
            INSERT INTO usuario (nombre, email, password, telefono, tipo, activo) VALUES
            ('Jorge Flores', 'jorge.flores@email.com', crypt('password123', gen_salt('bf')), '+1234567801', 'seguridad', TRUE),
            ('Mónica Díaz', 'monica.diaz@email.com', crypt('password123', gen_salt('bf')), '+1234567802', 'seguridad', TRUE),
            ('Ricardo Vargas', 'ricardo.vargas@email.com', crypt('password123', gen_salt('bf')), '+1234567803', 'conserje', TRUE),
            ('Isabel Castro', 'isabel.castro@email.com', crypt('password123', gen_salt('bf')), '+1234567804', 'conserje', TRUE),
            ('Fernando Ruiz', 'fernando.ruiz@email.com', crypt('password123', gen_salt('bf')), '+1234567805', 'mantenimiento', TRUE),
            ('Gabriela Morales', 'gabriela.morales@email.com', crypt('password123', gen_salt('bf')), '+1234567806', 'mantenimiento', TRUE),
            ('Roberto Silva', 'roberto.silva@email.com', crypt('password123', gen_salt('bf')), '+1234567807', 'administrador', TRUE);
            """
            total_registros += ejecutar_sql(sql_usuarios_3, "Insertando personal del condominio")
            
            # 6. Relaciones usuario-rol
            print("\n🔗 Poblando RELACIONES USUARIO-ROL...")
            sql_usuario_rol = """
            INSERT INTO usuario_rol (id_usuario, id_rol) VALUES
            (1, 1), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2), (8, 2), (9, 2),
            (7, 3), (10, 3), (11, 3), (12, 3), (13, 3),
            (14, 4), (15, 4), (16, 5), (17, 5), (18, 6), (19, 6), (20, 1);
            """
            total_registros += ejecutar_sql(sql_usuario_rol, "Asignando roles a usuarios")
            
            # 7. Áreas comunes
            print("\n🏛️ Poblando ÁREAS COMUNES...")
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
            ('Cine en Casa', 'Sala con equipo de proyección y sonido', 10, 35.00, '14:00-23:00', TRUE);
            """
            total_registros += ejecutar_sql(sql_areas, "Insertando 10 áreas comunes")
            
            print("=" * 60)
            print(f"✅ POBLADO COMPLETADO EXITOSAMENTE")
            print(f"📊 Total de registros insertados: {total_registros}")
            print(f"📅 Finalizado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
            print("=" * 60)
            
            # Mostrar resumen
            print("\n📋 RESUMEN DE DATOS POBLADOS:")
            print("  👥 Usuarios: 20 (1 admin principal + 19 usuarios)")
            print("  🏛️ Áreas Comunes: 10")
            print("  👑 Roles: 6") 
            print("  🔗 Relaciones Usuario-Rol: 20")
            print("\n🔑 CREDENCIALES DE ACCESO:")
            print("  📧 Email: admin@smartcondominium.com")
            print("  🔒 Password: admin123")
            
    except Exception as e:
        print(f"❌ ERROR CRÍTICO: {e}")
        return False
    
    return True

if __name__ == "__main__":
    # Verificar conexión a la base de datos
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        print("✅ Conexión a base de datos: OK")
    except Exception as e:
        print(f"❌ Error de conexión: {e}")
        sys.exit(1)
    
    # Ejecutar poblado
    exito = poblar_base_datos()
    
    if exito:
        print("\n🎉 Proceso completado exitosamente!")
        print("💡 Ahora puedes usar el sistema con las credenciales mostradas arriba.")
    else:
        print("\n💥 El proceso falló. Revisa los errores arriba.")
        sys.exit(1)
