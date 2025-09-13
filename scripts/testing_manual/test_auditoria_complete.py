#!/usr/bin/env python
"""
Script de pruebas para el módulo de auditoría
"""
import requests
import json
from datetime import datetime

# Configuración
BASE_URL = "http://127.0.0.1:8000/api"
HEADERS = {
    "Content-Type": "application/json"
}

class TestAuditoriaCompleto:
    def __init__(self):
        self.admin_token = None
        self.resident_token = None
    
    def parse_response_data(self, data):
        """Helper para manejar respuestas paginadas y listas directas"""
        if isinstance(data, dict) and 'results' in data:
            total = data.get('count', len(data.get('results', [])))
            resultados = data.get('results', [])
        elif isinstance(data, list):
            total = len(data)
            resultados = data
        else:
            total = 0
            resultados = []
        return total, resultados
        
    def print_test(self, test_name):
        """Imprime el nombre del test"""
        print(f"\n🧪 {test_name}")
        print("-" * 50)
    
    def login_users(self):
        """Login con diferentes tipos de usuarios"""
        print("🔐 Iniciando sesión con usuarios de prueba...")
        
        # Login admin
        self.print_test("Login como Administrador")
        admin_data = {
            "username": "admin",
            "password": "admin123"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/login/", json=admin_data, headers=HEADERS)
            if response.status_code == 200:
                self.admin_token = response.json().get('token')
                print(f"✅ Admin login exitoso - Token: {self.admin_token[:20]}...")
            else:
                print(f"❌ Error admin login: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error de conexión admin: {e}")
            return False
        
        # Login residente
        self.print_test("Login como Residente")
        resident_data = {
            "username": "carlos",
            "password": "123456"
        }
        
        try:
            response = requests.post(f"{BASE_URL}/login/", json=resident_data, headers=HEADERS)
            if response.status_code == 200:
                self.resident_token = response.json().get('token')
                print(f"✅ Resident login exitoso - Token: {self.resident_token[:20]}...")
            else:
                print(f"❌ Error resident login: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error de conexión resident: {e}")
            return False
        
        return True
    
    def test_registros_auditoria_admin(self):
        """Test de registros de auditoría como administrador"""
        self.print_test("Obtener Registros de Auditoría (Admin)")
        
        headers = {**HEADERS, "Authorization": f"Token {self.admin_token}"}
        
        try:
            response = requests.get(f"{BASE_URL}/audit/registros/", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Registros obtenidos exitosamente")
                
                # Manejar respuesta paginada o lista directa
                if isinstance(data, dict) and 'results' in data:
                    total = data.get('count', len(data.get('results', [])))
                    resultados = data.get('results', [])
                elif isinstance(data, list):
                    total = len(data)
                    resultados = data
                else:
                    total = 0
                    resultados = []
                
                print(f"   📊 Total de registros: {total}")
                
                if len(resultados) > 0:
                    registro = resultados[0]
                    print(f"   📝 Último registro: {registro.get('descripcion', '')[:60]}...")
                    print(f"   👤 Usuario: {registro.get('usuario_info', {}).get('username', 'N/A')}")
                    print(f"   🔍 Tipo: {registro.get('tipo_actividad_display', 'N/A')}")
                    print(f"   ⚠️  Nivel: {registro.get('nivel_importancia_display', 'N/A')}")
                
                return True
            else:
                print(f"❌ Error al obtener registros: {response.status_code}")
                print(f"   Respuesta: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            return False
    
    def test_registros_auditoria_resident(self):
        """Test de registros de auditoría como residente"""
        self.print_test("Obtener Mis Registros (Residente)")
        
        headers = {**HEADERS, "Authorization": f"Token {self.resident_token}"}
        
        try:
            response = requests.get(f"{BASE_URL}/audit/registros/mis_actividades/", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Mis registros obtenidos exitosamente")
                
                # Manejar tanto estructura paginada como lista directa
                if isinstance(data, dict) and 'results' in data:
                    total = data.get('count', len(data.get('results', [])))
                    resultados = data.get('results', [])
                elif isinstance(data, list):
                    total = len(data)
                    resultados = data
                else:
                    total = 0
                    resultados = []
                
                print(f"   📊 Mis actividades: {total}")
                
                if len(resultados) > 0:
                    registro = resultados[0]
                    print(f"   📝 Mi última actividad: {registro.get('descripcion', '')[:60]}...")
                    print(f"   🔍 Tipo: {registro.get('tipo_actividad_display', 'N/A')}")
                
                return True
            else:
                print(f"❌ Error al obtener mis registros: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            return False
    
    def test_resumen_auditoria(self):
        """Test del resumen de auditoría (solo admin)"""
        self.print_test("Obtener Resumen de Auditoría (Admin)")
        
        headers = {**HEADERS, "Authorization": f"Token {self.admin_token}"}
        
        try:
            response = requests.get(f"{BASE_URL}/audit/registros/resumen/", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Resumen de auditoría obtenido exitosamente")
                print(f"   📊 Total registros: {data.get('total_registros', 0)}")
                print(f"   📅 Registros hoy: {data.get('registros_hoy', 0)}")
                print(f"   📈 Registros semana: {data.get('registros_semana', 0)}")
                print(f"   ✅ Logins exitosos hoy: {data.get('logins_exitosos_hoy', 0)}")
                print(f"   ❌ Logins fallidos hoy: {data.get('logins_fallidos_hoy', 0)}")
                print(f"   👥 Usuarios activos hoy: {data.get('usuarios_activos_hoy', 0)}")
                print(f"   🟢 Sesiones activas: {data.get('sesiones_activas', 0)}")
                print(f"   🔴 Errores críticos hoy: {data.get('errores_criticos_hoy', 0)}")
                
                if data.get('actividades_por_tipo'):
                    print("   📋 Actividades por tipo:")
                    for tipo, count in data['actividades_por_tipo'].items():
                        print(f"     - {tipo}: {count}")
                
                return True
            else:
                print(f"❌ Error al obtener resumen: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            return False
    
    def test_sesiones_usuario(self):
        """Test de sesiones de usuario"""
        self.print_test("Obtener Sesiones de Usuario (Admin)")
        
        headers = {**HEADERS, "Authorization": f"Token {self.admin_token}"}
        
        try:
            response = requests.get(f"{BASE_URL}/audit/sesiones/", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Sesiones obtenidas exitosamente")
                
                # Manejar respuesta paginada o lista directa
                if isinstance(data, dict) and 'results' in data:
                    total = data.get('count', len(data.get('results', [])))
                    resultados = data.get('results', [])
                elif isinstance(data, list):
                    total = len(data)
                    resultados = data
                else:
                    total = 0
                    resultados = []
                
                print(f"   📊 Total de sesiones: {total}")
                
                if 'results' in data and len(data['results']) > 0:
                    sesion = data['results'][0]
                    print(f"   👤 Usuario: {sesion.get('usuario_info', {}).get('username', 'N/A')}")
                    print(f"   🌐 IP: {sesion.get('ip_address', 'N/A')}")
                    print(f"   ⏰ Duración: {sesion.get('duracion_sesion_str', 'N/A')}")
                    print(f"   🔄 Activa: {'✅' if sesion.get('esta_activa') else '❌'}")
                
                return True
            else:
                print(f"❌ Error al obtener sesiones: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            return False
    
    def test_mis_sesiones_resident(self):
        """Test de mis sesiones como residente"""
        self.print_test("Obtener Mis Sesiones (Residente)")
        
        headers = {**HEADERS, "Authorization": f"Token {self.resident_token}"}
        
        try:
            response = requests.get(f"{BASE_URL}/audit/sesiones/mis_sesiones/", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Mis sesiones obtenidas exitosamente")
                
                # Manejar tanto estructura paginada como lista directa
                if isinstance(data, dict) and 'results' in data:
                    total = data.get('count', len(data.get('results', [])))
                    resultados = data.get('results', [])
                elif isinstance(data, list):
                    total = len(data)
                    resultados = data
                else:
                    total = 0
                    resultados = []
                
                print(f"   📊 Mis sesiones: {total}")
                
                if len(resultados) > 0:
                    sesion = resultados[0]
                    print(f"   🌐 Mi IP: {sesion.get('ip_address', 'N/A')}")
                    print(f"   ⏰ Duración: {sesion.get('duracion_sesion_str', 'N/A')}")
                    print(f"   🔄 Activa: {'✅' if sesion.get('esta_activa') else '❌'}")
                
                return True
            else:
                print(f"❌ Error al obtener mis sesiones: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            return False
    
    def test_estadisticas_auditoria(self):
        """Test de estadísticas de auditoría"""
        self.print_test("Obtener Estadísticas de Auditoría (Admin)")
        
        headers = {**HEADERS, "Authorization": f"Token {self.admin_token}"}
        
        try:
            response = requests.get(f"{BASE_URL}/audit/estadisticas/", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Estadísticas obtenidas exitosamente")
                
                # Usar helper para procesar respuesta
                total, resultados = self.parse_response_data(data)
                print(f"   📊 Registros de estadísticas: {total}")
                
                if len(resultados) > 0:
                    stat = resultados[0]
                    print(f"   📅 Fecha: {stat.get('fecha', 'N/A')}")
                    print(f"   📈 Total actividades: {stat.get('total_actividades', 0)}")
                    print(f"   👥 Usuarios activos: {stat.get('total_usuarios_activos', 0)}")
                    print(f"   🔴 Errores: {stat.get('errores_sistema', 0)}")
                
                return True
            else:
                print(f"❌ Error al obtener estadísticas: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            return False
    
    def test_filtros_auditoria(self):
        """Test de filtros en registros de auditoría"""
        self.print_test("Probar Filtros de Auditoría (Admin)")
        
        headers = {**HEADERS, "Authorization": f"Token {self.admin_token}"}
        
        # Test filtro por tipo de actividad
        try:
            response = requests.get(
                f"{BASE_URL}/audit/registros/?tipo_actividad=login", 
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Filtro por tipo 'login':")
                total, _ = self.parse_response_data(data)
                print(f"   📊 Registros encontrados: {total}")
                
                # Test filtro por nivel de importancia
                response = requests.get(
                    f"{BASE_URL}/audit/registros/?nivel_importancia=critico", 
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Filtro por nivel 'crítico':")
                    total, _ = self.parse_response_data(data)
                    print(f"   📊 Registros encontrados: {total}")
                
                # Test filtro por éxito
                response = requests.get(
                    f"{BASE_URL}/audit/registros/?es_exitoso=false", 
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    print(f"✅ Filtro por operaciones fallidas:")
                    total, _ = self.parse_response_data(data)
                    print(f"   📊 Registros encontrados: {total}")
                
                return True
            else:
                print(f"❌ Error al probar filtros: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            return False
    
    def test_permisos_acceso(self):
        """Test de permisos de acceso"""
        self.print_test("Verificar Permisos de Acceso")
        
        # Residente no puede ver resumen general
        headers = {**HEADERS, "Authorization": f"Token {self.resident_token}"}
        
        try:
            response = requests.get(f"{BASE_URL}/audit/registros/resumen/", headers=headers)
            
            if response.status_code == 403:
                print(f"✅ Residente correctamente no puede acceder al resumen general")
            else:
                print(f"❌ Residente puede acceder al resumen (debería estar prohibido)")
                return False
            
            # Residente no puede ver todos los registros
            response = requests.get(f"{BASE_URL}/audit/registros/", headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Residente puede ver registros (solo los suyos)")
                # Verificar que solo ve sus propios registros
                if 'results' in data:
                    for registro in data['results'][:3]:  # Verificar los primeros 3
                        usuario = registro.get('usuario_info', {}).get('username', '')
                        if usuario and usuario != 'carlos':
                            print(f"❌ Residente ve registros de otros usuarios: {usuario}")
                            return False
                    print(f"✅ Residente solo ve sus propios registros")
                
            return True
            
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            return False
    
    def run_all_tests(self):
        """Ejecutar todas las pruebas"""
        print("🚀 INICIANDO PRUEBAS COMPLETAS DEL MÓDULO DE AUDITORÍA")
        print("=" * 70)
        
        tests = [
            ("Login de Usuarios", self.login_users),
            ("Registros Auditoría (Admin)", self.test_registros_auditoria_admin),
            ("Mis Registros (Residente)", self.test_registros_auditoria_resident),
            ("Resumen Auditoría", self.test_resumen_auditoria),
            ("Sesiones Usuario (Admin)", self.test_sesiones_usuario),
            ("Mis Sesiones (Residente)", self.test_mis_sesiones_resident),
            ("Estadísticas Auditoría", self.test_estadisticas_auditoria),
            ("Filtros Auditoría", self.test_filtros_auditoria),
            ("Permisos de Acceso", self.test_permisos_acceso),
        ]
        
        resultados = []
        
        for test_name, test_func in tests:
            try:
                resultado = test_func()
                resultados.append((test_name, resultado))
                if resultado:
                    print(f"✅ {test_name}: PASÓ")
                else:
                    print(f"❌ {test_name}: FALLÓ")
            except Exception as e:
                print(f"❌ {test_name}: ERROR - {e}")
                resultados.append((test_name, False))
        
        # Resumen final
        print("\n" + "=" * 70)
        print("📊 RESUMEN DE RESULTADOS:")
        
        passed = sum(1 for _, result in resultados if result)
        total = len(resultados)
        
        for test_name, result in resultados:
            status = "✅ PASÓ" if result else "❌ FALLÓ"
            print(f"   {status}: {test_name}")
        
        print(f"\n🎯 TOTAL: {passed}/{total} pruebas pasaron")
        
        if passed == total:
            print("🎉 ¡TODAS LAS PRUEBAS PASARON! El módulo de auditoría está funcionando correctamente.")
        else:
            print(f"⚠️  {total - passed} pruebas fallaron. Revisar implementación.")
        
        return passed == total


if __name__ == "__main__":
    tester = TestAuditoriaCompleto()
    success = tester.run_all_tests()
    exit(0 if success else 1)