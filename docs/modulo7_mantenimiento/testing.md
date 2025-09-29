# Testing - Módulo 7: Gestión de Mantenimiento

## Estrategia de Testing

### Niveles de Testing
1. **Unit Tests**: Funciones individuales y métodos
2. **Integration Tests**: Endpoints API completos
3. **End-to-End Tests**: Flujos completos de usuario

### Herramientas Utilizadas
- **Requests**: Para testing de API HTTP
- **JSON**: Para validación de respuestas
- **Datetime**: Para validación de timestamps

## Estructura de Tests

### Ubicación
```
Backend_Django/tests/mantenimiento/
├── test_solicitudes.py          # Tests de solicitudes
├── test_tareas.py              # Tests de tareas
├── test_permisos.py            # Tests de permisos
├── test_integracion.py         # Tests de integración
└── test_completo.py            # Suite completa
```

## Tests Individuales

### 1. Test de Solicitudes (`test_solicitudes.py`)

#### Crear Solicitud
```python
def test_crear_solicitud_mantenimiento():
    """POST /api/maintenance/solicitudes/"""
    data = {
        "descripcion": "Luz fundida en pasillo",
        "ubicacion": "Pasillo piso 2",
        "prioridad": "media"
    }

    response = requests.post(
        f"{BASE_URL}/api/maintenance/solicitudes/",
        json=data,
        headers=get_auth_headers(token)
    )

    assert response.status_code == 201
    solicitud = response.json()
    assert solicitud['estado'] == 'pendiente'
    assert solicitud['prioridad'] == 'media'
    return solicitud['id']
```

#### Listar Solicitudes
```python
def test_listar_solicitudes():
    """GET /api/maintenance/solicitudes/"""
    response = requests.get(
        f"{BASE_URL}/api/maintenance/solicitudes/",
        headers=get_auth_headers(token)
    )

    assert response.status_code == 200
    solicitudes = response.json()
    assert isinstance(solicitudes, list)
    assert len(solicitudes) >= 0
```

#### Filtrar Solicitudes
```python
def test_filtrar_solicitudes():
    """GET /api/maintenance/solicitudes/?estado=pendiente"""
    params = {'estado': 'pendiente'}

    response = requests.get(
        f"{BASE_URL}/api/maintenance/solicitudes/",
        params=params,
        headers=get_auth_headers(token)
    )

    assert response.status_code == 200
    solicitudes = response.json()
    for solicitud in solicitudes:
        assert solicitud['estado'] == 'pendiente'
```

### 2. Test de Tareas (`test_tareas.py`)

#### Asignar Tarea
```python
def test_asignar_tarea(solicitud_id):
    """POST /api/maintenance/solicitudes/{id}/asignar_tarea/"""
    data = {
        "asignado_a_id": 2,  # ID de usuario de mantenimiento
        "descripcion_tarea": "Reparar luz fundida",
        "notas": "Verificar circuito"
    }

    response = requests.post(
        f"{BASE_URL}/api/maintenance/solicitudes/{solicitud_id}/asignar_tarea/",
        json=data,
        headers=get_auth_headers(admin_token)
    )

    assert response.status_code == 201
    tarea = response.json()
    assert tarea['estado'] == 'asignada'
    assert tarea['asignado_a_info']['id'] == 2
    return tarea['id']
```

#### Actualizar Estado
```python
def test_actualizar_estado_tarea(tarea_id):
    """POST /api/maintenance/tareas/{id}/actualizar_estado/"""
    data = {
        "estado": "en_progreso",
        "notas": "Iniciando reparación"
    }

    response = requests.post(
        f"{BASE_URL}/api/maintenance/tareas/{tarea_id}/actualizar_estado/",
        json=data,
        headers=get_auth_headers(maintenance_token)
    )

    assert response.status_code == 200
    tarea = response.json()
    assert tarea['estado'] == 'en_progreso'
    assert "Iniciando reparación" in tarea['notas']
```

### 3. Test de Permisos (`test_permisos.py`)

#### Acceso Denegado para Residente
```python
def test_residente_no_puede_asignar():
    """Residente no puede asignar tareas"""
    data = {
        "asignado_a_id": 2,
        "descripcion_tarea": "Test",
        "notas": "Test"
    }

    response = requests.post(
        f"{BASE_URL}/api/maintenance/solicitudes/1/asignar_tarea/",
        json=data,
        headers=get_auth_headers(resident_token)
    )

    assert response.status_code == 403
    error = response.json()
    assert 'permisos' in error['error'].lower()
```

#### Acceso de Solo Lectura para Seguridad
```python
def test_seguridad_solo_lectura():
    """Personal de seguridad solo puede leer"""
    # Intentar crear solicitud
    data = {
        "descripcion": "Test",
        "ubicacion": "Test",
        "prioridad": "baja"
    }

    response = requests.post(
        f"{BASE_URL}/api/maintenance/solicitudes/",
        json=data,
        headers=get_auth_headers(security_token)
    )

    assert response.status_code == 403

    # Pero puede leer
    response = requests.get(
        f"{BASE_URL}/api/maintenance/solicitudes/",
        headers=get_auth_headers(security_token)
    )

    assert response.status_code == 200
```

### 4. Test de Integración (`test_integracion.py`)

#### Flujo Completo de Mantenimiento
```python
def test_flujo_completo_mantenimiento():
    """Prueba el flujo completo: solicitud -> asignación -> completado"""

    # 1. Crear solicitud
    solicitud_id = test_crear_solicitud_mantenimiento()

    # 2. Asignar tarea
    tarea_id = test_asignar_tarea(solicitud_id)

    # 3. Iniciar trabajo
    test_actualizar_estado_tarea(tarea_id, "en_progreso")

    # 4. Completar trabajo
    test_actualizar_estado_tarea(tarea_id, "completada")

    # 5. Verificar estados finales
    solicitud = get_solicitud(solicitud_id)
    tarea = get_tarea(tarea_id)

    assert solicitud['estado'] == 'completada'
    assert tarea['estado'] == 'completada'
    assert tarea['fecha_completado'] is not None
```

## Configuración de Testing

### Variables de Entorno
```python
BASE_URL = 'http://127.0.0.1:8000'

# Credenciales de test
ADMIN_USER = {'username': 'admin', 'password': 'clave123'}
RESIDENT_USER = {'username': 'prueba', 'password': 'clave123'}
MAINTENANCE_USER = {'username': 'prueba2', 'password': 'clave123'}
SECURITY_USER = {'username': 'prueba3', 'password': 'clave123'}
```

### Funciones Auxiliares
```python
def get_auth_headers(token):
    """Retorna headers con token de autenticación"""
    return {
        'Authorization': f'Token {token}',
        'Content-Type': 'application/json'
    }

def login_user(user_data):
    """Login y retorno de token"""
    response = requests.post(
        f'{BASE_URL}/api/auth-token/',
        json=user_data,
        headers={'Content-Type': 'application/json'}
    )
    return response.json()['token']
```

## Ejecución de Tests

### Ejecutar Todos los Tests
```bash
cd Backend_Django/tests/mantenimiento
python -m pytest  # Si se implementan con pytest
# o
python test_completo.py
```

### Ejecutar Tests Individuales
```bash
python test_solicitudes.py
python test_tareas.py
python test_permisos.py
python test_integracion.py
```

### Tests con Cobertura
```bash
coverage run --source='../backend/apps/maintenance' test_completo.py
coverage report
```

## Casos de Error Testing

### Validaciones de Datos
- Campos requeridos faltantes
- Datos con formato incorrecto
- IDs inexistentes
- Estados inválidos

### Permisos
- Acceso sin autenticación
- Roles sin permisos suficientes
- Modificación de recursos no propios

### Estados
- Transiciones de estado inválidas
- Estados duplicados
- Actualizaciones concurrentes

## Métricas de Testing

### Cobertura Objetivo
- **Líneas de código**: > 80%
- **Ramas condicionales**: > 75%
- **Funciones**: 100%

### Tipos de Tests
- **Tests unitarios**: 60%
- **Tests de integración**: 30%
- **Tests E2E**: 10%

## Automatización

### CI/CD Integration
```yaml
# .github/workflows/test.yml
- name: Run Maintenance Module Tests
  run: |
    cd Backend_Django/tests/mantenimiento
    python test_completo.py
```

### Reportes de Testing
- Resultados en JSON para integración con herramientas
- Screenshots de errores (futuro)
- Métricas de performance

## Mantenimiento de Tests

### Actualización de Tests
- Actualizar credenciales cuando cambien
- Modificar tests cuando cambie la API
- Agregar nuevos casos para nuevas funcionalidades

### Documentación de Tests
- Comentarios detallados en cada test
- Documentación de casos edge
- Guías para escribir nuevos tests