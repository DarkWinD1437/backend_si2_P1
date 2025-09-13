"""
Script para crear usuarios específicos para test de visualización
Ejecutar antes de test_visualizacion_avisos_completo.py
"""

import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from backend.apps.communications.models import Aviso

User = get_user_model()

def create_test_users():
    """Crear usuarios de prueba para todos los roles"""
    users_to_create = [
        {
            'username': 'admin_viz',
            'password': 'clave123',
            'email': 'admin_viz@test.com',
            'first_name': 'Admin',
            'last_name': 'Visualización',
            'role': 'admin'
        },
        {
            'username': 'resident1_viz',
            'password': 'clave123',
            'email': 'resident1_viz@test.com',
            'first_name': 'Residente',
            'last_name': 'Uno',
            'role': 'resident'
        },
        {
            'username': 'security1_viz',
            'password': 'clave123',
            'email': 'security1_viz@test.com',
            'first_name': 'Seguridad',
            'last_name': 'Uno',
            'role': 'security'
        }
    ]
    
    created_users = []
    
    print("🔧 Creando usuarios de prueba para visualización...")
    
    for user_data in users_to_create:
        username = user_data['username']
        
        # Verificar si el usuario ya existe
        if User.objects.filter(username=username).exists():
            print(f"   👤 Usuario {username} ya existe")
            user = User.objects.get(username=username)
            created_users.append(user)
            continue
        
        # Crear nuevo usuario
        try:
            user = User.objects.create_user(
                username=user_data['username'],
                password=user_data['password'],
                email=user_data['email'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                role=user_data['role']
            )
            created_users.append(user)
            print(f"   ✅ Usuario {username} creado exitosamente")
            
        except Exception as e:
            print(f"   ❌ Error creando usuario {username}: {e}")
    
    return created_users

def create_test_avisos():
    """Crear algunos avisos de prueba para los tests"""
    admin_user = User.objects.filter(role='admin').first()
    if not admin_user:
        print("❌ No hay usuario admin para crear avisos")
        return []
    
    avisos_to_create = [
        {
            'titulo': 'Aviso Urgente de Prueba',
            'contenido': 'Este es un aviso urgente para probar la visualización',
            'prioridad': 'urgente',
            'tipo_destinatario': 'todos',
            'estado': 'publicado',
            'es_fijado': True
        },
        {
            'titulo': 'Aviso para Residentes',
            'contenido': 'Este aviso está dirigido solo a residentes',
            'prioridad': 'media',
            'tipo_destinatario': 'residentes',
            'estado': 'publicado'
        },
        {
            'titulo': 'Aviso de Seguridad',
            'contenido': 'Aviso importante para el personal de seguridad',
            'prioridad': 'alta',
            'tipo_destinatario': 'seguridad',
            'estado': 'publicado'
        },
        {
            'titulo': 'Mantenimiento General',
            'contenido': 'Información sobre mantenimiento del edificio',
            'prioridad': 'baja',
            'tipo_destinatario': 'todos',
            'estado': 'publicado',
            'requiere_confirmacion': True
        }
    ]
    
    created_avisos = []
    
    print("📢 Creando avisos de prueba...")
    
    for aviso_data in avisos_to_create:
        # Verificar si ya existe un aviso similar
        existing = Aviso.objects.filter(titulo=aviso_data['titulo']).first()
        if existing:
            print(f"   📋 Aviso '{aviso_data['titulo']}' ya existe")
            created_avisos.append(existing)
            continue
        
        try:
            aviso = Aviso.objects.create(
                autor=admin_user,
                **aviso_data
            )
            
            # Publicar automáticamente
            if aviso.estado == 'publicado':
                aviso.publicar()
            
            created_avisos.append(aviso)
            print(f"   ✅ Aviso '{aviso.titulo}' creado exitosamente")
            
        except Exception as e:
            print(f"   ❌ Error creando aviso '{aviso_data['titulo']}': {e}")
    
    return created_avisos

def main():
    """Función principal"""
    print("🔧 CONFIGURANDO DATOS PARA TEST DE VISUALIZACIÓN")
    print("=" * 60)
    
    # Crear usuarios
    users = create_test_users()
    
    # Crear avisos de prueba
    avisos = create_test_avisos()
    
    print(f"\n📊 RESUMEN:")
    print(f"   👥 Usuarios creados/verificados: {len(users)}")
    print(f"   📢 Avisos creados/verificados: {len(avisos)}")
    
    print(f"\n🔑 CREDENCIALES PARA TESTS:")
    print(f"   👤 Admin: admin_viz / clave123")
    print(f"   👤 Residente: resident1_viz / clave123")  
    print(f"   👤 Seguridad: security1_viz / clave123")
    
    print(f"\n✅ Datos de prueba configurados correctamente")
    print(f"🧪 Ahora puedes ejecutar test_visualizacion_avisos_completo.py")

if __name__ == "__main__":
    main()