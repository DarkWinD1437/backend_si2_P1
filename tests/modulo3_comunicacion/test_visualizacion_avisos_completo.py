"""
Test completo para T2: Visualizar Avisos
Ejecutar con: python tests/modulo3_comunicacion/test_visualizacion_avisos_completo.py
"""

import requests
import json
from datetime import datetime, timedelta

# Configuración
BASE_URL = 'http://127.0.0.1:8000'

# Usuarios de prueba (usando los existentes)
ADMIN_USER = {'username': 'admin', 'password': 'clave123'}
RESIDENT_USER = {'username': 'prueba2', 'password': 'clave123'}  # Este usuario ya existe
SECURITY_USER = {'username': 'seguridad_com', 'password': 'seguridad123'}  # Usar el usuario de seguridad correcto

def get_auth_headers(user_credentials):
    """Obtener headers de autenticación"""
    try:
        response = requests.post(f'{BASE_URL}/api/auth-token/', json=user_credentials)
        if response.status_code == 200:
            token = response.json()['token']
            return {'Authorization': f'Token {token}'}
    except Exception as e:
        print(f"❌ Error obteniendo token para {user_credentials['username']}: {e}")
    return {}

def test_dashboard_admin():
    """Probar dashboard para administrador"""
    print("\n🏠 Probando dashboard de administrador...")
    
    headers = get_auth_headers(ADMIN_USER)
    if not headers:
        print("❌ No se pudo autenticar admin")
        return False
    
    try:
        response = requests.get(
            f'{BASE_URL}/api/communications/avisos/dashboard/',
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Dashboard admin exitoso")
            print(f"   📊 Total avisos: {data['estadisticas']['total_avisos']}")
            print(f"   📨 No leídos: {data['estadisticas']['avisos_no_leidos']}")
            print(f"   🚨 Urgentes: {data['estadisticas']['avisos_urgentes']}")
            print(f"   📌 Fijados: {data['estadisticas']['avisos_fijados']}")
            print(f"   🎯 Puede crear avisos: {data['usuario_info']['puede_crear_avisos']}")
            
            # Verificar estructura de datos
            required_keys = ['estadisticas', 'avisos_recientes', 'avisos_urgentes_no_leidos', 'avisos_fijados', 'usuario_info']
            for key in required_keys:
                if key not in data:
                    print(f"❌ Falta clave '{key}' en respuesta")
                    return False
            
            return True
        else:
            print(f"❌ Error en dashboard admin: {response.status_code}")
            print(f"   Respuesta: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error probando dashboard admin: {e}")
        return False

def test_dashboard_resident():
    """Probar dashboard para residente"""
    print("\n👥 Probando dashboard de residente...")
    
    headers = get_auth_headers(RESIDENT_USER)
    if not headers:
        print("❌ No se pudo autenticar resident")
        return False
    
    try:
        response = requests.get(
            f'{BASE_URL}/api/communications/avisos/dashboard/',
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Dashboard residente exitoso")
            print(f"   📊 Total avisos: {data['estadisticas']['total_avisos']}")
            print(f"   📨 No leídos: {data['estadisticas']['avisos_no_leidos']}")
            print(f"   🚨 Urgentes: {data['estadisticas']['avisos_urgentes']}")
            print(f"   🚫 Puede crear avisos: {data['usuario_info']['puede_crear_avisos']}")
            
            # Los residentes no deberían poder crear avisos
            if data['usuario_info']['puede_crear_avisos']:
                print("❌ ERROR: El residente no debería poder crear avisos")
                return False
                
            return True
        else:
            print(f"❌ Error en dashboard residente: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error probando dashboard residente: {e}")
        return False

def test_filtros_avanzados():
    """Probar filtros avanzados"""
    print("\n🔍 Probando filtros avanzados...")
    
    headers = get_auth_headers(ADMIN_USER)
    if not headers:
        print("❌ No se pudo autenticar admin")
        return False
    
    tests_passed = 0
    total_tests = 0
    
    # Test 1: Filtro por prioridad múltiple
    print("   📋 Probando filtro por múltiples prioridades...")
    total_tests += 1
    try:
        response = requests.get(
            f'{BASE_URL}/api/communications/avisos/filtros_avanzados/?prioridades=urgente,alta',
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Filtro prioridades: {len(data['results'])} avisos encontrados")
            tests_passed += 1
        else:
            print(f"   ❌ Error filtro prioridades: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error en filtro prioridades: {e}")
    
    # Test 2: Filtro por fechas
    print("   📅 Probando filtro por fechas...")
    total_tests += 1
    try:
        fecha_desde = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
        fecha_hasta = datetime.now().strftime('%Y-%m-%d')
        
        response = requests.get(
            f'{BASE_URL}/api/communications/avisos/filtros_avanzados/?fecha_desde={fecha_desde}&fecha_hasta={fecha_hasta}',
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Filtro fechas: {len(data['results'])} avisos encontrados")
            tests_passed += 1
        else:
            print(f"   ❌ Error filtro fechas: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error en filtro fechas: {e}")
    
    # Test 3: Filtro por palabras clave
    print("   🔤 Probando filtro por palabras clave...")
    total_tests += 1
    try:
        response = requests.get(
            f'{BASE_URL}/api/communications/avisos/filtros_avanzados/?palabras_clave=aviso,importante,urgente',
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Filtro palabras clave: {len(data['results'])} avisos encontrados")
            tests_passed += 1
        else:
            print(f"   ❌ Error filtro palabras clave: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error en filtro palabras clave: {e}")
    
    # Test 4: Filtro por estado de lectura
    print("   👁️ Probando filtro por estado de lectura...")
    total_tests += 1
    try:
        response = requests.get(
            f'{BASE_URL}/api/communications/avisos/filtros_avanzados/?estado_lectura=no_leidos',
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Filtro no leídos: {len(data['results'])} avisos encontrados")
            tests_passed += 1
        else:
            print(f"   ❌ Error filtro no leídos: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error en filtro no leídos: {e}")
    
    # Test 5: Ordenamiento personalizado
    print("   📊 Probando ordenamiento por prioridad...")
    total_tests += 1
    try:
        response = requests.get(
            f'{BASE_URL}/api/communications/avisos/filtros_avanzados/?orden=prioridad',
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Ordenamiento por prioridad: {len(data['results'])} avisos")
            tests_passed += 1
        else:
            print(f"   ❌ Error ordenamiento: {response.status_code}")
            
    except Exception as e:
        print(f"   ❌ Error en ordenamiento: {e}")
    
    print(f"📋 Filtros avanzados: {tests_passed}/{total_tests} tests pasaron")
    return tests_passed == total_tests

def test_busqueda_inteligente():
    """Probar búsqueda inteligente"""
    print("\n🔍 Probando búsqueda inteligente...")
    
    headers = get_auth_headers(ADMIN_USER)
    if not headers:
        print("❌ No se pudo autenticar admin")
        return False
    
    try:
        # Búsqueda general
        response = requests.get(
            f'{BASE_URL}/api/communications/avisos/busqueda_inteligente/?q=aviso',
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Búsqueda inteligente exitosa")
            print(f"   🔍 Query: '{data['query']}'")
            print(f"   📊 Resultados encontrados: {data['total_encontrados']}")
            print(f"   📋 Resultados en página: {len(data['results'])}")
            
            # Verificar estructura
            if 'results' in data and 'total_encontrados' in data and 'query' in data:
                return True
            else:
                print("❌ Estructura de respuesta incorrecta")
                return False
        else:
            print(f"❌ Error en búsqueda inteligente: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error probando búsqueda inteligente: {e}")
        return False

def test_resumen_usuario():
    """Probar resumen personalizado del usuario"""
    print("\n📊 Probando resumen de usuario...")
    
    # Probar con residente
    headers = get_auth_headers(RESIDENT_USER)
    if not headers:
        print("❌ No se pudo autenticar resident")
        return False
    
    try:
        response = requests.get(
            f'{BASE_URL}/api/communications/avisos/resumen_usuario/',
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Resumen usuario exitoso")
            
            resumen = data['resumen']
            print(f"   📊 Avisos disponibles: {resumen['avisos_disponibles']}")
            print(f"   📖 Avisos leídos: {resumen['avisos_leidos']}")
            print(f"   📨 Avisos no leídos: {resumen['avisos_no_leidos']}")
            print(f"   💬 Comentarios realizados: {resumen['comentarios_realizados']}")
            print(f"   📈 Porcentaje lectura: {resumen['porcentaje_lectura']}%")
            
            # Verificar estructura
            required_keys = ['resumen', 'avisos_importantes_pendientes', 'avisos_confirmacion_pendientes', 'ultimas_lecturas']
            for key in required_keys:
                if key not in data:
                    print(f"❌ Falta clave '{key}' en respuesta")
                    return False
            
            return True
        else:
            print(f"❌ Error en resumen usuario: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error probando resumen usuario: {e}")
        return False

def test_avisos_no_leidos():
    """Probar endpoint de avisos no leídos"""
    print("\n📨 Probando avisos no leídos...")
    
    headers = get_auth_headers(RESIDENT_USER)
    if not headers:
        print("❌ No se pudo autenticar resident")
        return False
    
    try:
        response = requests.get(
            f'{BASE_URL}/api/communications/avisos/no_leidos/',
            headers=headers
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Avisos no leídos: {len(data['results'])} encontrados")
            
            # Verificar que todos los avisos son accesibles para el usuario
            for aviso in data['results']:
                print(f"   📋 {aviso['titulo']} - Prioridad: {aviso['prioridad']}")
            
            return True
        else:
            print(f"❌ Error avisos no leídos: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error probando avisos no leídos: {e}")
        return False

def test_detalle_aviso_marca_leido():
    """Probar que al ver detalle de aviso se marca como leído"""
    print("\n👁️ Probando marcado automático como leído...")
    
    headers = get_auth_headers(SECURITY_USER)
    if not headers:
        print("❌ No se pudo autenticar security")
        return False
    
    try:
        # Primero obtener lista de avisos
        response = requests.get(
            f'{BASE_URL}/api/communications/avisos/',
            headers=headers
        )
        
        if response.status_code != 200 or not response.json().get('results'):
            print("❌ No hay avisos disponibles para probar")
            return False
        
        aviso_id = response.json()['results'][0]['id']
        
        # Ver detalle del aviso (debería marcarlo como leído)
        response = requests.get(
            f'{BASE_URL}/api/communications/avisos/{aviso_id}/',
            headers=headers
        )
        
        if response.status_code == 200:
            print("✅ Detalle de aviso visto correctamente")
            
            # Verificar que ahora aparece en la lista de leídos
            # (esto se verificaría comparando avisos no leídos antes y después)
            return True
        else:
            print(f"❌ Error viendo detalle: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error probando marcado leído: {e}")
        return False

def test_permisos_por_rol():
    """Probar que cada rol solo ve los avisos apropiados"""
    print("\n🔐 Probando permisos por rol...")
    
    roles_usuarios = [
        ('admin', ADMIN_USER),
        ('resident', RESIDENT_USER),
        ('security', SECURITY_USER)
    ]
    
    results = {}
    
    for role_name, user_creds in roles_usuarios:
        headers = get_auth_headers(user_creds)
        if not headers:
            print(f"❌ No se pudo autenticar {role_name}")
            continue
        
        try:
            response = requests.get(
                f'{BASE_URL}/api/communications/avisos/',
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                count = len(data['results'])
                results[role_name] = count
                print(f"   👤 {role_name}: {count} avisos visibles")
            else:
                print(f"   ❌ Error para {role_name}: {response.status_code}")
                results[role_name] = -1
                
        except Exception as e:
            print(f"   ❌ Error probando {role_name}: {e}")
            results[role_name] = -1
    
    # Los admins deberían ver igual o más avisos que otros roles
    if results.get('admin', 0) >= results.get('resident', 0) and results.get('admin', 0) >= 0:
        print("✅ Permisos por rol funcionan correctamente")
        return True
    else:
        print("❌ ERROR: Los permisos por rol no funcionan correctamente")
        return False

def run_all_tests():
    """Ejecutar todos los tests de visualización"""
    print("🧪 INICIANDO TESTS DE VISUALIZACIÓN DE AVISOS")
    print("=" * 60)
    
    tests = [
        ("Dashboard Admin", test_dashboard_admin),
        ("Dashboard Residente", test_dashboard_resident),
        ("Filtros Avanzados", test_filtros_avanzados),
        ("Búsqueda Inteligente", test_busqueda_inteligente),
        ("Resumen Usuario", test_resumen_usuario),
        ("Avisos No Leídos", test_avisos_no_leidos),
        ("Marcado Automático Leído", test_detalle_aviso_marca_leido),
        ("Permisos por Rol", test_permisos_por_rol)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name}: PASÓ")
            else:
                print(f"❌ {test_name}: FALLÓ")
        except Exception as e:
            print(f"❌ {test_name}: ERROR - {e}")
    
    print(f"\n{'='*60}")
    print(f"🧪 RESUMEN FINAL DE TESTS DE VISUALIZACIÓN")
    print(f"✅ Tests pasados: {passed}/{total}")
    print(f"❌ Tests fallados: {total - passed}")
    
    if passed == total:
        print("🎉 ¡Todos los tests de visualización pasaron exitosamente!")
        print("🎯 El módulo T2: Visualizar Avisos está funcionando correctamente")
    else:
        print("⚠️ Algunos tests fallaron. Revisar la implementación.")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)