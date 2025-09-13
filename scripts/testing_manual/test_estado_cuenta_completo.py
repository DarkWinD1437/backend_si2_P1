#!/usr/bin/env python
"""
Script de Testing Manual para Estado de Cuenta
Módulo 2: Gestión Financiera Básica - T2: Consultar estado de cuenta

Este script valida:
- Endpoint de estado de cuenta para residentes
- Endpoint de estado de cuenta para administradores  
- Permisos y restricciones de acceso
- Estructura y completitud de respuestas
- Casos de uso específicos

Ejecutar desde la raíz del proyecto:
python scripts/testing_manual/test_estado_cuenta_completo.py
"""

import os
import sys
import json
import requests
from datetime import datetime
from decimal import Decimal

# Configuración del servidor
BASE_URL = 'http://localhost:8000'
API_BASE = f'{BASE_URL}/api'

# Credenciales de prueba
ADMIN_CREDENTIALS = {
    'username': 'admin',
    'password': 'clave123'
}

RESIDENT_CREDENTIALS = {
    'username': 'resident1',  # Cambiar por usuario residente real
    'password': 'clave123'
}

class EstadoCuentaTester:
    def __init__(self):
        self.session = requests.Session()
        self.admin_token = None
        self.resident_token = None
        self.admin_user_id = None
        self.resident_user_id = None
        self.test_results = []
        
    def log_test(self, test_name, success, details="", response_data=None):
        """Registrar resultado de prueba"""
        result = {
            'test': test_name,
            'success': success,
            'details': details,
            'timestamp': datetime.now().isoformat()
        }
        if response_data and isinstance(response_data, dict):
            result['response_keys'] = list(response_data.keys())
        self.test_results.append(result)
        
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status} {test_name}")
        if details:
            print(f"    {details}")
        print()

    def authenticate(self):
        """Autenticar usuarios de prueba"""
        print("🔑 AUTENTICACIÓN")
        print("="*50)
        
        # Autenticar admin
        try:
            response = self.session.post(
                f'{API_BASE}/users/login/',
                json=ADMIN_CREDENTIALS
            )
            
            if response.status_code == 200:
                data = response.json()
                self.admin_token = data.get('token') or data.get('access_token')
                self.admin_user_id = data.get('user', {}).get('id')
                self.log_test(
                    "Autenticación Administrador", 
                    True, 
                    f"Token obtenido, User ID: {self.admin_user_id}"
                )
            else:
                self.log_test(
                    "Autenticación Administrador", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test("Autenticación Administrador", False, f"Error: {str(e)}")
        
        # Autenticar residente
        try:
            response = self.session.post(
                f'{API_BASE}/users/login/',
                json=RESIDENT_CREDENTIALS
            )
            
            if response.status_code == 200:
                data = response.json()
                self.resident_token = data.get('token') or data.get('access_token')
                self.resident_user_id = data.get('user', {}).get('id')
                self.log_test(
                    "Autenticación Residente", 
                    True, 
                    f"Token obtenido, User ID: {self.resident_user_id}"
                )
            else:
                self.log_test(
                    "Autenticación Residente", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test("Autenticación Residente", False, f"Error: {str(e)}")

    def test_estado_cuenta_residente(self):
        """Probar consulta de estado de cuenta por residente"""
        print("👤 PRUEBAS DE RESIDENTE")
        print("="*50)
        
        if not self.resident_token:
            self.log_test("Estado cuenta residente", False, "Sin token de residente")
            return
        
        headers = {'Authorization': f'Token {self.resident_token}'}
        
        try:
            # Consultar propio estado de cuenta
            response = self.session.get(
                f'{API_BASE}/finances/cargos/estado_cuenta/',
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Verificar estructura de respuesta
                required_keys = [
                    'residente_info', 'fecha_consulta', 'resumen_general',
                    'cargos_pendientes', 'cargos_vencidos', 'historial_pagos',
                    'desglose_por_tipo', 'proximo_vencimiento', 'ultimo_pago', 'alertas'
                ]
                
                missing_keys = [key for key in required_keys if key not in data]
                
                if not missing_keys:
                    self.log_test(
                        "Estado cuenta propio - Estructura completa", 
                        True, 
                        f"Todas las claves requeridas presentes. Pendientes: {data['resumen_general']['cantidad_cargos_pendientes']}"
                    )
                    
                    # Verificar info del residente
                    residente_info = data.get('residente_info', {})
                    if residente_info.get('id') == self.resident_user_id:
                        self.log_test(
                            "Estado cuenta propio - Info correcta", 
                            True, 
                            f"Usuario: {residente_info.get('username')}"
                        )
                    else:
                        self.log_test(
                            "Estado cuenta propio - Info correcta", 
                            False, 
                            f"ID no coincide: esperado {self.resident_user_id}, obtenido {residente_info.get('id')}"
                        )
                        
                    # Verificar totales
                    resumen = data.get('resumen_general', {})
                    if 'total_pendiente' in resumen and 'total_vencido' in resumen:
                        self.log_test(
                            "Estado cuenta propio - Totales", 
                            True, 
                            f"Pendiente: ${resumen['total_pendiente']}, Vencido: ${resumen['total_vencido']}"
                        )
                    
                else:
                    self.log_test(
                        "Estado cuenta propio - Estructura completa", 
                        False, 
                        f"Claves faltantes: {missing_keys}"
                    )
                    
            else:
                self.log_test(
                    "Estado cuenta propio", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test("Estado cuenta propio", False, f"Error: {str(e)}")
        
        # Intentar acceder a estado de cuenta de otro residente (debe fallar)
        if self.admin_user_id:
            try:
                response = self.session.get(
                    f'{API_BASE}/finances/cargos/estado_cuenta/?residente={self.admin_user_id}',
                    headers=headers
                )
                
                if response.status_code == 403:
                    self.log_test(
                        "Estado cuenta otros - Restricción permisos", 
                        True, 
                        "Correctamente prohibido acceso a estado de cuenta de otros"
                    )
                else:
                    self.log_test(
                        "Estado cuenta otros - Restricción permisos", 
                        False, 
                        f"Debería ser HTTP 403, obtenido: {response.status_code}"
                    )
                    
            except Exception as e:
                self.log_test("Estado cuenta otros - Restricción permisos", False, f"Error: {str(e)}")

    def test_estado_cuenta_admin(self):
        """Probar consulta de estado de cuenta por administrador"""
        print("👨‍💼 PRUEBAS DE ADMINISTRADOR")
        print("="*50)
        
        if not self.admin_token:
            self.log_test("Estado cuenta admin", False, "Sin token de administrador")
            return
        
        headers = {'Authorization': f'Token {self.admin_token}'}
        
        # Consultar propio estado de cuenta
        try:
            response = self.session.get(
                f'{API_BASE}/finances/cargos/estado_cuenta/',
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Estado cuenta propio (admin)", 
                    True, 
                    f"Admin puede consultar su propio estado. Pendientes: {data['resumen_general']['cantidad_cargos_pendientes']}"
                )
            else:
                self.log_test(
                    "Estado cuenta propio (admin)", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test("Estado cuenta propio (admin)", False, f"Error: {str(e)}")
        
        # Consultar estado de cuenta de residente específico
        if self.resident_user_id:
            try:
                response = self.session.get(
                    f'{API_BASE}/finances/cargos/estado_cuenta/?residente={self.resident_user_id}',
                    headers=headers
                )
                
                if response.status_code == 200:
                    data = response.json()
                    residente_info = data.get('residente_info', {})
                    
                    if residente_info.get('id') == self.resident_user_id:
                        self.log_test(
                            "Estado cuenta de residente (admin)", 
                            True, 
                            f"Admin consultó estado de {residente_info.get('username')}. Pendientes: {data['resumen_general']['cantidad_cargos_pendientes']}"
                        )
                    else:
                        self.log_test(
                            "Estado cuenta de residente (admin)", 
                            False, 
                            f"ID incorrecto en respuesta: esperado {self.resident_user_id}, obtenido {residente_info.get('id')}"
                        )
                else:
                    self.log_test(
                        "Estado cuenta de residente (admin)", 
                        False, 
                        f"HTTP {response.status_code}: {response.text}"
                    )
                    
            except Exception as e:
                self.log_test("Estado cuenta de residente (admin)", False, f"Error: {str(e)}")

    def test_endpoints_complementarios(self):
        """Probar endpoints complementarios relacionados"""
        print("🔗 ENDPOINTS COMPLEMENTARIOS")
        print("="*50)
        
        if not self.resident_token:
            return
        
        headers = {'Authorization': f'Token {self.resident_token}'}
        
        # Test mis_cargos
        try:
            response = self.session.get(
                f'{API_BASE}/finances/cargos/mis_cargos/',
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Endpoint mis_cargos", 
                    True, 
                    f"{len(data)} cargos encontrados"
                )
            else:
                self.log_test(
                    "Endpoint mis_cargos", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test("Endpoint mis_cargos", False, f"Error: {str(e)}")
        
        # Test conceptos vigentes
        try:
            response = self.session.get(
                f'{API_BASE}/finances/conceptos/vigentes/',
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                self.log_test(
                    "Conceptos vigentes", 
                    True, 
                    f"{len(data)} conceptos vigentes"
                )
            else:
                self.log_test(
                    "Conceptos vigentes", 
                    False, 
                    f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            self.log_test("Conceptos vigentes", False, f"Error: {str(e)}")

    def test_validacion_respuesta_detallada(self):
        """Validar estructura detallada de la respuesta"""
        print("🔍 VALIDACIÓN DETALLADA DE RESPUESTA")
        print("="*50)
        
        if not self.resident_token:
            return
        
        headers = {'Authorization': f'Token {self.resident_token}'}
        
        try:
            response = self.session.get(
                f'{API_BASE}/finances/cargos/estado_cuenta/',
                headers=headers
            )
            
            if response.status_code == 200:
                data = response.json()
                
                # Validar resumen_general
                resumen = data.get('resumen_general', {})
                expected_resumen_keys = [
                    'total_pendiente', 'total_vencido', 'total_al_dia',
                    'cantidad_cargos_pendientes', 'cantidad_cargos_vencidos',
                    'total_pagado_mes_actual', 'total_pagado_6_meses'
                ]
                
                missing_resumen = [key for key in expected_resumen_keys if key not in resumen]
                if not missing_resumen:
                    self.log_test(
                        "Validación resumen_general", 
                        True, 
                        "Todas las claves del resumen presentes"
                    )
                else:
                    self.log_test(
                        "Validación resumen_general", 
                        False, 
                        f"Claves faltantes en resumen: {missing_resumen}"
                    )
                
                # Validar alertas
                alertas = data.get('alertas', [])
                if isinstance(alertas, list):
                    self.log_test(
                        "Validación alertas", 
                        True, 
                        f"{len(alertas)} alertas en el estado de cuenta"
                    )
                    
                    for alerta in alertas:
                        if 'tipo' in alerta and 'severidad' in alerta and 'titulo' in alerta:
                            continue
                        else:
                            self.log_test(
                                "Validación estructura alertas", 
                                False, 
                                "Estructura de alerta inválida"
                            )
                            break
                    else:
                        if alertas:
                            self.log_test(
                                "Validación estructura alertas", 
                                True, 
                                "Todas las alertas tienen estructura válida"
                            )
                
                # Validar próximo vencimiento
                proximo = data.get('proximo_vencimiento', {})
                if 'cargo' in proximo and 'fecha' in proximo and 'dias_restantes' in proximo:
                    self.log_test(
                        "Validación próximo vencimiento", 
                        True, 
                        f"Estructura correcta. Días restantes: {proximo.get('dias_restantes')}"
                    )
                
                # Validar último pago
                ultimo_pago = data.get('ultimo_pago', {})
                if 'cargo' in ultimo_pago and 'fecha' in ultimo_pago and 'hace_dias' in ultimo_pago:
                    self.log_test(
                        "Validación último pago", 
                        True, 
                        f"Estructura correcta. Hace {ultimo_pago.get('hace_dias')} días"
                    )
                
            else:
                self.log_test(
                    "Validación detallada", 
                    False, 
                    f"No se pudo obtener respuesta válida: HTTP {response.status_code}"
                )
                
        except Exception as e:
            self.log_test("Validación detallada", False, f"Error: {str(e)}")

    def generate_report(self):
        """Generar reporte final de pruebas"""
        print("\n📊 REPORTE FINAL")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = len([t for t in self.test_results if t['success']])
        failed_tests = total_tests - passed_tests
        
        success_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        
        print(f"Total de pruebas: {total_tests}")
        print(f"Pruebas exitosas: {passed_tests} ✅")
        print(f"Pruebas fallidas: {failed_tests} ❌")
        print(f"Tasa de éxito: {success_rate:.1f}%")
        
        print(f"\n{'='*60}")
        
        if failed_tests > 0:
            print("PRUEBAS FALLIDAS:")
            for test in self.test_results:
                if not test['success']:
                    print(f"❌ {test['test']}: {test['details']}")
        else:
            print("🎉 ¡TODAS LAS PRUEBAS PASARON EXITOSAMENTE!")
        
        # Guardar reporte en archivo
        try:
            report_file = 'test_estado_cuenta_report.json'
            with open(report_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'summary': {
                        'total': total_tests,
                        'passed': passed_tests,
                        'failed': failed_tests,
                        'success_rate': success_rate
                    },
                    'tests': self.test_results
                }, f, indent=2, ensure_ascii=False)
            
            print(f"\n📄 Reporte guardado en: {report_file}")
            
        except Exception as e:
            print(f"⚠️ No se pudo guardar el reporte: {str(e)}")

    def run_all_tests(self):
        """Ejecutar todas las pruebas"""
        print("🚀 INICIANDO PRUEBAS DE ESTADO DE CUENTA")
        print("="*60)
        print(f"Servidor: {BASE_URL}")
        print(f"API Base: {API_BASE}")
        print(f"Timestamp: {datetime.now().isoformat()}")
        print()
        
        # Ejecutar pruebas en orden
        self.authenticate()
        self.test_estado_cuenta_residente()
        self.test_estado_cuenta_admin()
        self.test_endpoints_complementarios()
        self.test_validacion_respuesta_detallada()
        
        # Generar reporte
        self.generate_report()

def main():
    """Función principal"""
    tester = EstadoCuentaTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()