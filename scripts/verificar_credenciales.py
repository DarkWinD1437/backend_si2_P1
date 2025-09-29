#!/usr/bin/env python
"""
Script para verificar credenciales de usuarios
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.append('.')
django.setup()

from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate

User = get_user_model()

def verificar_credenciales():
    """Verificar credenciales de usuarios"""

    usuarios_a_verificar = [
        ('admin', 'admin123'),
        ('admin', 'clave123'),
        ('residente01', 'residente123'),
        ('residente01', 'clave123'),
    ]

    print("🔍 VERIFICANDO CREDENCIALES DE USUARIOS")
    print("=" * 50)

    for username, password in usuarios_a_verificar:
        user = authenticate(username=username, password=password)
        if user:
            print(f"✅ {username} + {password} -> OK (Role: {user.role})")
        else:
            print(f"❌ {username} + {password} -> FAIL")

    print("\n👥 USUARIOS EXISTENTES:")
    users = User.objects.all()[:10]  # Primeros 10 usuarios
    for user in users:
        print(f"  - {user.username} (Role: {user.role})")

if __name__ == "__main__":
    verificar_credenciales()