# 📁 Scripts del Proyecto

Esta carpeta contiene todos los scripts auxiliares del proyecto organizados por categoría.

## 📂 Estructura de Subcarpetas

### 🗃️ `/poblado_db/` - Scripts de Poblado de Base de Datos
Contiene scripts para poblar la base de datos con datos iniciales:
- `poblar_completo_simple.py` - Script de poblado completo simple
- `poblar_db.py` - Script básico de poblado
- `poblar_db_mejorado.py` - Script de poblado mejorado con validaciones
- `populate_simple.py` - Script de población simple

### 🧪 `/testing_manual/` - Scripts de Testing Manual
Scripts para pruebas manuales de funcionalidades:
- `test_api.py` - Tests manuales de la API
- `test_registro.py` - Tests manuales de registro
- `test_registro_completo.py` - Tests completos de registro
- `test_assign_role_manual.py` - Tests manuales de asignación de roles

### 🔧 `/utilidades/` - Scripts de Utilidades
Scripts auxiliares para mantenimiento y administración:
- `check_users.py` - Script para verificar usuarios en BD
- `create_test_users.py` - Script para crear usuarios de prueba
- `investigar_db.py` - Script para investigar estado de BD
- `update_admin_password.py` - Script para actualizar contraseña de admin

## 🚀 Uso de Scripts

### Para Poblar Base de Datos:
```bash
# Desde el directorio raíz del proyecto
python scripts/poblado_db/poblar_db_mejorado.py
```

### Para Testing Manual:
```bash
# Asegúrate de que el servidor esté corriendo
python scripts/testing_manual/test_api.py
```

### Para Utilidades:
```bash
# Actualizar contraseña de admin
python scripts/utilidades/update_admin_password.py

# Verificar usuarios
python scripts/utilidades/check_users.py
```

## ⚠️ Notas Importantes

1. **Entorno Virtual**: Asegúrate de tener el entorno virtual activado
2. **Servidor**: Para tests manuales, el servidor Django debe estar corriendo
3. **Base de Datos**: Algunos scripts requieren que la BD esté configurada
4. **Permisos**: Los scripts de utilidades pueden requerir permisos de admin

## 📋 Mantenimiento

- Revisa regularmente la funcionalidad de los scripts
- Actualiza las rutas si cambias la estructura del proyecto
- Documenta nuevos scripts que agregues
- Mantén las dependencias actualizadas
