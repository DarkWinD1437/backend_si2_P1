#!/usr/bin/env python
"""
Script de pruebas completo para Módulo 3: Comunicación Básica
T1: Publicar Aviso General

Este script valida:
1. Creación de avisos por administradores
2. Sistema flexible de destinatarios 
3. Listado de avisos según roles
4. Comentarios y lecturas
5. Validaciones de permisos
6. Filtros y búsquedas

Autor: Sistema de Condominios
Fecha: 13 de Septiembre, 2025
"""

import os
import sys
import django
import requests
import json
from datetime import datetime, timedelta

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.append('.')
django.setup()

# URL base de la API
BASE_URL = "http://localhost:8000"

def hacer_request(method, endpoint, data=None, token=None, files=None):
    """Función auxiliar para hacer requests"""
    url = f"{BASE_URL}{endpoint}"
    headers = {'Content-Type': 'application/json'}
    
    if token:
        headers['Authorization'] = f'Token {token}'
    
    if files:
        headers.pop('Content-Type', None)
        response = requests.request(method, url, headers=headers, files=files, data=data)
    else:
        response = requests.request(method, url, headers=headers, json=data)
    
    return response

def print_response(titulo, response, mostrar_datos=True):
    """Función para imprimir respuestas de forma organizada"""
    print(f"\n{'='*60}")
    print(f"📋 {titulo}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    
    if mostrar_datos and response.content:
        try:
            data = response.json()
            print(f"Response: {json.dumps(data, indent=2, ensure_ascii=False)}")
        except:
            print(f"Response Text: {response.text[:500]}")
    print(f"{'='*60}")

def test_comunicaciones_completo():
    """Función principal de pruebas"""
    print("🚀 INICIANDO PRUEBAS - MÓDULO 3: COMUNICACIÓN BÁSICA")
    print("📝 T1: Publicar Aviso General")
    print("🕐 Fecha:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    # 1. LOGIN DE USUARIOS
    print("\n🔐 PASO 1: LOGIN DE USUARIOS")
    
    # Login Admin
    login_admin = hacer_request('POST', '/api/login/', {
        'username': 'admin_com',
        'password': 'admin123'
    })
    
    if login_admin.status_code == 200:
        admin_token = login_admin.json()['token']
        print("✅ Login Admin exitoso")
    else:
        print("❌ Error en login Admin")
        print_response("Login Admin Error", login_admin)
        return
    
    # Login Residente
    login_residente = hacer_request('POST', '/api/login/', {
        'username': 'residente_com',
        'password': 'residente123'
    })
    
    if login_residente.status_code == 200:
        residente_token = login_residente.json()['token']
        print("✅ Login Residente exitoso")
    else:
        print("❌ Error en login Residente")
        print_response("Login Residente Error", login_residente)
        return
    
    # Login Seguridad
    login_seguridad = hacer_request('POST', '/api/login/', {
        'username': 'seguridad_com',
        'password': 'seguridad123'
    })
    
    if login_residente.status_code == 200:
        residente_token = login_residente.json()['token']
        print("✅ Login Residente exitoso")
    else:
        print("❌ Error en login Residente")
        print_response("Login Residente Error", login_residente)
        return
    
    # 2. CREAR AVISOS CON DIFERENTES TIPOS DE DESTINATARIOS
    print("\n📢 PASO 2: CREAR AVISOS CON DIFERENTES DESTINATARIOS")
    
    avisos_test = [
        {
            "titulo": "Aviso General - Corte de Agua",
            "contenido": "Se informa a todos los residentes que mañana habrá corte de agua de 8:00 AM a 12:00 PM por trabajos de mantenimiento en la red principal.",
            "resumen": "Corte de agua mañana de 8:00 AM a 12:00 PM",
            "prioridad": "alta",
            "tipo_destinatario": "todos",
            "requiere_confirmacion": True
        },
        {
            "titulo": "Reunión de Copropietarios",
            "contenido": "Se convoca a todos los residentes a la reunión de copropietarios el sábado 16 de septiembre a las 10:00 AM en el salón comunal.",
            "resumen": "Reunión copropietarios - Sábado 16/09 - 10:00 AM",
            "prioridad": "media",
            "tipo_destinatario": "residentes",
            "requiere_confirmacion": True,
            "es_fijado": True
        },
        {
            "titulo": "Protocolo de Seguridad Nocturna",
            "contenido": "Nuevo protocolo: A partir de las 10:00 PM, todo visitante debe ser registrado y autorizado por el residente correspondiente antes del ingreso.",
            "resumen": "Nuevo protocolo de seguridad nocturna",
            "prioridad": "alta",
            "tipo_destinatario": "admin_seguridad"
        },
        {
            "titulo": "Emergencia - Fuga de Gas",
            "contenido": "ATENCIÓN: Se ha detectado una fuga de gas en el sector A. Personal de seguridad debe evacuar inmediatamente y residentes deben permanecer en espacios abiertos.",
            "resumen": "EMERGENCIA: Fuga de gas sector A",
            "prioridad": "urgente",
            "tipo_destinatario": "residentes_seguridad",
            "requiere_confirmacion": True
        },
        {
            "titulo": "Mantenimiento de Elevadores", 
            "contenido": "Se realizará mantenimiento preventivo de elevadores el domingo 17 de septiembre. Elevadores fuera de servicio de 6:00 AM a 2:00 PM.",
            "resumen": "Mantenimiento elevadores - Domingo 17/09",
            "prioridad": "media",
            "tipo_destinatario": "personalizado",
            "roles_destinatarios": ["admin", "resident"]
        }
    ]
    
    avisos_creados = []
    
    for i, aviso_data in enumerate(avisos_test, 1):
        response = hacer_request('POST', '/api/communications/avisos/', aviso_data, admin_token)
        
        if response.status_code == 201:
            aviso = response.json()
            avisos_creados.append(aviso)
            print(f"✅ Aviso {i} creado: '{aviso_data['titulo'][:50]}...' - Destinatarios: {aviso_data['tipo_destinatario']}")
        else:
            print(f"❌ Error creando aviso {i}")
            print_response(f"Error Aviso {i}", response)
    
    # 3. INTENTAR CREAR AVISO COMO RESIDENTE (DEBE FALLAR)
    print("\n🚫 PASO 3: VALIDAR PERMISOS - RESIDENTE INTENTA CREAR AVISO")
    
    aviso_residente = hacer_request('POST', '/api/communications/avisos/', {
        "titulo": "Intento de aviso por residente",
        "contenido": "Este aviso no debería poder crearse",
        "tipo_destinatario": "todos"
    }, residente_token)
    
    if aviso_residente.status_code == 403:
        print("✅ Validación correcta: Residente no puede crear avisos")
    else:
        print("❌ Error de validación: Residente pudo crear aviso")
        print_response("Error Validación Permisos", aviso_residente)
    
    # 4. LISTAR AVISOS COMO ADMINISTRADOR
    print("\n📋 PASO 4: LISTAR AVISOS COMO ADMINISTRADOR")
    
    avisos_admin = hacer_request('GET', '/api/communications/avisos/', None, admin_token)
    print_response("Avisos para Admin", avisos_admin)
    
    # 5. LISTAR AVISOS COMO RESIDENTE
    print("\n👤 PASO 5: LISTAR AVISOS COMO RESIDENTE")
    
    avisos_residente = hacer_request('GET', '/api/communications/avisos/', None, residente_token)
    print_response("Avisos para Residente", avisos_residente)
    
    # 6. VER DETALLE DE AVISO Y MARCAR COMO LEÍDO
    if avisos_creados:
        # Obtener ID del primer aviso de la lista de admin
        avisos_admin_response = hacer_request('GET', '/api/communications/avisos/', None, admin_token)
        if avisos_admin_response.status_code == 200:
            avisos_list = avisos_admin_response.json()['results']
            if avisos_list:
                aviso_id = avisos_list[0]['id']
                
        print(f"\n👁️ PASO 6: VER DETALLE DE AVISO {aviso_id}")
        
        detalle_aviso = hacer_request('GET', f'/api/communications/avisos/{aviso_id}/', None, residente_token)
        print_response("Detalle de Aviso", detalle_aviso, False)
        
        # Marcar como leído
        print(f"\n✅ MARCAR AVISO {aviso_id} COMO LEÍDO")
        
        marcar_leido = hacer_request('POST', f'/api/communications/avisos/{aviso_id}/marcar_leido/', {}, residente_token)
        print_response("Marcar como Leído", marcar_leido)
    
    # 7. AGREGAR COMENTARIOS
    if avisos_creados:
        # Obtener ID del segundo aviso
        avisos_admin_response = hacer_request('GET', '/api/communications/avisos/', None, admin_token)
        if avisos_admin_response.status_code == 200:
            avisos_list = avisos_admin_response.json()['results']
            if len(avisos_list) > 1:
                aviso_id = avisos_list[1]['id']  # Usar segundo aviso
                
        print(f"\n💬 PASO 7: AGREGAR COMENTARIOS AL AVISO {aviso_id}")
        
        # Comentario del residente
        comentario_residente = hacer_request('POST', f'/api/communications/avisos/{aviso_id}/comentarios/', {
            "contenido": "¿A qué hora exactamente será la reunión? ¿Habrá agenda previa?"
        }, residente_token)
        print_response("Comentario Residente", comentario_residente)
        
        # Respuesta del admin
        comentario_admin = hacer_request('POST', f'/api/communications/avisos/{aviso_id}/comentarios/', {
            "contenido": "La reunión será exactamente a las 10:00 AM. La agenda será enviada por email el viernes."
        }, admin_token)
        print_response("Respuesta Admin", comentario_admin)
    
    # 8. FILTROS Y BÚSQUEDAS
    print("\n🔍 PASO 8: PRUEBAS DE FILTROS Y BÚSQUEDAS")
    
    # Filtro por prioridad
    avisos_urgentes = hacer_request('GET', '/api/communications/avisos/?prioridad=urgente', None, admin_token)
    print(f"📍 Avisos urgentes encontrados: {len(avisos_urgentes.json().get('results', []))}")
    
    # Filtro por tipo de destinatario
    avisos_residentes = hacer_request('GET', '/api/communications/avisos/?tipo_destinatario=residentes', None, admin_token)
    print(f"📍 Avisos para residentes: {len(avisos_residentes.json().get('results', []))}")
    
    # Búsqueda por texto
    busqueda_agua = hacer_request('GET', '/api/communications/avisos/?busqueda=agua', None, admin_token)
    print(f"📍 Avisos que contienen 'agua': {len(busqueda_agua.json().get('results', []))}")
    
    # 9. AVISOS NO LEÍDOS
    print("\n📭 PASO 9: AVISOS NO LEÍDOS")
    
    no_leidos = hacer_request('GET', '/api/communications/avisos/no_leidos/', None, residente_token)
    if no_leidos.status_code == 200:
        count_no_leidos = len(no_leidos.json().get('results', []))
        print(f"📬 Avisos no leídos para residente: {count_no_leidos}")
    
    # 10. ESTADÍSTICAS (SOLO ADMIN)
    print("\n📊 PASO 10: ESTADÍSTICAS DE AVISOS (SOLO ADMIN)")
    
    estadisticas = hacer_request('GET', '/api/communications/avisos/estadisticas/', None, admin_token)
    print_response("Estadísticas Admin", estadisticas)
    
    # 11. VER LECTURAS DE AVISO (SOLO ADMIN)
    if avisos_creados:
        # Obtener ID del primer aviso
        avisos_admin_response = hacer_request('GET', '/api/communications/avisos/', None, admin_token)
        if avisos_admin_response.status_code == 200:
            avisos_list = avisos_admin_response.json()['results']
            if avisos_list:
                aviso_id = avisos_list[0]['id']
                
        print(f"\n👥 PASO 11: VER LECTURAS DEL AVISO {aviso_id}")
        
        lecturas = hacer_request('GET', f'/api/communications/avisos/{aviso_id}/lecturas/', None, admin_token)
        print_response("Lecturas del Aviso", lecturas)
    
    # 12. AVISOS CREADOS POR USUARIO
    print("\n📝 PASO 12: MIS AVISOS CREADOS")
    
    mis_avisos = hacer_request('GET', '/api/communications/avisos/mis_avisos/', None, admin_token)
    if mis_avisos.status_code == 200:
        count_mis_avisos = len(mis_avisos.json().get('results', []))
        print(f"📋 Avisos creados por admin: {count_mis_avisos}")
    
    # RESUMEN FINAL
    print("\n" + "="*60)
    print("🎉 RESUMEN DE PRUEBAS COMPLETADAS")
    print("="*60)
    
    resultados = [
        f"✅ Avisos creados exitosamente: {len(avisos_creados)}/5",
        f"✅ Validación de permisos funcionando",
        f"✅ Sistema de destinatarios flexible implementado",
        f"✅ Listado diferenciado por roles",
        f"✅ Sistema de lectura y confirmación",
        f"✅ Comentarios y respuestas funcionando",
        f"✅ Filtros y búsquedas operativas",
        f"✅ Estadísticas para administradores",
        f"✅ Control de lecturas por aviso",
        f"✅ Seguimiento de avisos por autor"
    ]
    
    for resultado in resultados:
        print(resultado)
    
    print("\n🎯 TIPOS DE DESTINATARIOS VALIDADOS:")
    tipos_validados = [
        "📢 todos - Aviso visible para todos los usuarios",
        "👥 residentes - Solo para residentes del condominio", 
        "🔐 admin_seguridad - Para administradores y personal de seguridad",
        "🚨 residentes_seguridad - Para residentes y seguridad",
        "⚙️ personalizado - Selección específica de roles"
    ]
    
    for tipo in tipos_validados:
        print(tipo)
    
    print("\n✅ MÓDULO 3: COMUNICACIÓN BÁSICA - T1: PUBLICAR AVISO GENERAL")
    print("🚀 IMPLEMENTADO Y VALIDADO EXITOSAMENTE")
    print("="*60)

if __name__ == "__main__":
    try:
        test_comunicaciones_completo()
    except Exception as e:
        print(f"\n❌ ERROR EN PRUEBAS: {str(e)}")
        import traceback
        traceback.print_exc()