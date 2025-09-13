#!/usr/bin/env python
"""
Script para crear usuarios de prueba para el módulo de comunicaciones
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.append('.')
django.setup()

from django.contrib.auth import get_user_model
from rest_framework.authtoken.models import Token

User = get_user_model()

def crear_usuarios_comunicaciones():
    """Crear usuarios de prueba para comunicaciones"""
    
    print("🚀 CREANDO USUARIOS PARA MÓDULO DE COMUNICACIONES")
    
    usuarios = [
        {
            'username': 'admin_com',
            'email': 'admin@condominio.com',
            'first_name': 'Admin',
            'last_name': 'Comunicaciones',
            'role': 'admin',
            'password': 'admin123'
        },
        {
            'username': 'residente_com',
            'email': 'residente@condominio.com', 
            'first_name': 'Residente',
            'last_name': 'Prueba',
            'role': 'resident',
            'password': 'residente123'
        },
        {
            'username': 'seguridad_com',
            'email': 'seguridad@condominio.com',
            'first_name': 'Personal',
            'last_name': 'Seguridad',
            'role': 'security', 
            'password': 'seguridad123'
        }
    ]
    
    usuarios_creados = []
    
    for user_data in usuarios:
        username = user_data['username']
        
        # Verificar si ya existe
        if User.objects.filter(username=username).exists():
            print(f"⚠️  Usuario {username} ya existe, actualizando...")
            user = User.objects.get(username=username)
            user.set_password(user_data['password'])
            user.email = user_data['email']
            user.first_name = user_data['first_name']
            user.last_name = user_data['last_name']
            user.role = user_data['role']
            
            if user_data['role'] == 'admin':
                user.is_staff = True
                user.is_superuser = True
            
            user.save()
        else:
            print(f"✅ Creando usuario {username}...")
            user = User.objects.create_user(
                username=user_data['username'],
                email=user_data['email'],
                password=user_data['password'],
                first_name=user_data['first_name'],
                last_name=user_data['last_name'],
                role=user_data['role']
            )
            
            if user_data['role'] == 'admin':
                user.is_staff = True
                user.is_superuser = True
                user.save()
        
        # Crear o obtener token
        token, created = Token.objects.get_or_create(user=user)
        
        usuarios_creados.append({
            'user': user,
            'token': token.key,
            'password': user_data['password']
        })
        
        print(f"👤 Usuario: {user.username} | Rol: {user.role} | Token: {token.key[:20]}...")
    
    print(f"\n✅ {len(usuarios_creados)} usuarios listos para pruebas de comunicaciones")
    
    # Mostrar credenciales para pruebas
    print("\n" + "="*60)
    print("🔑 CREDENCIALES PARA PRUEBAS:")
    print("="*60)
    
    for user_info in usuarios_creados:
        user = user_info['user']
        print(f"Username: {user.username} | Password: {user_info['password']} | Rol: {user.role}")
    
    print("="*60)
    
    return usuarios_creados

if __name__ == "__main__":
    crear_usuarios_comunicaciones()