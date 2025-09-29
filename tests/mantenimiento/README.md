# Tests - Módulo 7: Gestión de Mantenimiento

Esta carpeta contiene la suite completa de tests para validar el funcionamiento del Módulo de Gestión de Mantenimiento.

## Estructura de Tests

```
tests/mantenimiento/
├── test_solicitudes.py      # Tests específicos de solicitudes
├── test_tareas.py          # Tests específicos de tareas
├── test_permisos.py        # Tests de permisos y roles
├── test_integracion.py     # Tests de integración completa
├── test_completo.py        # Suite completa (ejecuta todos)
└── README.md              # Esta documentación
```

## Requisitos Previos

### Servidor Django
Asegurarse de que el servidor Django esté ejecutándose:
```bash
cd Backend_Django
python manage.py runserver 0.0.0.0:8000
```

### Usuarios de Test
Los tests requieren que existan los siguientes usuarios en la base de datos:
- `admin` / `clave123` (Administrador)
- `prueba` / `clave123` (Residente)
- `prueba2` / `clave123` (Mantenimiento)
- `prueba3` / `clave123` (Seguridad)

### Base de Datos
- Las migraciones deben estar aplicadas
- La app `maintenance` debe estar instalada

## Ejecución de Tests

### Suite Completa
Ejecutar todos los tests en secuencia:
```bash
cd Backend_Django/tests/mantenimiento
python test_completo.py
```

### Tests Individuales

#### Tests de Solicitudes
```bash
python test_solicitudes.py
```
Valida:
- Creación de solicitudes
- Listado y filtrado
- Detalles de solicitud
- Validaciones de permisos
- Manejo de errores

#### Tests de Tareas
```bash
python test_tareas.py
```
Valida:
- Asignación de tareas
- Actualización de estados
- Listado de tareas
- Transiciones de estado válidas

#### Tests de Permisos
```bash
python test_permisos.py
```
Valida:
- Acceso de administradores
- Permisos de residentes
- Acceso de personal de mantenimiento
- Restricciones de seguridad
- Autenticación requerida

#### Tests de Integración
```bash
python test_integracion.py
```
Valida:
- Flujo completo de mantenimiento
- Sincronización de estados
- Interacción entre componentes
- Filtros y búsquedas

## Resultados Esperados

### Suite Completa Exitosa
```
🎉 ¡SUITE COMPLETA EXITOSA!
✅ Todos los tests del módulo de mantenimiento pasaron correctamente.
✅ El módulo está listo para producción.
```

### Tests Individuales
Cada test individual debe mostrar:
- ✅ Tests exitosos con detalles
- ❌ Tests fallidos con diagnóstico
- 📊 Resumen final con porcentajes

## Casos de Error Comunes

### Error de Conexión
```
❌ Error: Connection refused
```
**Solución:** Verificar que el servidor Django esté ejecutándose en `http://127.0.0.1:8000`

### Error de Autenticación
```
❌ Login failed
```
**Solución:** Verificar que los usuarios de test existan en la base de datos

### Error de Permisos
```
❌ Expected 403, got 200
```
**Solución:** Revisar configuración de roles y permisos en el código

### Error de Base de Datos
```
❌ Migration not applied
```
**Solución:** Ejecutar `python manage.py migrate` en el directorio del proyecto

## Configuración de Tests

### Variables de Configuración
```python
BASE_URL = 'http://127.0.0.1:8000'  # URL del servidor
TIMEOUT = 30                        # Timeout por request
RETRIES = 3                         # Reintentos en caso de error
```

### Credenciales
Las credenciales están hardcodeadas para testing. En producción, usar variables de entorno.

## Métricas de Calidad

### Cobertura Objetivo
- **Funcionalidades:** 100% (todas las tareas implementadas)
- **Endpoints:** 100% (todos los endpoints probados)
- **Permisos:** 100% (todos los roles validados)
- **Casos Edge:** 80% (errores y casos límite)

### Tiempo de Ejecución
- Suite completa: < 2 minutos
- Test individual: < 30 segundos

## Mantenimiento de Tests

### Agregar Nuevos Tests
1. Crear archivo `test_nuevo.py`
2. Implementar función `main()` que retorne `True/False`
3. Agregar a `test_completo.py`
4. Actualizar este README

### Actualizar Tests Existentes
- Modificar credenciales si cambian
- Actualizar URLs si cambian endpoints
- Revisar validaciones si cambia lógica de negocio

## Reportes de Testing

### Salida de Consola
Cada test genera salida detallada con:
- ✅ Operaciones exitosas
- ❌ Errores específicos
- 📊 Resúmenes numéricos

### Logs de Error
En caso de fallos, revisar:
- Código de estado HTTP
- Mensaje de error del servidor
- Datos enviados/recibidos

## Integración con CI/CD

### GitHub Actions
```yaml
- name: Run Maintenance Tests
  run: |
    cd Backend_Django/tests/mantenimiento
    python test_completo.py
```

### Requisitos de Aprobación
- ✅ Suite completa: 100% exitosa
- ⚠️  Desarrollo: > 80% exitosa
- ❌ Producción: No desplegar con tests fallidos

## Soporte

Para issues con los tests:
1. Verificar configuración del entorno
2. Revisar logs del servidor Django
3. Validar estado de la base de datos
4. Consultar documentación de la API

## Historial de Cambios

- **v1.0** - Tests iniciales completos
- Implementación de todas las funcionalidades del módulo
- Validación de permisos y roles
- Tests de integración end-to-end