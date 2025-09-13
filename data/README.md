# 📊 Carpeta de Datos

Esta carpeta contiene archivos de datos utilizados por el proyecto.

## 📋 Archivos Incluidos

### `seed_data.json`
- **Descripción**: Datos semilla para poblar la base de datos
- **Formato**: JSON estructurado
- **Uso**: Scripts de poblado de base de datos
- **Contenido**: Datos iniciales para tablas del sistema

### `login_data.json`
- **Descripción**: Datos de login para pruebas
- **Formato**: JSON con credenciales de usuario
- **Uso**: Scripts de testing manual
- **Contenido**: Credenciales de usuarios de prueba

## 🚀 Uso

Estos archivos son utilizados automáticamente por los scripts correspondientes:
- Scripts de poblado leen `seed_data.json`
- Scripts de testing leen `login_data.json`

## ⚠️ Seguridad

- **No subir a producción**: Estos archivos contienen datos de desarrollo
- **Credenciales**: Cambiar passwords en producción
- **Backup**: Mantener copias de seguridad si modificas los datos

## 📝 Formato de Archivos

Los archivos JSON deben mantener la estructura esperada por los scripts. Consulta la documentación específica de cada script antes de modificar.
