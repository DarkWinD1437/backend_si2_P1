#!/usr/bin/env python3
import os
import sys
import django
from pathlib import Path

# Configurar Django
BASE_DIR = Path(__file__).resolve().parent
sys.path.append(str(BASE_DIR))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from backend.apps.users.models import User
from django.contrib.auth.hashers import make_password

def create_test_users():
    """Crear usuarios de prueba para React y Flutter"""
    users_data = [
        {
            'username': 'admin_smart', 
            'email': 'admin@smartcondominium.com', 
            'password': 'admin123', 
            'role': 'admin', 
            'first_name': 'Admin', 
            'last_name': 'Principal'
        },
        {
            'username': 'carlos', 
            'email': 'carlos.rodriguez@email.com', 
            'password': 'password123', 
            'role': 'resident', 
            'first_name': 'Carlos', 
            'last_name': 'Rodriguez'
        },
        {
            'username': 'maria', 
            'email': 'maria.gonzalez@email.com', 
            'password': 'password123', 
            'role': 'resident', 
            'first_name': 'Maria', 
            'last_name': 'Gonzalez'
        },
        {
            'username': 'seguridad', 
            'email': 'jorge.flores@email.com', 
            'password': 'security123', 
            'role': 'security', 
            'first_name': 'Jorge', 
            'last_name': 'Flores'
        },
    ]

    created_users = 0
    print("🔄 Creando usuarios de prueba...")
    
    for user_data in users_data:
        if not User.objects.filter(username=user_data['username']).exists():
            user = User.objects.create(
                username=user_data['username'],
                email=user_data['email'],
                password=make_password(user_data['password']),
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                role=user_data['role'],
                is_staff=user_data['role'] == 'admin',
                is_superuser=user_data['role'] == 'admin'
            )
            created_users += 1
            print(f'✅ Usuario creado: {user.username} ({user.email}) - {user.get_role_display()}')
        else:
            print(f'⚠️ Usuario ya existe: {user_data["username"]}')

    print(f'\n🎉 {created_users} usuarios nuevos creados para React/Flutter')
    
    # Mostrar todos los usuarios
    print("\n📋 USUARIOS DISPONIBLES:")
    for user in User.objects.all():
        print(f"  - {user.username} | {user.email} | {user.get_role_display()}")

if __name__ == "__main__":
    create_test_users()
