"""
Suite completa de tests: Módulo 7 de Mantenimiento
Ejecutar con: python test_completo.py

Este script ejecuta todos los tests del módulo de mantenimiento:
- test_solicitudes.py
- test_tareas.py
- test_permisos.py
- test_integracion.py
"""

import subprocess
import sys
import os

def run_test(test_file, test_name):
    """Ejecuta un test individual y retorna resultado"""
    print(f"\n{'='*60}")
    print(f"🚀 EJECUTANDO: {test_name}")
    print('='*60)

    try:
        # Ejecutar el test
        result = subprocess.run(
            [sys.executable, test_file],
            capture_output=True,
            text=True,
            encoding='utf-8',
            cwd=os.path.dirname(test_file)
        )

        # Mostrar output
        if result.stdout:
            print(result.stdout)

        if result.stderr:
            print("STDERR:", result.stderr)

        # Verificar resultado
        if result.returncode == 0:
            print(f"✅ {test_name} - PASÓ")
            return True
        else:
            print(f"❌ {test_name} - FALLÓ")
            return False

    except Exception as e:
        print(f"💥 Error ejecutando {test_name}: {e}")
        return False

def main():
    """Función principal"""
    print("🧪 SUITE COMPLETA - Módulo 7: Gestión de Mantenimiento")
    print("=" * 70)
    print("Ejecutando todos los tests del módulo...")
    print()

    # Definir tests a ejecutar
    tests_dir = os.path.dirname(__file__)
    tests = [
        (os.path.join(tests_dir, "test_solicitudes.py"), "Tests de Solicitudes"),
        (os.path.join(tests_dir, "test_tareas.py"), "Tests de Tareas"),
        (os.path.join(tests_dir, "test_permisos.py"), "Tests de Permisos"),
        (os.path.join(tests_dir, "test_integracion.py"), "Tests de Integración"),
    ]

    resultados = []

    # Ejecutar cada test
    for test_file, test_name in tests:
        if os.path.exists(test_file):
            resultado = run_test(test_file, test_name)
            resultados.append(resultado)
        else:
            print(f"⚠️  Archivo no encontrado: {test_file}")
            resultados.append(False)

    # Resultados finales
    print(f"\n{'='*70}")
    print("📊 RESULTADOS FINALES DE LA SUITE")
    print('='*70)

    exitosos = sum(resultados)
    total = len(resultados)

    print(f"Tests ejecutados: {total}")
    print(f"Tests exitosos: {exitosos}")
    print(f"Tests fallidos: {total - exitosos}")

    print(f"\nDetalle por test:")
    test_names = ["Solicitudes", "Tareas", "Permisos", "Integración"]
    for i, (resultado, nombre) in enumerate(zip(resultados, test_names), 1):
        status = "✅ PASÓ" if resultado else "❌ FALLÓ"
        print(f"  {i}. {nombre}: {status}")

    # Evaluación final
    print(f"\n{'='*70}")
    if exitosos == total:
        print("🎉 ¡SUITE COMPLETA EXITOSA!")
        print("✅ Todos los tests del módulo de mantenimiento pasaron correctamente.")
        print("✅ El módulo está listo para producción.")
        print("\n📋 Resumen de funcionalidades validadas:")
        print("   • ✅ Creación de solicitudes de mantenimiento")
        print("   • ✅ Asignación de tareas a personal calificado")
        print("   • ✅ Seguimiento de estados y progreso")
        print("   • ✅ Sistema de permisos por roles")
        print("   • ✅ Filtros y búsqueda avanzada")
        print("   • ✅ Integración completa entre componentes")
        return True

    elif exitosos >= total * 0.8:  # 80% de éxito
        print("⚠️  SUITE MAYORITARIAMENTE EXITOSA")
        print(f"✅ {exitosos}/{total} tests pasaron ({exitosos/total*100:.1f}%)")
        print("El módulo es funcional pero requiere atención en algunos tests.")
        return False

    else:
        print("❌ SUITE FALLIDA")
        print(f"❌ Solo {exitosos}/{total} tests pasaron ({exitosos/total*100:.1f}%)")
        print("El módulo requiere correcciones importantes antes de producción.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
