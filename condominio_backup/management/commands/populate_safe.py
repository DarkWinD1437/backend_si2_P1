from django.core.management.base import BaseCommand
from django.db import connection, transaction
from datetime import datetime

class Command(BaseCommand):
    help = 'Poblar la base de datos Smart_Condominium con datos iniciales (VERSION MEJORADA - maneja duplicados)'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Limpiar todas las tablas antes de poblar'
        )
        parser.add_argument(
            '--force',
            action='store_true',
            help='Forzar la inserción incluso si hay datos existentes'
        )
        parser.add_argument(
            '--check-only',
            action='store_true',
            help='Solo verificar el estado actual de la base de datos'
        )

    def verificar_registros(self, tabla):
        """Verificar cuántos registros hay en una tabla"""
        try:
            with connection.cursor() as cursor:
                cursor.execute(f"SELECT COUNT(*) FROM {tabla}")
                return cursor.fetchone()[0]
        except:
            return 0

    def ejecutar_sql_seguro(self, cursor, sql, descripcion):
        """Ejecutar SQL de forma segura, manejando duplicados"""
        try:
            cursor.execute(sql)
            affected = cursor.rowcount
            if affected > 0:
                self.stdout.write(
                    self.style.SUCCESS(f'✅ {descripcion}: {affected} registros insertados')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'⚠️ {descripcion}: 0 registros insertados')
                )
            return affected
        except Exception as e:
            error_str = str(e).lower()
            if any(keyword in error_str for keyword in ["duplicate", "duplicada", "unique", "already exists"]):
                self.stdout.write(
                    self.style.WARNING(f'⚠️ {descripcion}: Datos ya existen (ignorado)')
                )
                return 0
            else:
                self.stdout.write(
                    self.style.ERROR(f'❌ {descripcion}: {str(e)[:100]}...')
                )
                raise e

    def limpiar_tablas(self):
        """Limpiar todas las tablas en orden correcto"""
        self.stdout.write(self.style.WARNING('🧹 Limpiando tablas...'))
        
        tablas_orden = [
            'evento_seguridad', 'pago', 'cuota', 'reserva', 'reporte', 
            'mantenimiento', 'aviso', 'vehiculo_autorizado', 'persona_autorizada',
            'camara', 'zona', 'unidad_habitacional', 'usuario_rol',
            'area_comun', 'tipo_evento', 'usuario', 'rol'
        ]
        
        with connection.cursor() as cursor:
            for tabla in tablas_orden:
                try:
                    cursor.execute(f"DELETE FROM {tabla}")
                    count = cursor.rowcount
                    if count > 0:
                        self.stdout.write(f'  🗑️ {tabla}: {count} registros eliminados')
                    else:
                        self.stdout.write(f'  ✅ {tabla}: ya estaba vacía')
                except Exception as e:
                    if "does not exist" in str(e).lower():
                        self.stdout.write(f'  ℹ️ {tabla}: tabla no existe')
                    else:
                        self.stdout.write(f'  ⚠️ {tabla}: {str(e)[:50]}...')

    def mostrar_estado(self):
        """Mostrar el estado actual de la base de datos"""
        self.stdout.write('\n📊 ESTADO ACTUAL DE LA BASE DE DATOS:')
        self.stdout.write('='*60)
        
        tablas_principales = [
            'rol', 'usuario', 'usuario_rol', 'area_comun', 'tipo_evento',
            'unidad_habitacional', 'vehiculo_autorizado', 'reserva', 
            'cuota', 'pago', 'mantenimiento', 'aviso', 'evento_seguridad'
        ]
        
        total_registros = 0
        for tabla in tablas_principales:
            count = self.verificar_registros(tabla)
            total_registros += count
            status = "✅" if count > 0 else "🔹"
            self.stdout.write(f'  {status} {tabla:20} : {count:4} registros')
        
        self.stdout.write('='*60)
        self.stdout.write(f'📈 TOTAL DE REGISTROS: {total_registros}')
        return total_registros

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.HTTP_INFO('🚀 SMART CONDOMINIUM - POBLADO MEJORADO')
        )
        self.stdout.write(
            self.style.HTTP_INFO(f'📅 {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}')
        )
        
        # Si solo queremos verificar el estado
        if options['check_only']:
            self.mostrar_estado()
            return
        
        # Verificar estado inicial
        registros_iniciales = self.mostrar_estado()
        
        if registros_iniciales > 0 and not options['force']:
            self.stdout.write(
                self.style.WARNING(f'\n⚠️ La base ya tiene {registros_iniciales} registros')
            )
            if not options['clear']:
                self.stdout.write('💡 Continuando con inserción (ignorando duplicados)...')
                self.stdout.write('💡 Usa --clear para limpiar antes o --force para forzar')
        
        if options['clear']:
            confirm = input('⚠️ ¿CONFIRMAS limpiar TODOS los datos? (escribe SI): ')
            if confirm != 'SI':
                self.stdout.write(self.style.ERROR('❌ Operación cancelada'))
                return
            self.limpiar_tablas()
        
        total_insertados = 0
        
        try:
            # Usar savepoints individuales en lugar de una transacción completa
            self.stdout.write('\n🚀 INICIANDO POBLADO...\n')
            
            with connection.cursor() as cursor:
                # 1. ROLES
                self.stdout.write('👥 POBLANDO ROLES:')
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
                total_insertados += self.ejecutar_sql_seguro(
                    cursor, sql_roles, "Inserción de roles básicos"
                )
                
                # 2. USUARIO ADMINISTRADOR
                self.stdout.write('\n🔐 CREANDO USUARIO ADMINISTRADOR:')
                sql_admin = """
                INSERT INTO usuario (nombre, email, password, telefono, tipo, activo)
                VALUES ('Admin Sistema', 'admin@smartcondominium.com', 
                       crypt('admin123', gen_salt('bf')), '+1234567890', 
                       'administrador', TRUE)
                ON CONFLICT (email) DO NOTHING;
                """
                total_insertados += self.ejecutar_sql_seguro(
                    cursor, sql_admin, "Usuario administrador principal"
                )
                
                # 3. VERIFICAR SI NECESITAMOS MÁS USUARIOS
                count_usuarios = self.verificar_registros('usuario')
                if count_usuarios < 5:
                    self.stdout.write('\n👤 AGREGANDO USUARIOS ADICIONALES:')
                    sql_usuarios = """
                    INSERT INTO usuario (nombre, email, password, telefono, tipo, activo) VALUES
                    ('Carlos Rodríguez', 'carlos.rodriguez@email.com', crypt('password123', gen_salt('bf')), '+1234567891', 'propietario', TRUE),
                    ('María González', 'maria.gonzalez@email.com', crypt('password123', gen_salt('bf')), '+1234567892', 'propietario', TRUE),
                    ('Juan Pérez', 'juan.perez@email.com', crypt('password123', gen_salt('bf')), '+1234567893', 'propietario', TRUE),
                    ('Jorge Flores', 'jorge.flores@email.com', crypt('password123', gen_salt('bf')), '+1234567801', 'seguridad', TRUE)
                    ON CONFLICT (email) DO NOTHING;
                    """
                    total_insertados += self.ejecutar_sql_seguro(
                        cursor, sql_usuarios, "Usuarios adicionales del sistema"
                    )
                else:
                    self.stdout.write(f'\n✅ Ya hay {count_usuarios} usuarios registrados')
                
                # 4. ÁREAS COMUNES
                count_areas = self.verificar_registros('area_comun')
                if count_areas < 5:
                    self.stdout.write('\n🏛️ POBLANDO ÁREAS COMUNES:')
                    sql_areas = """
                    INSERT INTO area_comun (nombre, descripcion, capacidad, precio_hora, horario_disponible, activa) VALUES
                    ('Salón de Eventos', 'Amplio salón para eventos sociales', 100, 50.00, '08:00-22:00', TRUE),
                    ('Piscina', 'Piscina climatizada con área de descanso', 30, 20.00, '07:00-20:00', TRUE),
                    ('Gimnasio', 'Gimnasio equipado con máquinas de última generación', 15, 10.00, '05:00-23:00', TRUE),
                    ('Cancha de Tenis', 'Cancha de tenis con superficie profesional', 4, 15.00, '07:00-21:00', TRUE),
                    ('Biblioteca', 'Espacio tranquilo con colección de libros', 15, 0.00, '08:00-20:00', TRUE),
                    ('Terraza', 'Terraza con vista panorámica y asadores', 25, 25.00, '10:00-23:00', TRUE)
                    ON CONFLICT (nombre) DO NOTHING;
                    """
                    total_insertados += self.ejecutar_sql_seguro(
                        cursor, sql_areas, "Áreas comunes del condominio"
                    )
                else:
                    self.stdout.write(f'\n✅ Ya hay {count_areas} áreas comunes registradas')
                
                # 5. TIPOS DE EVENTOS
                count_tipos = self.verificar_registros('tipo_evento')
                if count_tipos < 5:
                    self.stdout.write('\n🚨 POBLANDO TIPOS DE EVENTOS:')
                    sql_tipos = """
                    INSERT INTO tipo_evento (nombre, descripcion, severidad) VALUES
                    ('Acceso no autorizado', 'Intento de acceso sin autorización', 'alta'),
                    ('Vehículo no reconocido', 'Vehículo no registrado intentando ingresar', 'media'),
                    ('Actividad sospechosa', 'Comportamiento inusual o sospechoso', 'media'),
                    ('Emergencia médica', 'Situación que requiere atención médica', 'alta'),
                    ('Acceso autorizado', 'Acceso permitido y registrado', 'baja'),
                    ('Visitante registrado', 'Ingreso de visitante previamente registrado', 'baja')
                    ON CONFLICT (nombre) DO NOTHING;
                    """
                    total_insertados += self.ejecutar_sql_seguro(
                        cursor, sql_tipos, "Tipos de eventos de seguridad"
                    )
                else:
                    self.stdout.write(f'\n✅ Ya hay {count_tipos} tipos de eventos registrados')
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'❌ Error crítico durante el poblado: {e}')
            )
            return
            
        # Mostrar estado final
        self.stdout.write('\n' + '='*70)
        self.stdout.write(self.style.SUCCESS('✅ POBLADO COMPLETADO'))
        self.stdout.write(f'📊 Registros insertados en esta ejecución: {total_insertados}')
        
        self.mostrar_estado()
        
        if total_insertados > 0:
            self.stdout.write('\n🔑 CREDENCIALES DEL ADMINISTRADOR:')
            self.stdout.write('📧 Email: admin@smartcondominium.com')
            self.stdout.write('🔒 Password: admin123')
            self.stdout.write('\n💡 Usa estas credenciales para acceder al admin de Django')
            
        self.stdout.write('\n🎉 ¡Listo! La base de datos está poblada y lista para usar.')
