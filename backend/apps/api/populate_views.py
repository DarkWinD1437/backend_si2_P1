"""
Vista para poblar la base de datos de producción via API
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model
from django.db import transaction
from backend.apps.users.models import User
from backend.apps.condominio.models import Rol, Usuario, AreaComun, Aviso
import random
from datetime import datetime, timedelta, date

User = get_user_model()

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def populate_database(request):
    """
    Endpoint para poblar la base de datos de producción
    Solo usuarios admin pueden ejecutarlo
    """
    if not request.user.is_superuser:
        return Response({
            'error': 'Solo administradores pueden ejecutar esta acción'
        }, status=status.HTTP_403_FORBIDDEN)
    
    try:
        with transaction.atomic():
            result = {
                'usuarios': 0,
                'roles': 0,
                'areas_comunes': 0,
                'avisos': 0,
                'datos_financieros': 0,
                'mensaje': 'Base de datos poblada exitosamente'
            }
            
            # 1. Crear roles básicos del sistema
            roles_creados = crear_roles_sistema()
            result['roles'] = roles_creados
            
            # 2. Crear usuarios básicos del sistema
            usuarios_creados = crear_usuarios_basicos()
            result['usuarios'] = usuarios_creados
            
            # 3. Crear áreas comunes
            areas_creadas = crear_areas_comunes()
            result['areas_comunes'] = areas_creadas
            
            # 4. Crear avisos de ejemplo
            avisos_creados = crear_avisos_basicos()
            result['avisos'] = avisos_creados
            
            # 5. Crear datos financieros (usuarios condominio, unidades, cuotas y deudas)
            datos_financieros = crear_datos_financieros()
            result['datos_financieros'] = datos_financieros
            
            return Response(result, status=status.HTTP_200_OK)
            
    except Exception as e:
        return Response({
            'error': f'Error al poblar la base de datos: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def crear_roles_sistema():
    """Crear roles básicos del sistema"""
    roles_data = [
        {
            'nombre': 'Administrador',
            'descripcion': 'Administrador del condominio'
        },
        {
            'nombre': 'Conserje',
            'descripcion': 'Personal de conserjería'
        },
        {
            'nombre': 'Residente',
            'descripcion': 'Residente del condominio'
        },
        {
            'nombre': 'Seguridad',
            'descripcion': 'Personal de seguridad'
        }
    ]
    
    roles_creados = 0
    for rol_data in roles_data:
        if not Rol.objects.filter(nombre=rol_data['nombre']).exists():
            Rol.objects.create(**rol_data)
            roles_creados += 1
    
    return roles_creados


def crear_usuarios_basicos():
    """Crear usuarios básicos del sistema: 25 residentes y 5 seguridad"""
    
    # Nombres y apellidos para generar usuarios realistas
    nombres_masculinos = ['Carlos', 'Juan', 'Diego', 'Miguel', 'Luis', 'Pedro', 'José', 'Daniel', 'David', 'Mario', 'Roberto', 'Fernando', 'Eduardo', 'Andrés', 'Ricardo']
    nombres_femeninos = ['María', 'Ana', 'Carmen', 'Laura', 'Isabel', 'Patricia', 'Sofía', 'Lucía', 'Mónica', 'Elena', 'Andrea', 'Claudia', 'Paola', 'Alejandra', 'Valentina']
    apellidos = ['García', 'Rodríguez', 'González', 'Hernández', 'López', 'Martínez', 'Pérez', 'Sánchez', 'Ramírez', 'Cruz', 'Torres', 'Flores', 'Gómez', 'Díaz', 'Morales', 'Jiménez', 'Muñoz', 'Álvarez', 'Romero', 'Herrera']
    
    usuarios_creados = 0
    
    # Crear 1 administrador
    admin_data = {
        'username': 'admin',
        'email': 'admin@condominio.com',
        'first_name': 'Administrador',
        'last_name': 'Principal',
        'password': 'admin123',
        'role': 'admin',
        'phone': '3001234567'
    }
    
    if not User.objects.filter(username=admin_data['username']).exists():
        user = User.objects.create_user(
            username=admin_data['username'],
            email=admin_data['email'],
            first_name=admin_data['first_name'],
            last_name=admin_data['last_name'],
            password=admin_data['password'],
            role=admin_data['role'],
            phone=admin_data['phone']
        )
        user.is_staff = True
        user.is_superuser = True
        user.save()
        usuarios_creados += 1
    
    # Crear 5 personal de seguridad
    seguridad_nombres = ['Carlos', 'Diego', 'Miguel', 'Roberto', 'Fernando']
    for i, nombre in enumerate(seguridad_nombres, 1):
        apellido = random.choice(apellidos)
        usuario_data = {
            'username': f'seguridad{i}',
            'email': f'seguridad{i}@condominio.com',
            'first_name': nombre,
            'last_name': apellido,
            'password': 'seguridad123',
            'role': 'security',
            'phone': f'300123456{i}'
        }
        
        if not User.objects.filter(username=usuario_data['username']).exists():
            User.objects.create_user(**usuario_data)
            usuarios_creados += 1
    
    # Crear 25 residentes
    for i in range(1, 26):
        # Alternar entre nombres masculinos y femeninos
        if i % 2 == 0:
            nombre = random.choice(nombres_femeninos)
        else:
            nombre = random.choice(nombres_masculinos)
        
        apellido1 = random.choice(apellidos)
        apellido2 = random.choice(apellidos)
        
        usuario_data = {
            'username': f'residente{i:02d}',  # residente01, residente02, etc.
            'email': f'residente{i:02d}@email.com',
            'first_name': nombre,
            'last_name': f'{apellido1} {apellido2}',
            'password': 'residente123',
            'role': 'resident',
            'phone': f'31012345{i:02d}'
        }
        
        if not User.objects.filter(username=usuario_data['username']).exists():
            User.objects.create_user(**usuario_data)
            usuarios_creados += 1
    
    return usuarios_creados


def crear_areas_comunes():
    """Crear áreas comunes básicas"""
    areas_data = [
        {
            'nombre': 'Salón de Eventos',
            'descripcion': 'Salón para eventos y celebraciones',
            'capacidad': 100,
            'precio_hora': 50000.00,
            'activa': True
        },
        {
            'nombre': 'Gimnasio',
            'descripcion': 'Área de ejercicios y fitness',
            'capacidad': 20,
            'precio_hora': 0.00,
            'activa': True
        },
        {
            'nombre': 'Piscina',
            'descripcion': 'Piscina comunitaria',
            'capacidad': 50,
            'precio_hora': 0.00,
            'activa': True
        },
        {
            'nombre': 'BBQ',
            'descripcion': 'Zona de parrillas y asados',
            'capacidad': 30,
            'precio_hora': 25000.00,
            'activa': True
        }
    ]
    
    areas_creadas = 0
    for area_data in areas_data:
        if not AreaComun.objects.filter(nombre=area_data['nombre']).exists():
            AreaComun.objects.create(**area_data)
            areas_creadas += 1
    
    return areas_creadas


def crear_avisos_basicos():
    """Crear avisos de ejemplo"""
    avisos_data = [
        {
            'titulo': 'Mantenimiento de ascensores',
            'contenido': 'Se realizará mantenimiento preventivo de ascensores el próximo sábado de 8AM a 12PM.',
            'prioridad': 'media',
            'fecha_publicacion': date.today(),
            'fecha_expiracion': date.today() + timedelta(days=15)
        },
        {
            'titulo': 'Nueva normativa de mascotas',
            'contenido': 'Se recuerda a todos los residentes que las mascotas deben usar correa en las áreas comunes.',
            'prioridad': 'baja',
            'fecha_publicacion': date.today(),
            'fecha_expiracion': date.today() + timedelta(days=30)
        },
        {
            'titulo': 'Reunión de copropietarios',
            'contenido': 'Se convoca a reunión ordinaria para el 30 de este mes a las 7PM en el salón de eventos.',
            'prioridad': 'alta',
            'fecha_publicacion': date.today(),
            'fecha_expiracion': date.today() + timedelta(days=10)
        }
    ]
    
    avisos_creados = 0
    for aviso_data in avisos_data:
        if not Aviso.objects.filter(titulo=aviso_data['titulo']).exists():
            Aviso.objects.create(**aviso_data)
            avisos_creados += 1
    
    return avisos_creados


def crear_datos_financieros():
    """Crear datos financieros realistas: usuarios condominio, unidades y cuotas con deudas"""
    from backend.apps.condominio.models import UnidadHabitacional, Cuota, Pago
    
    # Obtener rol de residente
    try:
        rol_residente = Rol.objects.get(nombre='Residente')
    except Rol.DoesNotExist:
        return 0
    
    # Obtener usuarios de tipo resident del modelo User
    users_residentes = User.objects.filter(role='resident')[:25]  # Solo los primeros 25 residentes
    
    datos_creados = 0
    
    # Crear usuarios en el modelo Usuario de condominio y unidades habitacionales
    for i, user in enumerate(users_residentes, 1):
        # Crear usuario en el modelo condominio
        usuario_condo, created = Usuario.objects.get_or_create(
            nombre=user.first_name,
            apellido=user.last_name.split()[0] if ' ' in user.last_name else user.last_name,
            email=user.email,
            telefono=user.phone,
            defaults={
                'id_rol': rol_residente,
                'activo': True
            }
        )
        
        if created:
            datos_creados += 1
        
        # Crear unidad habitacional
        numero_unidad = f"{100 + i:03d}"  # 101, 102, 103, etc.
        unidad, created = UnidadHabitacional.objects.get_or_create(
            numero=numero_unidad,
            defaults={
                'id_usuariopropietario': usuario_condo,
                'tipo_unidad': random.choice(['apartamento', 'casa']),
                'area_m2': random.randint(60, 150),
                'activa': True
            }
        )
        
        if created:
            datos_creados += 1
            
            # Crear cuotas para los últimos 6 meses
            for mes_atras in range(6):
                fecha_vencimiento = date.today().replace(day=15) - timedelta(days=30 * mes_atras)
                
                # Algunos residentes tienen deudas (30% de probabilidad de no pagar)
                esta_pagada = random.random() > 0.3
                
                cuota = Cuota.objects.create(
                    id_unidadhabitacional=unidad,
                    monto=random.choice([150000, 180000, 200000, 220000]),  # Montos variados
                    fecha_vencimiento=fecha_vencimiento,
                    estado='pagada' if esta_pagada else 'pendiente',
                    concepto=f'Cuota administración {fecha_vencimiento.strftime("%B %Y")}',
                    tipo='administracion'
                )
                datos_creados += 1
                
                # Si está pagada, crear el pago correspondiente
                if esta_pagada:
                    Pago.objects.create(
                        id_cuota=cuota,
                        monto_pagado=cuota.monto,
                        fecha_pago=fecha_vencimiento + timedelta(days=random.randint(-5, 10)),
                        metodo_pago=random.choice(['efectivo', 'transferencia', 'cheque']),
                        referencia_pago=f'REF{random.randint(100000, 999999)}',
                        estado='aprobado'
                    )
                    datos_creados += 1
    
    return datos_creados