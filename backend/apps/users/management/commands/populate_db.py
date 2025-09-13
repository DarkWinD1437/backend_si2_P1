from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from django.db import transaction
from django.contrib.auth.hashers import make_password
import json
import os

User = get_user_model()

class Command(BaseCommand):
    help = 'Poblar la base de datos con datos iniciales'

    def add_arguments(self, parser):
        parser.add_argument(
            '--users',
            action='store_true',
            help='Poblar solo usuarios',
        )
        parser.add_argument(
            '--all',
            action='store_true',
            help='Poblar todas las tablas',
        )
        parser.add_argument(
            '--file',
            type=str,
            help='Archivo JSON con los datos a cargar',
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Limpiar tablas antes de poblar',
        )

    def handle(self, *args, **options):
        self.stdout.write(
            self.style.SUCCESS('🚀 Iniciando poblado de base de datos...')
        )

        try:
            with transaction.atomic():
                if options['clear']:
                    self.clear_database()
                
                if options['file']:
                    self.populate_from_file(options['file'])
                elif options['users']:
                    self.populate_users()
                elif options['all']:
                    self.populate_all()
                else:
                    self.populate_default()
                    
        except Exception as e:
            raise CommandError(f'Error al poblar la base de datos: {e}')

        self.stdout.write(
            self.style.SUCCESS('✅ Base de datos poblada exitosamente!')
        )

    def clear_database(self):
        """Limpiar las tablas antes de poblar"""
        self.stdout.write('🧹 Limpiando base de datos...')
        
        # Limpiar usuarios (excepto superusuarios)
        User.objects.filter(is_superuser=False).delete()
        
        self.stdout.write(
            self.style.WARNING('⚠️  Tablas limpiadas (superusuarios conservados)')
        )

    def populate_from_file(self, file_path):
        """Poblar desde archivo JSON"""
        self.stdout.write(f'📄 Cargando datos desde: {file_path}')
        
        if not os.path.exists(file_path):
            raise CommandError(f'El archivo {file_path} no existe')
            
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            
        # Poblar según la estructura del JSON
        if 'users' in data:
            self.create_users_from_data(data['users'])
            
        # Aquí puedes agregar más entidades según tus necesidades
        # if 'areas_comunes' in data:
        #     self.create_areas_comunes_from_data(data['areas_comunes'])

    def populate_users(self):
        """Poblar solo usuarios"""
        self.stdout.write('👥 Poblando usuarios...')
        
        users_data = self.get_default_users_data()
        self.create_users_from_data(users_data)

    def populate_all(self):
        """Poblar todas las tablas"""
        self.stdout.write('🏢 Poblando todas las entidades...')
        
        self.populate_users()
        # Aquí agregar más llamadas según necesites
        # self.populate_areas_comunes()
        # self.populate_reservas()

    def populate_default(self):
        """Poblado por defecto"""
        self.populate_users()

    def create_users_from_data(self, users_data):
        """Crear usuarios desde datos"""
        created_count = 0
        updated_count = 0
        
        for user_data in users_data:
            try:
                # Verificar si el usuario ya existe
                user, created = User.objects.get_or_create(
                    username=user_data['username'],
                    defaults={
                        'email': user_data['email'],
                        'first_name': user_data.get('first_name', ''),
                        'last_name': user_data.get('last_name', ''),
                        'password': make_password(user_data['password']),
                        'role': user_data.get('role', 'resident'),
                        'phone': user_data.get('phone', ''),
                        'address': user_data.get('address', ''),
                        'is_active': user_data.get('is_active', True),
                        'is_staff': user_data.get('is_staff', False),
                        'is_superuser': user_data.get('is_superuser', False),
                    }
                )
                
                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ Usuario creado: {user.username}')
                    )
                else:
                    updated_count += 1
                    self.stdout.write(
                        self.style.WARNING(f'⚠️  Usuario ya existe: {user.username}')
                    )
                    
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'❌ Error creando usuario {user_data["username"]}: {e}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'👥 Usuarios procesados - Creados: {created_count}, Ya existían: {updated_count}'
            )
        )

    def get_default_users_data(self):
        """Datos por defecto de usuarios"""
        return [
            {
                'username': 'admin',
                'email': 'admin@smartcondominium.com',
                'password': 'admin123',
                'first_name': 'Administrador',
                'last_name': 'Principal',
                'role': 'admin',
                'phone': '+1234567890',
                'is_staff': True,
                'is_superuser': True,
                'is_active': True,
            },
            {
                'username': 'carlos.rodriguez',
                'email': 'carlos.rodriguez@email.com',
                'password': 'password123',
                'first_name': 'Carlos',
                'last_name': 'Rodríguez',
                'role': 'resident',
                'phone': '+1234567891',
                'address': 'Departamento A101',
            },
            {
                'username': 'maria.gonzalez',
                'email': 'maria.gonzalez@email.com',
                'password': 'password123',
                'first_name': 'María',
                'last_name': 'González',
                'role': 'resident',
                'phone': '+1234567892',
                'address': 'Departamento A102',
            },
            {
                'username': 'security1',
                'email': 'security@smartcondominium.com',
                'password': 'security123',
                'first_name': 'Jorge',
                'last_name': 'Flores',
                'role': 'security',
                'phone': '+1234567801',
                'is_staff': True,
            },
        ]
