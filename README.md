# 🏢 Smart Condominium Backend - Django

## 📁 Estructura del Proyecto Organizada

```
Backend_Django/
├── 🔧 api/                    # API endpoints básicos
├── 🏗️ backend/                # Configuración principal Django
│   ├── apps/users/           # App de usuarios (Módulo 1)
│   ├── settings.py           # Configuración Django
│   └── urls.py               # URLs principales
├── 🏠 condominio/             # App principal del condominio
├── 📊 data/                   # Archivos de datos ⭐ ORGANIZADO
│   ├── seed_data.json        # Datos semilla para BD
│   ├── login_data.json       # Datos de login para tests
│   └── README.md             # Documentación de datos
├── 📚 docs/                   # Documentación completa ⭐ ORGANIZADO
│   ├── informes_tareas/      # Informes principales
│   ├── modulo1_usuarios/     # Docs específicas Módulo 1
│   ├── README.md             # Índice de documentación
│   └── [otros archivos].md   # Documentación general
├── 🔧 scripts/               # Scripts auxiliares ⭐ ORGANIZADO
│   ├── poblado_db/          # Scripts poblado de base de datos
│   ├── testing_manual/      # Scripts testing manual
│   ├── utilidades/         # Scripts de utilidades
│   └── README.md           # Documentación de scripts
├── 🧪 tests/                 # Tests unitarios ⭐ LIMPIO
│   └── modulo1_usuarios/    # Tests Módulo 1 únicamente
├── 🔐 .env                   # Variables de entorno
├── 🐍 manage.py              # Script principal Django
├── 📋 requirements.txt       # Dependencias Python
└── 🌐 venv/                  # Entorno virtual Python
```

## 🎯 Estado del Proyecto

### ✅ MÓDULO 1: GESTIÓN DE USUARIOS Y AUTENTICACIÓN - COMPLETADO
- **T1**: Registro de usuarios ✅
- **T2**: Login y Logout ✅
- **T3**: Gestión de perfil de usuario ✅
- **T4**: Asignar rol a usuario ✅

### 📊 Estadísticas
- **4/4 tareas completadas** (100%)
- **46+ tests unitarios** ejecutados exitosamente
- **Documentación completa** y organizada
- **Estructura limpia** y mantenible

## 🚀 Inicio Rápido

### 1. Preparar Entorno
```bash
# Activar entorno virtual
venv/Scripts/activate  # Windows
source venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt
```

### 2. Configurar Base de Datos
```bash
# Migraciones
python manage.py makemigrations
python manage.py migrate

# Poblar con datos iniciales
python scripts/poblado_db/poblar_db_mejorado.py

# Crear admin (opcional)
python scripts/utilidades/update_admin_password.py
```

### 3. Ejecutar Servidor
```bash
python manage.py runserver
```

### 4. Ejecutar Tests
```bash
# Tests unitarios específicos
python manage.py test tests.modulo1_usuarios.test_assign_role

# Tests manuales (servidor debe estar corriendo)
python scripts/testing_manual/test_api.py
```

## 📋 Comandos Útiles

### 🔧 Administración
```bash
# Verificar usuarios en BD
python scripts/utilidades/check_users.py

# Actualizar contraseña admin
python scripts/utilidades/update_admin_password.py

# Investigar estado de BD
python scripts/utilidades/investigar_db.py
```

### 🧪 Testing
```bash
# Tests unitarios por módulo
python manage.py test tests.modulo1_usuarios

# Tests manuales específicos
python scripts/testing_manual/test_registro.py
python scripts/testing_manual/test_assign_role_manual.py
```

### 🗃️ Base de Datos
```bash
# Poblar BD con diferentes scripts
python scripts/poblado_db/poblar_db.py              # Básico
python scripts/poblado_db/poblar_db_mejorado.py     # Recomendado
python scripts/poblado_db/poblar_completo_simple.py # Completo
```

## 🌐 API Endpoints Principales

### Autenticación
- `POST /api/login/` - Iniciar sesión
- `POST /api/logout/` - Cerrar sesión
- `POST /api/logout-all/` - Cerrar todas las sesiones

### Usuarios
- `POST /api/backend/users/register/` - Registro
- `GET /api/profile/` - Perfil completo
- `POST /api/profile/change-password/` - Cambiar contraseña
- `POST /api/users/{id}/assign-role/` - Asignar rol (admin)

### Información
- `GET /api/status/` - Estado de la API
- `GET /api/users/` - Listar usuarios (admin)

## 📚 Documentación

### 📋 Informes Principales
- [`docs/informes_tareas/RESUMEN_FINAL_MODULO1.md`](./docs/informes_tareas/RESUMEN_FINAL_MODULO1.md) - Resumen completo
- [`docs/README.md`](./docs/README.md) - Índice de documentación

### 📋 Informes por Tarea
- [`docs/modulo1_usuarios/INFORME_REGISTRO_USUARIO.md`](./docs/modulo1_usuarios/INFORME_REGISTRO_USUARIO.md) - T1
- [`docs/modulo1_usuarios/INFORME_LOGIN_LOGOUT.md`](./docs/modulo1_usuarios/INFORME_LOGIN_LOGOUT.md) - T2
- [`docs/modulo1_usuarios/INFORME_PERFIL_USUARIO.md`](./docs/modulo1_usuarios/INFORME_PERFIL_USUARIO.md) - T3
- [`docs/modulo1_usuarios/INFORME_ASSIGN_ROLE.md`](./docs/modulo1_usuarios/INFORME_ASSIGN_ROLE.md) - T4

## 🔧 Scripts Organizados

### 📂 [`scripts/poblado_db/`](./scripts/poblado_db/)
Scripts para poblar la base de datos con datos iniciales

### 📂 [`scripts/testing_manual/`](./scripts/testing_manual/)
Scripts para pruebas manuales de funcionalidades

### 📂 [`scripts/utilidades/`](./scripts/utilidades/)
Scripts auxiliares para mantenimiento y administración

### 📂 [`data/`](./data/)
Archivos de datos JSON para scripts

## 🏆 Características Destacadas

### ✅ Organización Perfecta
- **Estructura limpia**: Sin archivos sueltos
- **Carpetas categorizadas**: Scripts, docs, datos organizados
- **Fácil navegación**: READMEs explicativos en cada carpeta
- **Mantenibilidad**: Fácil localizar y modificar archivos

### ✅ Funcionalidad Completa
- **Sistema de usuarios robusto**: Registro, login, perfil, roles
- **API RESTful completa**: Todos los endpoints documentados
- **Tests exhaustivos**: Unitarios e integración
- **Seguridad implementada**: Autenticación, autorización, validaciones

### ✅ Documentación Exhaustiva
- **Informes detallados**: Por cada tarea implementada
- **Guías de uso**: Para desarrolladores y administradores
- **Ejemplos prácticos**: Código, cURL, JavaScript
- **Troubleshooting**: Soluciones a problemas comunes

## 🎉 Proyecto Listo para Producción

El **Módulo 1: Gestión de Usuarios y Autenticación** está completamente implementado, probado, documentado y organizado. El sistema incluye:

- ✅ **4 tareas completadas** con funcionalidad robusta
- ✅ **46+ tests unitarios** todos exitosos  
- ✅ **Documentación completa** y bien organizada
- ✅ **Estructura de proyecto limpia** y profesional
- ✅ **Scripts organizados** por categoría y función
- ✅ **API completa** lista para frontend

---

**🚀 SMART CONDOMINIUM BACKEND - MÓDULO 1 COMPLETADO**

*Sistema de gestión de usuarios completo, seguro, bien documentado y perfectamente organizado.*

**Última actualización**: 11 de Septiembre de 2025
