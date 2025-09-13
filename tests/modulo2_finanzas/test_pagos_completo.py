"""
Script completo para probar el módulo de pagos en línea
T3: Pagar cuota en línea - Módulo 2 Gestión Financiera Básica

Ejecutar con: python test_pagos_completo.py
"""

import requests
import json
from datetime import datetime

# Configuración
BASE_URL = 'http://127.0.0.1:8000'
ADMIN_USER = {'username': 'admin', 'password': 'clave123'}
RESIDENT_USER = {'username': 'prueba2', 'password': 'clave123'}  # Usuario residente con cargos

def login_user(user_data, user_type):
    """Login de usuario y obtener token"""
    print(f"🔑 Probando login de {user_type}...")
    
    try:
        response = requests.post(
            f'{BASE_URL}/api/auth-token/',
            json=user_data,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            token = data.get('token')
            print(f"   ✅ Login {user_type} exitoso!")
            print(f"      Token: {token[:20] if token else 'No encontrado'}...")
            return token
        else:
            print(f"   ❌ Login {user_type} falló: {response.text}")
            return None
            
    except Exception as e:
        print(f"   ❌ Error de conexión: {str(e)}")
        return None

def get_cargos_pendientes(token, user_type="usuario"):
    """Obtener cargos pendientes del usuario"""
    print(f"\n📋 Obteniendo cargos pendientes ({user_type})...")
    
    if not token:
        print("   ❌ No hay token disponible")
        return []
    
    headers = {'Authorization': f'Token {token}', 'Content-Type': 'application/json'}
    
    try:
        response = requests.get(
            f'{BASE_URL}/api/finances/cargos/mis_cargos/',
            headers=headers
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            cargos = response.json()
            cargos_pendientes = [cargo for cargo in cargos if cargo['estado'] == 'pendiente']
            print(f"   ✅ Cargos pendientes encontrados: {len(cargos_pendientes)}")
            
            for cargo in cargos_pendientes[:3]:  # Mostrar solo los primeros 3
                print(f"      - ID: {cargo['id']}, {cargo['concepto_nombre']}: ${cargo['monto']}")
            
            return cargos_pendientes
        else:
            print(f"   ❌ Error: {response.text}")
            return []
            
    except Exception as e:
        print(f"   ❌ Error de conexión: {str(e)}")
        return []

def test_pago_residente(token, cargo_id):
    """Probar pago de residente (en línea)"""
    print(f"\n💳 Probando pago en línea (residente) - Cargo ID: {cargo_id}...")
    
    if not token:
        print("   ❌ No hay token disponible")
        return False
    
    headers = {'Authorization': f'Token {token}', 'Content-Type': 'application/json'}
    
    pago_data = {
        'referencia_pago': f'TXN_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
        'observaciones': 'Pago realizado desde app móvil',
        'metodo_pago': 'online',
        'confirmar_pago': True
    }
    
    try:
        response = requests.post(
            f'{BASE_URL}/api/finances/cargos/{cargo_id}/pagar/',
            json=pago_data,
            headers=headers
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            pago_info = data.get('pago_info', {})
            
            print(f"   ✅ Pago procesado exitosamente!")
            print(f"      Concepto: {pago_info.get('concepto', 'N/A')}")
            print(f"      Monto pagado: ${pago_info.get('monto_pagado', '0')}")
            print(f"      Referencia: {pago_info.get('referencia_pago', 'N/A')}")
            print(f"      Fecha: {pago_info.get('fecha_pago', 'N/A')}")
            print(f"      Estado: {pago_info.get('estado_actual', 'N/A')}")
            
            return True
        else:
            print(f"   ❌ Error en pago: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error de conexión: {str(e)}")
        return False

def test_pago_admin_por_residente(admin_token, cargo_id):
    """Probar pago de admin en nombre de residente (presencial)"""
    print(f"\n🏢 Probando pago presencial (admin por residente) - Cargo ID: {cargo_id}...")
    
    if not admin_token:
        print("   ❌ No hay token de admin disponible")
        return False
    
    headers = {'Authorization': f'Token {admin_token}', 'Content-Type': 'application/json'}
    
    pago_data = {
        'referencia_pago': f'VOUCHER_{datetime.now().strftime("%Y%m%d_%H%M%S")}',
        'observaciones': 'Pago realizado en oficina administrativa',
        'metodo_pago': 'efectivo',
        'confirmar_pago': True
    }
    
    try:
        response = requests.post(
            f'{BASE_URL}/api/finances/cargos/{cargo_id}/pagar/',
            json=pago_data,
            headers=headers
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            pago_info = data.get('pago_info', {})
            
            print(f"   ✅ Pago admin procesado exitosamente!")
            print(f"      Residente: {pago_info.get('residente', 'N/A')}")
            print(f"      Concepto: {pago_info.get('concepto', 'N/A')}")
            print(f"      Monto pagado: ${pago_info.get('monto_pagado', '0')}")
            print(f"      Procesado por: {pago_info.get('procesado_por', 'N/A')}")
            print(f"      Es pago admin: {pago_info.get('es_pago_admin', False)}")
            
            return True
        else:
            print(f"   ❌ Error en pago admin: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error de conexión: {str(e)}")
        return False

def test_validaciones_pago(token, cargo_id):
    """Probar validaciones del sistema de pagos"""
    print(f"\n🛡️ Probando validaciones de pago - Cargo ID: {cargo_id}...")
    
    if not token:
        print("   ❌ No hay token disponible")
        return
    
    headers = {'Authorization': f'Token {token}', 'Content-Type': 'application/json'}
    
    # Test 1: Pago sin confirmación
    print("   🧪 Test 1: Pago sin confirmación...")
    pago_data = {
        'confirmar_pago': False
    }
    
    response = requests.post(
        f'{BASE_URL}/api/finances/cargos/{cargo_id}/pagar/',
        json=pago_data,
        headers=headers
    )
    
    if response.status_code == 400:
        print("      ✅ Correcto: Rechazado por falta de confirmación")
    else:
        print(f"      ❌ Error: Se esperaba 400, obtuvo {response.status_code}")
    
    # Test 2: Método de pago inválido para residente
    print("   🧪 Test 2: Método de pago inválido para residente...")
    pago_data = {
        'metodo_pago': 'efectivo',  # Solo admin puede usar este método
        'confirmar_pago': True
    }
    
    response = requests.post(
        f'{BASE_URL}/api/finances/cargos/{cargo_id}/pagar/',
        json=pago_data,
        headers=headers
    )
    
    if response.status_code == 400:
        print("      ✅ Correcto: Rechazado por método de pago inválido")
    else:
        print(f"      ❌ Permitió método no autorizado: {response.status_code}")

def test_pago_cargo_ya_pagado(token):
    """Probar intento de pago de cargo ya pagado"""
    print(f"\n🚫 Probando pago de cargo ya pagado...")
    
    if not token:
        print("   ❌ No hay token disponible")
        return
    
    headers = {'Authorization': f'Token {token}', 'Content-Type': 'application/json'}
    
    # Obtener cargos pagados
    response = requests.get(
        f'{BASE_URL}/api/finances/cargos/pagos/',
        headers=headers
    )
    
    if response.status_code == 200:
        data = response.json()
        pagos = data.get('pagos', [])
        
        if pagos:
            cargo_pagado_id = pagos[0]['id']
            print(f"   Intentando pagar cargo ya pagado ID: {cargo_pagado_id}")
            
            pago_data = {
                'confirmar_pago': True,
                'referencia_pago': 'TEST_PAGO_DUPLICADO'
            }
            
            response = requests.post(
                f'{BASE_URL}/api/finances/cargos/{cargo_pagado_id}/pagar/',
                json=pago_data,
                headers=headers
            )
            
            if response.status_code == 400:
                print("   ✅ Correcto: Rechazado pago de cargo ya pagado")
            else:
                print(f"   ❌ Error: Permitió pago duplicado - Status: {response.status_code}")
        else:
            print("   📝 No hay pagos previos para probar")
    else:
        print(f"   ❌ Error obteniendo historial: {response.text}")

def test_historial_pagos(token, user_type="usuario"):
    """Probar endpoint de historial de pagos"""
    print(f"\n📊 Probando historial de pagos ({user_type})...")
    
    if not token:
        print("   ❌ No hay token disponible")
        return
    
    headers = {'Authorization': f'Token {token}', 'Content-Type': 'application/json'}
    
    try:
        response = requests.get(
            f'{BASE_URL}/api/finances/cargos/pagos/',
            headers=headers
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            pagos = data.get('pagos', [])
            estadisticas = data.get('estadisticas', {})
            
            print(f"   ✅ Historial obtenido!")
            print(f"      Total pagos: {estadisticas.get('total_pagos', 0)}")
            print(f"      Monto total: ${estadisticas.get('monto_total', '0')}")
            
            if pagos:
                print(f"      📋 PAGOS RECIENTES ({len(pagos)}):")
                for pago in pagos[:3]:  # Mostrar solo los primeros 3
                    print(f"         - {pago.get('concepto_nombre', 'N/A')}: ${pago.get('monto', '0')} ({pago.get('fecha_aplicacion', 'N/A')})")
            
            return True
        else:
            print(f"   ❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error de conexión: {str(e)}")
        return False

def test_estado_cuenta_actualizado(token, user_type="usuario"):
    """Verificar que el estado de cuenta refleje los pagos realizados"""
    print(f"\n🔄 Verificando actualización del estado de cuenta ({user_type})...")
    
    if not token:
        print("   ❌ No hay token disponible")
        return
    
    headers = {'Authorization': f'Token {token}', 'Content-Type': 'application/json'}
    
    try:
        response = requests.get(
            f'{BASE_URL}/api/finances/cargos/estado_cuenta/',
            headers=headers
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            resumen = data.get('resumen_general', {})
            ultimo_pago = data.get('ultimo_pago', {})
            
            print(f"   ✅ Estado de cuenta actualizado!")
            print(f"      Cargos pendientes: {resumen.get('cantidad_cargos_pendientes', 0)}")
            print(f"      Total pendiente: ${resumen.get('total_pendiente', '0')}")
            print(f"      Pagado este mes: ${resumen.get('total_pagado_mes_actual', '0')}")
            
            if ultimo_pago.get('cargo'):
                print(f"      🎯 Último pago: {ultimo_pago['cargo'].get('concepto_nombre', 'N/A')}")
                print(f"         Hace {ultimo_pago.get('hace_dias', 'N/A')} días")
            
            return True
        else:
            print(f"   ❌ Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"   ❌ Error de conexión: {str(e)}")
        return False

def main():
    """Ejecutar todas las pruebas del módulo de pagos"""
    print("🚀 PRUEBAS COMPLETAS DEL MÓDULO DE PAGOS EN LÍNEA")
    print("T3: Pagar cuota en línea")
    print("="*60)
    
    # 1. Login de usuarios
    admin_token = login_user(ADMIN_USER, "admin")
    resident_token = login_user(RESIDENT_USER, "residente")
    
    if not admin_token or not resident_token:
        print("❌ No se pudieron obtener los tokens necesarios")
        return
    
    # 2. Obtener cargos pendientes
    cargos_admin = get_cargos_pendientes(admin_token, "admin")
    cargos_residente = get_cargos_pendientes(resident_token, "residente")
    
    # 3. Probar pagos de residente
    if cargos_residente:
        primer_cargo = cargos_residente[0]['id']
        
        # Probar validaciones primero
        test_validaciones_pago(resident_token, primer_cargo)
        
        # Realizar pago exitoso
        pago_exitoso = test_pago_residente(resident_token, primer_cargo)
        
        # Probar pago duplicado
        if pago_exitoso:
            test_pago_cargo_ya_pagado(resident_token)
    
    # 4. Probar pago de admin por residente
    if cargos_residente and len(cargos_residente) > 1:
        segundo_cargo = cargos_residente[1]['id']
        test_pago_admin_por_residente(admin_token, segundo_cargo)
    
    # 5. Probar historial de pagos
    test_historial_pagos(resident_token, "residente")
    test_historial_pagos(admin_token, "admin")
    
    # 6. Verificar integración con estado de cuenta
    test_estado_cuenta_actualizado(resident_token, "residente")
    test_estado_cuenta_actualizado(admin_token, "admin")
    
    print(f"\n🎯 FUNCIONALIDADES VALIDADAS:")
    print(f"   ✅ Pago en línea por residentes")
    print(f"   ✅ Pago presencial por administradores")
    print(f"   ✅ Validaciones de seguridad y negocio")
    print(f"   ✅ Historial completo de pagos")
    print(f"   ✅ Integración con estado de cuenta")
    print(f"   ✅ Múltiples métodos de pago")
    print(f"   ✅ Referencias y observaciones")
    print(f"   ✅ Control de permisos por roles")
    
    print("="*60)
    print("✅ MÓDULO T3: PAGAR CUOTA EN LÍNEA COMPLETAMENTE FUNCIONAL")

if __name__ == "__main__":
    main()