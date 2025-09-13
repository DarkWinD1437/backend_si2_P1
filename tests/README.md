# 🧪 Tests del Sistema de Condominio

Este directorio contiene todos los scripts de pruebas organizados por módulos para mantener una estructura limpia y fácil de navegar.

## 📁 Estructura de Carpetas

### `modulo1_usuarios/`
Scripts para probar funcionalidades del módulo de usuarios:

- `test_assign_role.py` - Pruebas de asignación de roles
- `test_endpoint_completo.py` - Pruebas completas de endpoints de usuarios
- `test_final_complete.py` - Pruebas finales completas del módulo
- `test_login_logout.py` - Pruebas básicas de autenticación
- `test_login_logout_advanced.py` - Pruebas avanzadas de autenticación
- `test_profile_fixes.py` - Pruebas de correcciones de perfil
- `test_profile_management.py` - Pruebas de gestión de perfiles

### `modulo2_finanzas/`
Scripts para probar funcionalidades del módulo financiero:

- `test_comprobantes_completo.py` - Pruebas completas de comprobantes de pago
- `test_pagos_completo.py` - Pruebas completas del sistema de pagos

### `modulo3_comunicacion/`
Scripts para probar funcionalidades del módulo de comunicaciones:

- `test_avisos_completo.py` - Pruebas completas del sistema de avisos generales

## 🚀 Cómo Ejecutar los Tests

### Desde el directorio raíz del proyecto:

```bash
# Test específico del módulo 1 (usuarios)
python tests/modulo1_usuarios/test_login_logout.py

# Test específico del módulo 2 (finanzas)
python tests/modulo2_finanzas/test_pagos_completo.py

# Test específico del módulo 3 (comunicaciones)
python tests/modulo3_comunicacion/test_avisos_completo.py
```

### Desde cada carpeta de módulo:

```bash
# Navegar a la carpeta del módulo
cd tests/modulo1_usuarios
python test_login_logout.py

cd ../modulo2_finanzas
python test_pagos_completo.py

cd ../modulo3_comunicacion
python test_avisos_completo.py
```

## 📋 Requisitos

- Django 5.x corriendo en `http://127.0.0.1:8000`
- Base de datos poblada con datos de prueba
- Usuarios de prueba creados (admin, residentes, etc.)

## 🔧 Configuración

Antes de ejecutar cualquier test, asegúrate de:

1. **Servidor en funcionamiento:**
   ```bash
   python manage.py runserver
   ```

2. **Base de datos actualizada:**
   ```bash
   python manage.py migrate
   python manage.py makemigrations
   ```

3. **Datos de prueba poblados:**
   ```bash
   python scripts/poblado_db/poblar_completo_simple.py
   ```

## 📊 Cobertura de Tests

| Módulo | Funcionalidad | Estado |
|--------|---------------|--------|
| Usuarios | Registro/Login | ✅ |
| Usuarios | Gestión de Perfiles | ✅ |
| Usuarios | Asignación de Roles | ✅ |
| Finanzas | Sistema de Pagos | ✅ |
| Finanzas | Comprobantes PDF | ✅ |
| Comunicaciones | Avisos Generales | ✅ |

## 🐛 Solución de Problemas

### Error de Conexión
- Verificar que el servidor Django esté corriendo
- Confirmar que la URL base sea correcta (`http://127.0.0.1:8000`)

### Error de Autenticación
- Verificar que los usuarios de prueba existan
- Ejecutar script de creación de usuarios si es necesario

### Error de Base de Datos
- Ejecutar migraciones pendientes
- Repoblar la base de datos con datos de prueba

## 📝 Notas

- Todos los tests están diseñados para ser independientes
- Se recomienda ejecutar los tests en un ambiente de desarrollo
- Los tests crean y utilizan datos de prueba que no afectan datos reales