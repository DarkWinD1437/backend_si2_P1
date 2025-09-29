# Tests del Módulo Analytics

Este directorio contiene tests exhaustivos para el módulo de Reportes y Analítica del sistema SmartCondominium.

## Estructura de Tests

```
Tests/analytics/
├── test_comprehensive_analytics.py    # Tests exhaustivos de API
├── test_load_performance.py          # Tests de carga y rendimiento
├── conftest.py                       # Configuración de pytest
├── requirements-test.txt             # Dependencias para tests
├── run_tests.py                      # Script para ejecutar tests
└── README.md                         # Esta documentación
```

## Endpoints Probados

### Reportes Financieros
- `GET /api/analytics/reportes-financieros/` - Listar reportes
- `POST /api/analytics/reportes-financieros/` - Crear reporte
- `GET /api/analytics/reportes-financieros/{id}/` - Detalle reporte
- `PUT /api/analytics/reportes-financieros/{id}/` - Actualizar completo
- `PATCH /api/analytics/reportes-financieros/{id}/` - Actualizar parcial
- `DELETE /api/analytics/reportes-financieros/{id}/` - Eliminar reporte
- `POST /api/analytics/reportes-financieros/generar_reporte/` - Generar reporte

### Reportes de Seguridad
- `GET /api/analytics/reportes-seguridad/` - Listar reportes
- `POST /api/analytics/reportes-seguridad/` - Crear reporte
- `GET /api/analytics/reportes-seguridad/{id}/` - Detalle reporte
- `PUT /api/analytics/reportes-seguridad/{id}/` - Actualizar completo
- `PATCH /api/analytics/reportes-seguridad/{id}/` - Actualizar parcial
- `DELETE /api/analytics/reportes-seguridad/{id}/` - Eliminar reporte
- `POST /api/analytics/reportes-seguridad/generar_reporte/` - Generar reporte

### Reportes de Uso de Áreas
- `GET /api/analytics/reportes-uso-areas/` - Listar reportes
- `POST /api/analytics/reportes-uso-areas/` - Crear reporte
- `GET /api/analytics/reportes-uso-areas/{id}/` - Detalle reporte
- `PUT /api/analytics/reportes-uso-areas/{id}/` - Actualizar completo
- `PATCH /api/analytics/reportes-uso-areas/{id}/` - Actualizar parcial
- `DELETE /api/analytics/reportes-uso-areas/{id}/` - Eliminar reporte
- `POST /api/analytics/reportes-uso-areas/generar_reporte/` - Generar reporte

### Predicciones de Morosidad
- `GET /api/analytics/predicciones-morosidad/` - Listar predicciones
- `POST /api/analytics/predicciones-morosidad/` - Crear predicción
- `GET /api/analytics/predicciones-morosidad/{id}/` - Detalle predicción
- `PUT /api/analytics/predicciones-morosidad/{id}/` - Actualizar completo
- `PATCH /api/analytics/predicciones-morosidad/{id}/` - Actualizar parcial
- `DELETE /api/analytics/predicciones-morosidad/{id}/` - Eliminar predicción
- `POST /api/analytics/predicciones-morosidad/generar_prediccion/` - Generar predicción IA

## Instalación de Dependencias

```bash
# Instalar dependencias de test
pip install -r Tests/analytics/requirements-test.txt

# O instalar individualmente
pip install pytest pytest-django pytest-cov pytest-xdist psutil locust
```

## Ejecución de Tests

### Usando el Script de Ejecución

```bash
# Ejecutar todos los tests
python Tests/analytics/run_tests.py

# Ejecutar tests específicos
python Tests/analytics/run_tests.py unit          # Tests de modelos y serializers
python Tests/analytics/run_tests.py integration   # Tests de integración
python Tests/analytics/run_tests.py load          # Tests de carga
python Tests/analytics/run_tests.py comprehensive # Tests exhaustivos

# Opciones adicionales
python Tests/analytics/run_tests.py --verbose     # Modo verbose
python Tests/analytics/run_tests.py --coverage    # Con reporte de cobertura
python Tests/analytics/run_tests.py --parallel    # Tests en paralelo
```

### Usando pytest Directamente

```bash
# Todos los tests
pytest Tests/analytics/

# Tests específicos
pytest Tests/analytics/test_models.py
pytest Tests/analytics/test_comprehensive_analytics.py

# Con cobertura
pytest --cov=backend.apps.analytics --cov-report=html Tests/analytics/

# Tests en paralelo
pytest -n auto Tests/analytics/
```

### Usando Django Test Runner

```bash
# Ejecutar tests usando Django
python Tests/analytics/run_tests.py --django

# O directamente
python manage.py test backend.apps.analytics
```

## Tipos de Tests Incluidos

### 1. Tests de Modelos (`test_models.py`)
- Creación de instancias
- Validación de campos
- Relaciones entre modelos
- Métodos de modelo

### 2. Tests de Serializers (`test_serializers.py`)
- Serialización de datos
- Validación de entrada
- Formato de salida

### 3. Tests de Vistas y APIs (`test_views.py`, `test_integration.py`)
- Endpoints CRUD completos
- Autenticación y autorización
- Validación de datos
- Manejo de errores

### 4. Tests Exhaustivos (`test_comprehensive_analytics.py`)
- **150+ tests individuales**
- Cobertura completa de todos los endpoints
- Tests de permisos por rol
- Tests de filtrado y búsqueda
- Tests de paginación
- Tests de validación
- Tests de workflow completo
- Tests de integración cruzada
- Tests de concurrencia
- Tests de manejo de errores

### 5. Tests de Carga y Rendimiento (`test_load_performance.py`)
- Tests de concurrencia
- Medición de tiempos de respuesta
- Tests de uso de memoria
- Análisis de queries SQL
- Simulación de carga mixta
- Tests de rate limiting

## Roles y Permisos Probados

### Administrador (`admin`)
- ✅ Acceso completo a todos los endpoints
- ✅ Puede generar todos los tipos de reportes
- ✅ Puede crear, leer, actualizar y eliminar todos los recursos

### Seguridad (`security`)
- ✅ Acceso de lectura a reportes
- ✅ Puede generar reportes de seguridad
- ❌ No puede generar reportes financieros o predicciones

### Mantenimiento (`maintenance`)
- ✅ Acceso de lectura limitado a reportes
- ❌ No puede generar reportes
- ❌ No puede crear recursos

### Residente (`resident`)
- ❌ Sin acceso a ningún endpoint de analytics

## Modelos de IA Probados

### Algoritmos de Predicción
- `regresion_logistica` - Regresión Logística
- `random_forest` - Random Forest
- `xgboost` - XGBoost
- `red_neuronal` - Red Neuronal
- `ensemble` - Ensemble de modelos

### Niveles de Confianza
- `alto` - Precisión ≥ 85%
- `medio` - Precisión 75-84%
- `bajo` - Precisión < 75%

## Tipos de Reportes Probados

### Financieros
- `ingresos` - Análisis de ingresos
- `egresos` - Análisis de gastos
- `balance` - Balance general
- `morosidad` - Análisis de morosidad

### Seguridad
- `accesos` - Reporte de accesos
- `incidentes` - Reporte de incidentes
- `alertas` - Reporte de alertas
- `auditoria` - Reporte de auditoría

### Uso de Áreas
- `gimnasio` - Uso del gimnasio
- `piscina` - Uso de la piscina
- `salon_eventos` - Uso del salón de eventos
- `estacionamiento` - Uso del estacionamiento
- `todas` - Todas las áreas

## Métricas de Rendimiento

Los tests de carga miden:
- **Throughput**: Requests por segundo
- **Latencia**: Tiempo de respuesta promedio
- **Tasa de éxito**: Porcentaje de requests exitosas
- **Uso de memoria**: Consumo de RAM
- **Queries SQL**: Número de consultas a BD

## Configuración de Base de Datos

Los tests usan una base de datos SQLite en memoria para:
- Aislamiento entre tests
- Velocidad de ejecución
- Fácil setup/teardown

## Reportes de Cobertura

Para generar reportes de cobertura:

```bash
# Reporte HTML
pytest --cov=backend.apps.analytics --cov-report=html Tests/analytics/

# Reporte en terminal
pytest --cov=backend.apps.analytics --cov-report=term Tests/analytics/
```

Los reportes se guardan en `htmlcov/index.html`

## Tests de Integración Continua

Para CI/CD, ejecutar:

```bash
# Tests rápidos (sin carga)
python Tests/analytics/run_tests.py comprehensive --parallel

# Tests completos (incluyendo carga)
python Tests/analytics/run_tests.py all --coverage
```

## Debugging de Tests

Para debuggear tests fallidos:

```bash
# Ejecutar con verbose y sin captura de output
pytest -v -s Tests/analytics/test_comprehensive_analytics.py::AnalyticsAPITestCase::test_reporte_financiero_create_admin
```

## Métricas de Calidad

- **Cobertura de código**: > 95%
- **Tasa de éxito**: > 99%
- **Tiempo de ejecución**: < 30s para tests básicos
- **Throughput**: > 50 req/s en tests de carga

## Notas Importantes

1. **Base de datos**: Los tests usan SQLite en memoria
2. **Autenticación**: Tests incluyen autenticación automática
3. **Permisos**: Tests validan permisos por rol de usuario
4. **Concurrencia**: Tests de carga usan múltiples threads
5. **Aislamiento**: Cada test es independiente
6. **Fixtures**: Datos de prueba se crean automáticamente

## Solución de Problemas

### Error de Import
```bash
pip install -r Tests/analytics/requirements-test.txt
```

### Error de Base de Datos
```bash
python manage.py migrate
```

### Tests Lentos
```bash
# Ejecutar en paralelo
python Tests/analytics/run_tests.py --parallel
```

### Memory Issues
```bash
# Ejecutar tests de carga individualmente
python Tests/analytics/run_tests.py load
```