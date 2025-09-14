#!/usr/bin/env python3
"""
Script para dar permisos de superusuario al usuario admin
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

from backend.apps.users.models import User

def fix_admin_permissions():
    try:
        # Buscar al usuario admin
        admin_user = User.objects.get(username='admin')
        
        print(f"Usuario encontrado: {admin_user.username}")
        print(f"Estado actual:")
        print(f"  - Es superusuario: {admin_user.is_superuser}")
        print(f"  - Es staff: {admin_user.is_staff}")
        print(f"  - Está activo: {admin_user.is_active}")
        print(f"  - Rol: {admin_user.get_role_display() if hasattr(admin_user, 'role') else 'No definido'}")
        
        # Dar permisos de superusuario
        admin_user.is_superuser = True
        admin_user.is_staff = True
        admin_user.is_active = True
        
        # Si el modelo tiene un campo role, asignarlo como ADMIN
        if hasattr(admin_user, 'role'):
            # Verificar si existe el rol ADMIN
            if hasattr(admin_user, 'ADMIN'):
                admin_user.role = admin_user.ADMIN
            elif hasattr(admin_user._meta.get_field('role'), 'choices'):
                # Buscar en las choices el valor para admin
                choices = admin_user._meta.get_field('role').choices
                for choice_value, choice_label in choices:
                    if 'admin' in choice_label.lower() or 'administrador' in choice_label.lower():
                        admin_user.role = choice_value
                        break
        
        admin_user.save()
        
        print(f"\n✅ Permisos actualizados correctamente!")
        print(f"Estado nuevo:")
        print(f"  - Es superusuario: {admin_user.is_superuser}")
        print(f"  - Es staff: {admin_user.is_staff}")
        print(f"  - Está activo: {admin_user.is_active}")
        print(f"  - Rol: {admin_user.get_role_display() if hasattr(admin_user, 'role') else 'No definido'}")
        
        return True
        
    except User.DoesNotExist:
        print("❌ Error: El usuario 'admin' no existe en la base de datos")
        print("Usuarios disponibles:")
        for user in User.objects.all():
            print(f"  - {user.username}")
        return False
        
    except Exception as e:
        print(f"❌ Error inesperado: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Arreglando permisos del usuario admin...")
    success = fix_admin_permissions()
    
    if success:
        print("\n🎉 ¡Listo! Ahora puedes iniciar sesión como administrador con:")
        print("   Usuario: admin")
        print("   Contraseña: clave123")
    else:
        print("\n❌ No se pudieron corregir los permisos. Revisa los errores arriba.")