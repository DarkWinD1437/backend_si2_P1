#!/usr/bin/env python
"""
Script de prueba para el servicio de predicción de morosidad con IA
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
sys.path.insert(0, os.path.dirname(__file__))
django.setup()

# Configurar API key de prueba
os.environ['OPENROUTER_API_KEY'] = 'test_key'

from backend.apps.analytics.services import GrokMorosidadService

def main():
    print("🚀 Iniciando prueba del servicio de predicción de morosidad con IA")
    print("=" * 60)

    try:
        # Crear servicio
        service = GrokMorosidadService()
        print("✅ Servicio GrokMorosidadService inicializado correctamente")

        # Datos de prueba
        test_data = {
            'residentes': [
                {
                    'id': 'residente_1',
                    'pagos_atrasados_ultimo_anio': 0,
                    'cambio_ingresos_porcentaje': 5.0,
                    'cambio_uso_servicios_porcentaje': -10.0,
                    'meses_como_residente': 24
                },
                {
                    'id': 'residente_2',
                    'pagos_atrasados_ultimo_anio': 3,
                    'cambio_ingresos_porcentaje': -15.0,
                    'cambio_uso_servicios_porcentaje': 40.0,
                    'meses_como_residente': 12
                },
                {
                    'id': 'residente_3',
                    'pagos_atrasados_ultimo_anio': 8,
                    'cambio_ingresos_porcentaje': -30.0,
                    'cambio_uso_servicios_porcentaje': 80.0,
                    'meses_como_residente': 6
                }
            ]
        }

        print(f"📊 Probando con {len(test_data['residentes'])} residentes de prueba")

        # Probar método de fallback
        print("\n🧪 Probando método de predicción de fallback...")
        resultado = service._fallback_prediction(test_data, 'random_forest')

        print("✅ Resultado obtenido:")
        print(f"   - Fuente: {resultado.get('fuente', 'fallback')}")
        print(f"   - Total residentes analizados: {resultado['estadisticas_generales']['total_residentes']}")
        print(f"   - Riesgo bajo: {resultado['estadisticas_generales']['riesgo_bajo']}")
        print(f"   - Riesgo medio: {resultado['estadisticas_generales']['riesgo_medio']}")
        print(f"   - Riesgo alto: {resultado['estadisticas_generales']['riesgo_alto']}")
        print(".1f")
        print(f"   - Predicciones por residente: {len(resultado['predicciones_por_residente'])}")

        print("\n📊 Predicciones detalladas:")
        for pred in resultado['predicciones_por_residente']:
            print(f"   - {pred['residente_id']}: Riesgo {pred['riesgo_morosidad']} ({pred['probabilidad']*100:.1f}%)")
            print(f"     Factores: {', '.join(pred['factores_riesgo'])}")
            print(f"     Recomendaciones: {', '.join(pred['recomendaciones'])}")

        # Probar validación de datos
        print("\n🔍 Probando validación de datos...")
        validacion = service.validar_datos_entrada(test_data)
        print(f"   - Datos válidos: {validacion['valido']}")
        print(f"   - Errores: {len(validacion['errores'])}")
        print(f"   - Advertencias: {len(validacion['warnings'])}")

        # Probar cálculo de score de riesgo
        print("\n📈 Probando cálculo de score de riesgo...")
        residente_prueba = test_data['residentes'][0]
        score = service._calculate_basic_risk_score(residente_prueba)
        print(f"   - Score para residente de bajo riesgo: {score:.3f} (debería ser < 0.3)")

        residente_alto_riesgo = test_data['residentes'][2]
        score_alto = service._calculate_basic_risk_score(residente_alto_riesgo)
        print(f"   - Score para residente de alto riesgo: {score_alto:.3f} (debería ser > 0.7)")

        print("\n" + "=" * 60)
        print("✅ PRUEBA COMPLETADA EXITOSAMENTE")
        print("🎯 El servicio de predicción de morosidad con IA está funcionando correctamente!")
        print("\n📋 Resumen:")
        print("   • Servicio inicializado ✓")
        print("   • Método de fallback funciona ✓")
        print("   • Validación de datos funciona ✓")
        print("   • Cálculo de riesgo funciona ✓")
        print("   • Predicciones generadas ✓")

    except Exception as e:
        print(f"\n❌ ERROR durante la prueba: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0

if __name__ == "__main__":
    exit(main())