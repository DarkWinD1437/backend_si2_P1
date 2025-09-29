#!/usr/bin/env python
"""
Script de setup para tests del módulo Analytics
Instala dependencias y configura el entorno de testing
"""

import os
import sys
import subprocess
import argparse

def install_dependencies():
    """Instalar dependencias de testing"""
    print("📦 Instalando dependencias de testing...")

    requirements_file = "Tests/analytics/requirements-test.txt"

    if not os.path.exists(requirements_file):
        print(f"❌ Archivo {requirements_file} no encontrado")
        return False

    try:
        subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", requirements_file
        ], check=True)
        print("✅ Dependencias instaladas correctamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error instalando dependencias: {e}")
        return False

def setup_database():
    """Configurar base de datos para tests"""
    print("🗄️ Configurando base de datos para tests...")

    try:
        # Ejecutar migraciones
        subprocess.run([
            sys.executable, "manage.py", "migrate", "--settings=backend.settings"
        ], check=True, cwd=os.path.dirname(os.path.dirname(__file__)))

        print("✅ Base de datos configurada correctamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error configurando base de datos: {e}")
        return False

def run_quick_test():
    """Ejecutar un test rápido para verificar configuración"""
    print("🧪 Ejecutando test de verificación...")

    try:
        result = subprocess.run([
            sys.executable, "-c",
            """
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
import django
django.setup()

# Test básico de importación
from backend.apps.analytics.models import ReporteFinanciero
from backend.apps.analytics.serializers import ReporteFinancieroSerializer
print('✅ Imports funcionando correctamente')

# Test de modelo básico
reporte = ReporteFinanciero(
    titulo='Test Setup',
    tipo='ingresos',
    periodo='mensual',
    formato='json',
    fecha_inicio='2024-01-01',
    fecha_fin='2024-01-31',
    generado_por=None,
    datos={'test': 'ok'},
    total_registros=1
)
print('✅ Modelo creado correctamente')
            """
        ], check=True, cwd=os.path.dirname(os.path.dirname(__file__)))

        print("✅ Configuración verificada correctamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error en verificación: {e}")
        return False

def create_test_data():
    """Crear datos de prueba básicos"""
    print("📝 Creando datos de prueba...")

    try:
        result = subprocess.run([
            sys.executable, "-c",
            """
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
import django
django.setup()

from django.contrib.auth import get_user_model
from backend.apps.analytics.models import ReporteFinanciero

User = get_user_model()

# Crear usuario de prueba si no existe
if not User.objects.filter(username='test_admin').exists():
    User.objects.create_user(
        username='test_admin',
        email='test@admin.com',
        password='test123',
        role='admin'
    )
    print('✅ Usuario de prueba creado')

# Crear reporte de prueba si no existe
if not ReporteFinanciero.objects.filter(titulo='Reporte de Prueba').exists():
    admin_user = User.objects.get(username='test_admin')
    ReporteFinanciero.objects.create(
        titulo='Reporte de Prueba',
        tipo='ingresos',
        periodo='mensual',
        formato='json',
        fecha_inicio='2024-01-01',
        fecha_fin='2024-01-31',
        generado_por=admin_user,
        datos={'total': 1000},
        total_registros=10
    )
    print('✅ Reporte de prueba creado')

print('✅ Datos de prueba listos')
            """
        ], check=True, cwd=os.path.dirname(os.path.dirname(__file__)))

        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error creando datos de prueba: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Setup para tests del módulo Analytics')
    parser.add_argument('--install', action='store_true',
                       help='Instalar dependencias')
    parser.add_argument('--database', action='store_true',
                       help='Configurar base de datos')
    parser.add_argument('--verify', action='store_true',
                       help='Verificar configuración')
    parser.add_argument('--test-data', action='store_true',
                       help='Crear datos de prueba')
    parser.add_argument('--all', action='store_true',
                       help='Ejecutar todo el setup')

    args = parser.parse_args()

    if not any([args.install, args.database, args.verify, args.test_data, args.all]):
        parser.print_help()
        return

    success = True

    if args.all or args.install:
        success &= install_dependencies()

    if args.all or args.database:
        success &= setup_database()

    if args.all or args.verify:
        success &= run_quick_test()

    if args.all or args.test_data:
        success &= create_test_data()

    if success:
        print("\n🎉 Setup completado exitosamente!")
        print("\nPara ejecutar tests:")
        print("  python Tests/analytics/run_tests.py")
        print("  pytest Tests/analytics/")
    else:
        print("\n❌ Setup falló. Revisa los errores arriba.")
        sys.exit(1)

if __name__ == '__main__':
    main()