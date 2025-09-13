"""
Script para corregir el rol del usuario prueba2
"""

import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from backend.apps.users.models import User

print("🔧 CORRIGIENDO ROL DEL USUARIO PRUEBA2")
print("="*50)

try:
    prueba2 = User.objects.get(username='prueba2')
    print(f"Antes - ID: {prueba2.id}, Role: {prueba2.role}")
    
    # Cambiar rol a resident
    prueba2.role = 'resident'
    prueba2.save()
    
    print(f"Después - ID: {prueba2.id}, Role: {prueba2.role}")
    print("✅ Rol corregido exitosamente")
    
except User.DoesNotExist:
    print("❌ Usuario prueba2 no encontrado")