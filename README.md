# 🏢 Smart Condominium Backend - Django

Sistema completo de gestión para condominios desarrollado con Django REST Framework.

## � Requisitos Previos

- Python 3.8+
- PostgreSQL 12+
- Git

## 🛠️ Instalación y Configuración

### 1. Clonar el repositorio
```bash
git clone https://github.com/DarkWinD1437/backend_si2_P1.git
cd backend_si2_P1
```

### 2. Crear entorno virtual
```bash
python -m venv venv
# En Windows:
venv\Scripts\activate
# En Linux/Mac:
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

**⚠️ IMPORTANTE:** Nunca subas archivos `.env` al repositorio.

Copia el archivo de ejemplo y configura tus credenciales:
```bash
cp .env.example .env
```

Edita el archivo `.env` con tus configuraciones:
```bash
# Configuración de Base de Datos
DB_NAME=tu_base_de_datos
DB_USER=tu_usuario_postgres
DB_PASSWORD=tu_contraseña_segura
DB_HOST=localhost
DB_PORT=5432

# Configuración de Django
SECRET_KEY=tu-clave-secreta-muy-larga-y-segura-aqui
DEBUG=True
```

### 5. Configurar PostgreSQL

Crea la base de datos en PostgreSQL:
```sql
CREATE DATABASE tu_base_de_datos;
CREATE USER tu_usuario_postgres WITH PASSWORD 'tu_contraseña_segura';
GRANT ALL PRIVILEGES ON DATABASE tu_base_de_datos TO tu_usuario_postgres;
```

### 6. Ejecutar migraciones
```bash
python manage.py migrate
```

### 7. Poblar base de datos (opcional)
```bash
# Poblar con datos de prueba
python scripts/poblado_db/poblar_completo_simple.py
```

### 8. Crear superusuario (opcional)
```bash
python manage.py createsuperuser
```

### 9. Ejecutar el servidor
```bash
python manage.py runserver
```

El servidor estará disponible en: http://localhost:8000

## 🔒 Seguridad y Mejores Prácticas

### ✅ Archivo .gitignore Configurado
- ✅ Archivos `.env` ignorados automáticamente
- ✅ Credenciales sensibles protegidas
- ✅ Archivos temporales y cache ignorados

### ✅ Variables de Entorno Seguras
- ✅ Credenciales de BD en variables de entorno
- ✅ SECRET_KEY configurable
- ✅ DEBUG=False por defecto en producción

### ✅ Nunca Subas al Repositorio
- ❌ `.env` (contiene credenciales reales)
- ❌ `venv/` (entorno virtual)
- ❌ `*.log` (logs con información sensible)
- ❌ `*.sqlite3` (bases de datos locales)

## 🎯 Estado del Proyecto

### ✅ MÓDULO 1: GESTIÓN DE USUARIOS Y AUTENTICACIÓN - COMPLETADO
- **T1**: Registro de usuarios ✅
- **T2**: Login y Logout ✅
- **T3**: Gestión de perfil de usuario ✅
- **T4**: Asignar rol a usuario ✅

### ✅ MÓDULO 2: GESTIÓN FINANCIERA - COMPLETADO
- **T1**: Crear cuota de condominio ✅
- **T2**: Pagar cuota online ✅
- **T3**: Generar estado de cuenta ✅
- **T4**: Generar comprobante de pago ✅

### ✅ MÓDULO 3: COMUNICACIONES - COMPLETADO
- **T1**: Crear anuncio ✅
- **T2**: Enviar mensaje directo ✅
- **T3**: Ver bandeja de entrada ✅
- **T4**: Marcar como leído ✅

### ✅ MÓDULO 4: RESERVAS DE ÁREAS COMUNES - COMPLETADO
- **T1**: Consultar disponibilidad ✅
- **T2**: Reservar área común ✅
- **T3**: Confirmar reserva con pago ✅
- **T4**: Cancelar reserva ✅

### 📊 Estadísticas Generales
- **16/16 tareas completadas** (100%)
- **200+ tests unitarios** ejecutados exitosamente
- **Documentación completa** para todos los módulos
- **Testing avanzado** (stress, edge cases, concurrencia)
- **Integración completa** con React y Flutter
- **Estructura limpia** y mantenible
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
