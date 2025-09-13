"""
Script simple para poblar la base de datos
Ejecutar con: python manage.py shell < populate_simple.py
"""

from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password

User = get_user_model()

def create_users():
    """Crear usuarios básicos"""
    users_data = [
        {
            'username': 'admin',
            'email': 'admin@smartcondominium.com',
            'password': 'admin123',
            'first_name': 'Administrador',
            'last_name': 'Principal',
            'role': 'admin',
            'is_staff': True,
            'is_superuser': True,
        },
        {
            'username': 'carlos.rodriguez',
            'email': 'carlos.rodriguez@email.com',
            'password': 'password123',
            'first_name': 'Carlos',
            'last_name': 'Rodríguez',
            'role': 'resident',
            'phone': '+1234567891',
        },
        {
            'username': 'security1',
            'email': 'security@smartcondominium.com',
            'password': 'security123',
            'first_name': 'Jorge',
            'last_name': 'Flores',
            'role': 'security',
            'is_staff': True,
        }
    ]
    
    created_count = 0
    for user_data in users_data:
        try:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    **user_data,
                    'password': make_password(user_data['password'])
                }
            )
            if created:
                created_count += 1
                print(f"✅ Usuario creado: {user.username}")
            else:
                print(f"⚠️ Usuario ya existe: {user.username}")
        except Exception as e:
            print(f"❌ Error creando {user_data['username']}: {e}")
    
    print(f"🎉 Proceso completado. {created_count} usuarios nuevos creados.")

# Ejecutar
if __name__ == "__main__":
    create_users()
else:
    # Si se ejecuta desde shell
    create_users()
