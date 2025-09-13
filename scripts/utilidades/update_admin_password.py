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

def update_admin_password():
    """Cambiar contraseña del admin a 'clave123'"""
    try:
        # Buscar usuario admin
        admin_user = User.objects.filter(username='admin').first()
        
        if admin_user:
            # Cambiar contraseña
            admin_user.password = make_password('clave123')
            admin_user.save()
            print(f"✅ Contraseña actualizada para usuario: {admin_user.username}")
            print(f"📧 Email: {admin_user.email}")
            print(f"🔑 Nueva contraseña: clave123")
        else:
            print("❌ Usuario 'admin' no encontrado")
        
        # Mostrar todos los usuarios y sus emails
        print("\n📋 USUARIOS DISPONIBLES:")
        for user in User.objects.all():
            print(f"  👤 {user.username} | {user.email} | {user.get_role_display()}")
            
        print(f"\n🎯 CREDENCIALES PARA PRUEBAS:")
        print(f"   Username: admin")
        print(f"   Password: clave123")
        
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    update_admin_password()
