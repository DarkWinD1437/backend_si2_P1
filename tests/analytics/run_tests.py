#!/usr/bin/env python
"""
Script para ejecutar tests del módulo Analytics
"""

import os
import sys
import subprocess
import argparse

def run_tests(test_type='all', verbose=False, coverage=False, parallel=False):
    """
    Ejecutar tests del módulo Analytics

    Args:
        test_type: Tipo de tests a ejecutar ('all', 'unit', 'integration', 'load')
        verbose: Modo verbose
        coverage: Incluir reporte de cobertura
        parallel: Ejecutar tests en paralelo
    """

    # Cambiar al directorio del proyecto
    project_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(project_dir)

    # Configurar comando base
    cmd = ['python', '-m', 'pytest']

    # Agregar opciones
    if verbose:
        cmd.append('-v')
    else:
        cmd.append('-q')

    if coverage:
        cmd.extend(['--cov=backend.apps.analytics', '--cov-report=html', '--cov-report=term'])

    if parallel:
        cmd.extend(['-n', 'auto'])

    # Configurar path de tests
    test_path = 'Tests/analytics/'

    if test_type == 'unit':
        cmd.append(f'{test_path}test_models.py')
        cmd.append(f'{test_path}test_serializers.py')
    elif test_type == 'integration':
        cmd.append(f'{test_path}test_views.py')
        cmd.append(f'{test_path}test_integration.py')
    elif test_type == 'load':
        cmd.append(f'{test_path}test_load_performance.py')
    elif test_type == 'comprehensive':
        cmd.append(f'{test_path}test_comprehensive_analytics.py')
    else:  # all
        cmd.append(test_path)

    # Agregar configuración de Django
    env = os.environ.copy()
    env['DJANGO_SETTINGS_MODULE'] = 'backend.settings'

    print(f"Ejecutando: {' '.join(cmd)}")
    print(f"Directorio: {os.getcwd()}")

    try:
        result = subprocess.run(cmd, env=env, check=True)
        print("✅ Tests ejecutados exitosamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error ejecutando tests: {e}")
        return False

def run_django_tests():
    """Ejecutar tests usando el test runner de Django"""
    project_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.chdir(project_dir)

    cmd = ['python', 'manage.py', 'test', 'backend.apps.analytics']

    env = os.environ.copy()
    env['DJANGO_SETTINGS_MODULE'] = 'backend.settings'

    print(f"Ejecutando tests de Django: {' '.join(cmd)}")

    try:
        result = subprocess.run(cmd, env=env, check=True)
        print("✅ Tests de Django ejecutados exitosamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error ejecutando tests de Django: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description='Ejecutar tests del módulo Analytics')
    parser.add_argument('test_type', nargs='?', default='all',
                       choices=['all', 'unit', 'integration', 'load', 'comprehensive'],
                       help='Tipo de tests a ejecutar')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Modo verbose')
    parser.add_argument('--coverage', '-c', action='store_true',
                       help='Incluir reporte de cobertura')
    parser.add_argument('--parallel', '-p', action='store_true',
                       help='Ejecutar tests en paralelo')
    parser.add_argument('--django', '-d', action='store_true',
                       help='Usar test runner de Django en lugar de pytest')

    args = parser.parse_args()

    if args.django:
        success = run_django_tests()
    else:
        success = run_tests(args.test_type, args.verbose, args.coverage, args.parallel)

    sys.exit(0 if success else 1)

if __name__ == '__main__':
    main()