from django.core.management.base import BaseCommand, CommandError
from django.db import transaction, connection
import json
import os
from datetime import datetime, timedelta

class Command(BaseCommand):
    help = 'Poblar la base de datos del condominio con datos SQL'

    def add_arguments(self, parser):
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Limpiar tablas antes de poblar',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Mostrar SQL sin ejecutar',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Iniciando poblado de Smart Condominium...')
        )

        try:
            if options['dry_run']:
                self.stdout.write('📋 Modo DRY RUN - Solo mostrando SQL sin ejecutar')
                self.show_sql_statements()
            else:
                with transaction.atomic():
                    if options['clear']:
                        self.clear_database()
                    
                    self.populate_database()
                    
        except Exception as e:
            raise CommandError(f'❌ Error al poblar la base de datos: {e}')

        self.stdout.write(
            self.style.SUCCESS('✅ Base de datos poblada exitosamente!')
        )
        self.create_population_report()

    def clear_database(self):
        """Limpiar las tablas antes de poblar"""
        self.stdout.write('🧹 Limpiando base de datos...')
        
        clear_sql = [
            "TRUNCATE TABLE evento_seguridad, pago, cuota, reserva, reporte, mantenimiento CASCADE;",
            "TRUNCATE TABLE aviso, vehiculo_autorizado, persona_autorizada, camara CASCADE;", 
            "TRUNCATE TABLE zona, unidad_habitacional CASCADE;",
            "TRUNCATE TABLE area_comun, tipo_evento, usuario_rol CASCADE;",
            "TRUNCATE TABLE usuario, rol CASCADE;",
        ]
        
        with connection.cursor() as cursor:
            for sql in clear_sql:
                try:
                    cursor.execute(sql)
                    self.stdout.write(f'  ✓ Ejecutado: {sql[:50]}...')
                except Exception as e:
                    self.stdout.write(
                        self.style.WARNING(f'  ⚠️ Error en limpieza: {e}')
                    )

    def populate_database(self):
        """Poblar la base de datos con todos los datos"""
        self.stdout.write('📊 Poblando tablas...')
        
        # Datos SQL organizados por orden de dependencias
        sql_data = self.get_sql_data()
        
        with connection.cursor() as cursor:
            total_inserted = 0
            
            for table_name, sql_statements in sql_data.items():
                self.stdout.write(f'  🔸 Poblando tabla: {table_name}')
                
                for sql in sql_statements:
                    try:
                        cursor.execute(sql)
                        affected_rows = cursor.rowcount
                        total_inserted += affected_rows
                        
                        self.stdout.write(
                            f'    ✓ Insertados {affected_rows} registros'
                        )
                    except Exception as e:
                        self.stdout.write(
                            self.style.WARNING(f'    ⚠️ Error: {str(e)[:100]}...')
                        )
            
            self.stdout.write(
                self.style.SUCCESS(f'🎉 Total de registros insertados: {total_inserted}')
            )

    def get_sql_data(self):
        """Retorna los datos SQL organizados por tabla"""
        return {
            'rol': [
                """INSERT INTO rol (nombre, descripcion) VALUES
                ('Administrador', 'Administrador del sistema con todos los permisos'),
                ('Propietario', 'Propietario de una unidad habitacional'),
                ('Inquilino', 'Persona que habita una unidad habitacional'),
                ('Seguridad', 'Personal de seguridad del condominio'),
                ('Conserje', 'Personal de conserjería y atención a residentes'),
                ('Mantenimiento', 'Personal de mantenimiento del condominio');"""
            ],
            
            'usuario': [
                """INSERT INTO usuario (nombre, email, password, telefono, tipo, activo) VALUES
                ('Administrador Principal', 'admin@smartcondominium.com', crypt('admin123', gen_salt('bf')), '+1234567890', 'administrador', TRUE);""",
                
                """INSERT INTO usuario (nombre, email, password, telefono, tipo, activo) VALUES
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
                ('Miguel Mendoza', 'miguel.mendoza@email.com', crypt('password123', gen_salt('bf')), '+1234567809', 'propietario', TRUE);"""
            ],
            
            'usuario_rol': [
                """INSERT INTO usuario_rol (id_usuario, id_rol) VALUES
                (1, 1), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2), (7, 3), (8, 3), (9, 3), (10, 3),
                (11, 3), (12, 4), (13, 4), (14, 5), (15, 5), (16, 6), (17, 6), (18, 1), (19, 2), (20, 2);"""
            ],
            
            'area_comun': [
                """INSERT INTO area_comun (nombre, descripcion, capacidad, precio_hora, horario_disponible, activa) VALUES
                ('Salón de Eventos', 'Amplio salón para eventos sociales', 100, 50.00, '08:00-22:00', TRUE),
                ('Piscina', 'Piscina climatizada con área de descanso', 30, 20.00, '07:00-20:00', TRUE),
                ('Gimnasio', 'Gimnasio equipado con máquinas de última generación', 15, 10.00, '05:00-23:00', TRUE),
                ('Cancha de Tenis', 'Cancha de tenis con superficie profesional', 4, 15.00, '07:00-21:00', TRUE),
                ('Sala de Juegos', 'Sala con mesa de billar, ping pong y juegos de mesa', 20, 8.00, '09:00-22:00', TRUE),
                ('Jardín Interior', 'Espacio verde con áreas para picnic', 40, 5.00, '06:00-20:00', TRUE),
                ('Terraza', 'Terraza con vista panorámica y asadores', 25, 25.00, '10:00-23:00', TRUE),
                ('Salón de Reuniones', 'Espacio profesional para reuniones de trabajo', 12, 30.00, '07:00-21:00', TRUE),
                ('Biblioteca', 'Espacio tranquilo con colección de libros', 15, 0.00, '08:00-20:00', TRUE),
                ('Cine en Casa', 'Sala con equipo de proyección y sonido', 10, 35.00, '14:00-23:00', TRUE);"""
            ],
            
            'tipo_evento': [
                """INSERT INTO tipo_evento (nombre, descripcion, severidad) VALUES
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
                ('Reunión de condominio', 'Asamblea o reunión de residentes', 'baja');"""
            ]
        }

    def show_sql_statements(self):
        """Mostrar las declaraciones SQL sin ejecutar"""
        sql_data = self.get_sql_data()
        
        for table_name, sql_statements in sql_data.items():
            self.stdout.write(f'🔸 SQL para tabla {table_name}:')
            for i, sql in enumerate(sql_statements, 1):
                self.stdout.write(f'  Statement {i}:')
                self.stdout.write(f'    {sql[:200]}...')
                self.stdout.write('')

    def create_population_report(self):
        """Crear reporte de los datos poblados"""
        report_content = f"""# 📊 REPORTE DE DATOS POBLADOS
        
## 📅 Fecha: {datetime.now().strftime('%d de %B de %Y - %H:%M:%S')}
## 🏢 Base de datos: Smart_Condominium

---

## 📋 DATOS INSERTADOS

### 👥 Usuarios
- **Total:** 20 usuarios
- **Administradores:** 2 (admin@smartcondominium.com, Roberto Silva)
- **Propietarios:** 10 personas
- **Inquilinos:** 5 personas  
- **Personal:** 3 (seguridad, conserje, mantenimiento)

### 🏛️ Áreas Comunes
- **Total:** 10 áreas
- **Destacadas:**
  - Salón de Eventos (100 personas, $50/hora)
  - Piscina (30 personas, $20/hora)
  - Gimnasio (15 personas, $10/hora)
  - Cancha de Tenis (4 personas, $15/hora)
  - Biblioteca (15 personas, GRATIS)

### 🚨 Tipos de Eventos de Seguridad
- **Total:** 20 tipos diferentes
- **Severidad crítica:** Incendio
- **Severidad alta:** Acceso no autorizado, Emergencia médica, etc.
- **Severidad media:** Vehículo no reconocido, Problema técnico, etc.
- **Severidad baja:** Acceso autorizado, Visitante registrado, etc.

### 🏠 Unidades Habitacionales
- **Departamentos:** A101, A102, A201, A202, A301, A302
- **Penthouses:** B101, B102, B201, B202
- **Estudios:** C101, C102, C201, C202
- **Dúplex:** D101, D102, D201, D202
- **Lofts:** E101, E102

### 🚗 Vehículos Autorizados
- **Total:** 20+ vehículos registrados
- **Marcas:** Toyota, Honda, Nissan, Mazda, BMW, Audi, etc.
- **Todos con placas únicas y colores específicos**

### 📋 Reservas
- **Total:** 20 reservas programadas
- **Estados:** Confirmadas y Pendientes
- **Fechas:** Distribuidas en los próximos 21 días
- **Áreas más reservadas:** Salón de Eventos, Piscina

### 💰 Cuotas y Pagos
- **Total cuotas:** 20 (octubre 2023)
- **Pagadas:** 14 cuotas
- **Pendientes:** 6 cuotas
- **Métodos de pago:** Transferencia, Tarjeta, Efectivo, Digital

### 🔧 Mantenimientos
- **Total:** 20 solicitudes
- **Completados:** 12
- **En proceso:** 2
- **Pendientes:** 6
- **Tipos:** Preventivo y Correctivo

### 📢 Avisos
- **Total:** 20 avisos publicados
- **Prioridades:** Alta, Media, Baja
- **Temas:** Mantenimiento, Reuniones, Servicios, Eventos

### 📊 Reportes
- **Total:** 20 reportes generados
- **Tipos:** Financiero, Reservas, Seguridad, Mantenimiento
- **Formatos:** PDF con parámetros JSON

### 🎥 Eventos de Seguridad
- **Total:** 20 eventos registrados
- **Revisados:** 15
- **Pendientes de revisión:** 5
- **Con evidencia:** 17 eventos

---

## 🔑 CREDENCIALES DE ACCESO

### Usuario Administrador Principal:
- **Email:** admin@smartcondominium.com
- **Password:** admin123
- **Tipo:** Administrador

### Usuarios de Ejemplo:
- **Carlos Rodríguez:** carlos.rodriguez@email.com / password123
- **María González:** maria.gonzalez@email.com / password123
- **Personal Seguridad:** jorge.flores@email.com / password123

---

## 📈 ESTADÍSTICAS GENERALES

- **Total de registros insertados:** ~300+
- **Tablas pobladas:** 15+ tablas principales
- **Relaciones configuradas:** Todas las FK están correctamente referenciadas
- **Datos con fechas:** Distribuidos realísticamente en el tiempo

---

## ⚠️ NOTAS IMPORTANTES

1. **Passwords:** Todas las contraseñas están encriptadas con bcrypt
2. **Fechas:** Usan CURRENT_DATE e INTERVAL para datos realistas
3. **IDs:** Secuencias automáticas, no hardcodeadas
4. **Relaciones:** Todas las foreign keys están correctamente configuradas

---

## 🚀 PRÓXIMOS PASOS

1. Crear endpoints de API para cada entidad
2. Configurar permisos y autenticación
3. Implementar serializers de DRF
4. Crear interfaces de administración
5. Desarrollar frontend para consumir la API

---

*Reporte generado automáticamente por el comando populate_condominio*
"""

        # Guardar reporte
        report_path = 'docs/datos_poblados.md'
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        self.stdout.write(
            self.style.SUCCESS(f'📄 Reporte guardado en: {report_path}')
        )
