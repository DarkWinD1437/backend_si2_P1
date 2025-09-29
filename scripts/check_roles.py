"""
Script para verificar roles de usuarios en la base de datos
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from backend.apps.users.models import User

print("🔍 VERIFICANDO ROLES DE USUARIOS")
print("="*50)

# Verificar usuario admin
try:
    admin = User.objects.get(username='admin')
    print(f"Admin - ID: {admin.id}, Role: {admin.role}, Is_superuser: {admin.is_superuser}")
except User.DoesNotExist:
    print("Admin no encontrado")

# Verificar usuario prueba2
try:
    prueba2 = User.objects.get(username='prueba2')
    print(f"Prueba2 - ID: {prueba2.id}, Role: {prueba2.role}, Is_superuser: {prueba2.is_superuser}")
    
    # Verificar si tiene el atributo role
    print(f"HasAttr role: {hasattr(prueba2, 'role')}")
    print(f"Role value: {getattr(prueba2, 'role', 'NO_ROLE')}")
    
except User.DoesNotExist:
    print("Prueba2 no encontrado")

# Listar todos los usuarios con sus roles
print(f"\n📋 TODOS LOS USUARIOS:")
users = User.objects.all()
for user in users:
    print(f"   {user.id}: {user.username} - Role: {user.role} - Superuser: {user.is_superuser}")