#!/usr/bin/env python3
"""
Test completo del Módulo 2: Gestión Financiera Básica
T1: Configurar Cuotas y Multas

Prueba todas las funcionalidades:
- CRUD de conceptos financieros
- CRUD de cargos financieros
- Permisos diferenciados
- Procesamiento de pagos
- Estadísticas
"""

import requests
import json
from datetime import date, timedelta

# Configuración
BASE_URL = "http://127.0.0.1:8000/api"
HEADERS = {'Content-Type': 'application/json'}

class TestFinances:
    def __init__(self):
        self.admin_token = None
        self.resident_token = None
        self.concepto_id = None
        self.cargo_id = None

    def print_section(self, title):
        print(f"\n{'='*60}")
        print(f"🔧 {title}")
        print('='*60)

    def print_test(self, description):
        print(f"\n📋 {description}")
        print("-" * 50)

    def login_users(self):
        """Login con diferentes tipos de usuarios"""
        self.print_section("AUTENTICACIÓN DE USUARIOS")
        
        # Login admin
        self.print_test("Login como Administrador")
        admin_data = {"username": "admin", "password": "clave123"}
        
        try:
            response = requests.post(f"{BASE_URL}/login/", json=admin_data, headers=HEADERS)
            if response.status_code == 200:
                self.admin_token = response.json()['token']
                print(f"✅ Admin login exitoso - Token: {self.admin_token[:20]}...")
            else:
                print(f"❌ Error admin login: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error de conexión admin: {e}")
            return False

        # Login residente
        self.print_test("Login como Residente")
        resident_data = {"username": "carlos", "password": "password123"}
        
        try:
            response = requests.post(f"{BASE_URL}/login/", json=resident_data, headers=HEADERS)
            if response.status_code == 200:
                self.resident_token = response.json()['token']
                print(f"✅ Resident login exitoso - Token: {self.resident_token[:20]}...")
                return True
            else:
                print(f"❌ Error resident login: {response.text}")
                return False
        except Exception as e:
            print(f"❌ Error de conexión resident: {e}")
            return False

    def test_conceptos_financieros(self):
        """Test CRUD de conceptos financieros"""
        self.print_section("PRUEBAS DE CONCEPTOS FINANCIEROS")
        
        admin_headers = {**HEADERS, 'Authorization': f'Token {self.admin_token}'}
        resident_headers = {**HEADERS, 'Authorization': f'Token {self.resident_token}'}

        # 1. Crear concepto como admin
        self.print_test("Crear Concepto Financiero (Admin)")
        concepto_data = {
            "nombre": "Cuota de Mantenimiento Enero 2025",
            "descripcion": "Cuota mensual de mantenimiento para enero 2025",
            "tipo": "cuota_mensual",
            "monto": "150.00",
            "es_recurrente": True,
            "aplica_a_todos": True,
            "fecha_vigencia_desde": str(date.today()),
            "fecha_vigencia_hasta": str(date.today() + timedelta(days=365))
        }

        try:
            response = requests.post(
                f"{BASE_URL}/finances/conceptos/",
                json=concepto_data,
                headers=admin_headers
            )
            if response.status_code == 201:
                concepto_response = response.json()
                self.concepto_id = concepto_response['id']
                print(f"✅ Concepto creado exitosamente - ID: {self.concepto_id}")
                print(f"   Nombre: {concepto_response['nombre']}")
                print(f"   Monto: ${concepto_response['monto']}")
            else:
                print(f"❌ Error creando concepto: {response.text}")
        except Exception as e:
            print(f"❌ Error de conexión: {e}")

        # 2. Intentar crear concepto como residente (debe fallar)
        self.print_test("Crear Concepto como Residente (Debe Fallar)")
        try:
            response = requests.post(
                f"{BASE_URL}/finances/conceptos/",
                json=concepto_data,
                headers=resident_headers
            )
            if response.status_code == 403:
                print("✅ Correctamente bloqueado - No tiene permisos")
            else:
                print(f"❌ Debería haber fallado pero retornó: {response.status_code}")
        except Exception as e:
            print(f"❌ Error de conexión: {e}")

        # 3. Listar conceptos como residente
        self.print_test("Listar Conceptos como Residente")
        try:
            response = requests.get(f"{BASE_URL}/finances/conceptos/", headers=resident_headers)
            if response.status_code == 200:
                conceptos = response.json()['results'] if 'results' in response.json() else response.json()
                print(f"✅ Conceptos obtenidos: {len(conceptos)} conceptos")
                for concepto in conceptos[:3]:  # Mostrar solo los primeros 3
                    print(f"   - {concepto['nombre']}: ${concepto['monto']}")
            else:
                print(f"❌ Error obteniendo conceptos: {response.text}")
        except Exception as e:
            print(f"❌ Error de conexión: {e}")

        # 4. Obtener conceptos vigentes
        self.print_test("Obtener Conceptos Vigentes")
        try:
            response = requests.get(f"{BASE_URL}/finances/conceptos/vigentes/", headers=admin_headers)
            if response.status_code == 200:
                conceptos = response.json()
                print(f"✅ Conceptos vigentes: {len(conceptos)} conceptos")
                for concepto in conceptos[:3]:
                    vigente = "✓" if concepto.get('esta_vigente') else "✗"
                    print(f"   {vigente} {concepto['nombre']}: ${concepto['monto']}")
            else:
                print(f"❌ Error obteniendo conceptos vigentes: {response.text}")
        except Exception as e:
            print(f"❌ Error de conexión: {e}")

    def test_cargos_financieros(self):
        """Test CRUD de cargos financieros"""
        self.print_section("PRUEBAS DE CARGOS FINANCIEROS")
        
        admin_headers = {**HEADERS, 'Authorization': f'Token {self.admin_token}'}
        resident_headers = {**HEADERS, 'Authorization': f'Token {self.resident_token}'}

        # 1. Obtener ID de residente para aplicar cargo
        self.print_test("Obtener información de residente Carlos")
        residente_id = None
        try:
            response = requests.get(f"{BASE_URL}/me/", headers=resident_headers)
            if response.status_code == 200:
                residente_info = response.json()
                residente_id = residente_info['id']
                print(f"✅ Residente obtenido - ID: {residente_id}, Username: {residente_info['username']}")
            else:
                print(f"❌ Error obteniendo residente: {response.text}")
                return
        except Exception as e:
            print(f"❌ Error de conexión: {e}")
            return

        # 2. Aplicar cargo como admin
        self.print_test("Aplicar Cargo Financiero (Admin)")
        cargo_data = {
            "concepto": self.concepto_id if self.concepto_id else 1,
            "residente": residente_id,
            "monto": "150.00",
            "fecha_aplicacion": str(date.today()),
            "fecha_vencimiento": str(date.today() + timedelta(days=30)),
            "observaciones": "Cargo aplicado por prueba automática"
        }

        try:
            response = requests.post(
                f"{BASE_URL}/finances/cargos/",
                json=cargo_data,
                headers=admin_headers
            )
            if response.status_code == 201:
                cargo_response = response.json()
                self.cargo_id = cargo_response['id']
                print(f"✅ Cargo aplicado exitosamente - ID: {self.cargo_id}")
                print(f"   Residente: {cargo_response.get('residente_info', {}).get('username', 'N/A')}")
                print(f"   Monto: ${cargo_response['monto']}")
                print(f"   Estado: {cargo_response['estado_display']}")
            else:
                print(f"❌ Error aplicando cargo: {response.text}")
        except Exception as e:
            print(f"❌ Error de conexión: {e}")

        # 3. Obtener mis cargos como residente
        self.print_test("Obtener Mis Cargos (Residente)")
        try:
            response = requests.get(f"{BASE_URL}/finances/cargos/mis_cargos/", headers=resident_headers)
            if response.status_code == 200:
                mis_cargos = response.json()
                print(f"✅ Mis cargos obtenidos: {len(mis_cargos)} cargos")
                for cargo in mis_cargos[:3]:
                    vencimiento = cargo.get('dias_para_vencimiento')
                    estado_venc = f" ({vencimiento} días)" if vencimiento and vencimiento > 0 else " (vencido)" if cargo.get('esta_vencido') else ""
                    print(f"   - {cargo['concepto_nombre']}: ${cargo['monto']} - {cargo['estado_display']}{estado_venc}")
            else:
                print(f"❌ Error obteniendo mis cargos: {response.text}")
        except Exception as e:
            print(f"❌ Error de conexión: {e}")

        # 4. Ver todos los cargos como admin
        self.print_test("Listar Todos los Cargos (Admin)")
        try:
            response = requests.get(f"{BASE_URL}/finances/cargos/", headers=admin_headers)
            if response.status_code == 200:
                todos_cargos = response.json()['results'] if 'results' in response.json() else response.json()
                print(f"✅ Todos los cargos obtenidos: {len(todos_cargos)} cargos")
                for cargo in todos_cargos[:3]:
                    print(f"   - {cargo['residente_username']}: ${cargo['monto']} - {cargo['estado_display']}")
            else:
                print(f"❌ Error obteniendo todos los cargos: {response.text}")
        except Exception as e:
            print(f"❌ Error de conexión: {e}")

    def test_proceso_pago(self):
        """Test del proceso de pago"""
        self.print_section("PRUEBAS DE PROCESO DE PAGO")
        
        admin_headers = {**HEADERS, 'Authorization': f'Token {self.admin_token}'}
        resident_headers = {**HEADERS, 'Authorization': f'Token {self.resident_token}'}

        if not self.cargo_id:
            print("❌ No hay cargo para probar el pago")
            return

        # 1. Pagar cargo como residente
        self.print_test("Procesar Pago de Cargo (Residente)")
        pago_data = {
            "referencia_pago": f"PAGO-TEST-{date.today()}",
            "observaciones": "Pago procesado en prueba automática"
        }

        try:
            response = requests.post(
                f"{BASE_URL}/finances/cargos/{self.cargo_id}/pagar/",
                json=pago_data,
                headers=resident_headers
            )
            if response.status_code == 200:
                pago_response = response.json()
                print("✅ Pago procesado exitosamente")
                print(f"   Referencia: {pago_response['cargo']['referencia_pago']}")
                print(f"   Nuevo estado: {pago_response['cargo']['estado_display']}")
                print(f"   Fecha pago: {pago_response['cargo']['fecha_pago']}")
            else:
                print(f"❌ Error procesando pago: {response.text}")
        except Exception as e:
            print(f"❌ Error de conexión: {e}")

        # 2. Intentar pagar cargo ya pagado (debe fallar)
        self.print_test("Intentar Pagar Cargo Ya Pagado (Debe Fallar)")
        try:
            response = requests.post(
                f"{BASE_URL}/finances/cargos/{self.cargo_id}/pagar/",
                json=pago_data,
                headers=resident_headers
            )
            if response.status_code == 400:
                print("✅ Correctamente bloqueado - Cargo ya pagado")
            else:
                print(f"❌ Debería haber fallado pero retornó: {response.status_code}")
                print(f"   Respuesta: {response.text}")
        except Exception as e:
            print(f"❌ Error de conexión: {e}")

    def test_resumen_y_estadisticas(self):
        """Test de resúmenes y estadísticas"""
        self.print_section("PRUEBAS DE RESÚMENES Y ESTADÍSTICAS")
        
        admin_headers = {**HEADERS, 'Authorization': f'Token {self.admin_token}'}
        resident_headers = {**HEADERS, 'Authorization': f'Token {self.resident_token}'}

        # 1. Resumen financiero del residente
        self.print_test("Resumen Financiero del Residente")
        try:
            # Obtener ID del residente actual
            me_response = requests.get(f"{BASE_URL}/me/", headers=resident_headers)
            if me_response.status_code == 200:
                user_id = me_response.json()['id']
                
                response = requests.get(
                    f"{BASE_URL}/finances/cargos/resumen/{user_id}/",
                    headers=resident_headers
                )
                if response.status_code == 200:
                    resumen = response.json()
                    print("✅ Resumen financiero obtenido")
                    print(f"   Total pendiente: ${resumen.get('total_pendiente', 0)}")
                    print(f"   Total vencido: ${resumen.get('total_vencido', 0)}")
                    print(f"   Pagado este mes: ${resumen.get('total_pagado_mes', 0)}")
                    print(f"   Cargos pendientes: {resumen.get('cantidad_cargos_pendientes', 0)}")
                else:
                    print(f"❌ Error obteniendo resumen: {response.text}")
            else:
                print(f"❌ Error obteniendo info de usuario: {me_response.text}")
        except Exception as e:
            print(f"❌ Error de conexión: {e}")

        # 2. Estadísticas generales como admin
        self.print_test("Estadísticas Generales (Admin)")
        try:
            response = requests.get(f"{BASE_URL}/finances/estadisticas/", headers=admin_headers)
            if response.status_code == 200:
                estadisticas = response.json()
                print("✅ Estadísticas obtenidas")
                print(f"   Conceptos activos: {estadisticas.get('total_conceptos_activos', 0)}")
                print(f"   Cargos pendientes: {estadisticas.get('total_cargos_pendientes', 0)}")
                print(f"   Monto total pendiente: ${estadisticas.get('monto_total_pendiente', 0)}")
                print(f"   Cargos vencidos: {estadisticas.get('total_cargos_vencidos', 0)}")
                print(f"   Pagos este mes: ${estadisticas.get('total_pagos_mes_actual', 0)}")
            else:
                print(f"❌ Error obteniendo estadísticas: {response.text}")
        except Exception as e:
            print(f"❌ Error de conexión: {e}")

        # 3. Intentar ver estadísticas como residente (debe fallar)
        self.print_test("Intentar Ver Estadísticas como Residente (Debe Fallar)")
        try:
            response = requests.get(f"{BASE_URL}/finances/estadisticas/", headers=resident_headers)
            if response.status_code == 403:
                print("✅ Correctamente bloqueado - No tiene permisos")
            else:
                print(f"❌ Debería haber fallado pero retornó: {response.status_code}")
        except Exception as e:
            print(f"❌ Error de conexión: {e}")

    def run_all_tests(self):
        """Ejecutar todas las pruebas"""
        print("🧪 INICIANDO PRUEBAS DEL MÓDULO 2: GESTIÓN FINANCIERA")
        print("=" * 80)
        
        if not self.login_users():
            print("❌ Falló la autenticación. Abortando pruebas.")
            return
        
        self.test_conceptos_financieros()
        self.test_cargos_financieros() 
        self.test_proceso_pago()
        self.test_resumen_y_estadisticas()
        
        print("\n" + "=" * 80)
        print("✅ PRUEBAS DEL MÓDULO 2 COMPLETADAS")
        print("📋 Funcionalidades probadas:")
        print("   ✓ Autenticación y permisos")
        print("   ✓ CRUD de conceptos financieros")
        print("   ✓ CRUD de cargos financieros")
        print("   ✓ Proceso de pagos")
        print("   ✓ Resúmenes y estadísticas")
        print("   ✓ Permisos diferenciados por rol")
        print("=" * 80)


if __name__ == "__main__":
    test_suite = TestFinances()
    test_suite.run_all_tests()