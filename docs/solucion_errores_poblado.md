# 🔧 Solución a Errores de Poblado - Smart Condominium

## 📅 Fecha: ${new Date().toLocaleDateString('es-ES')} - ${new Date().toLocaleTimeString('es-ES')}

---

## ⚠️ PROBLEMA IDENTIFICADO

El script de poblado original `poblar_db.py` falló con el siguiente error:

```
llave duplicada viola restricción de unicidad «uk_rol_nombre»
DETALLE: Ya existe la llave (nombre)=(Administrador).
```

**Causa:** El script intentaba insertar datos que ya existían en la base de datos, causando violaciones de restricciones UNIQUE.

---

## ✅ SOLUCIONES IMPLEMENTADAS

### 1. 📝 Script Mejorado: `poblar_db_mejorado.py`

**Características:**
- ✅ Manejo inteligente de duplicados con `ON CONFLICT DO NOTHING`
- ✅ Verificación del estado actual de la base de datos
- ✅ Menú interactivo con múltiples opciones
- ✅ Modo de limpieza segura (opcional)
- ✅ Reportes detallados de inserción
- ✅ Credenciales de administrador claramente mostradas

**Mejoras implementadas:**
```sql
-- Antes (ERROR):
INSERT INTO rol (nombre, descripcion) VALUES ('Administrador', '...');

-- Después (SEGURO):
INSERT INTO rol (nombre, descripcion) VALUES ('Administrador', '...')
ON CONFLICT (nombre) DO NOTHING;
```

### 2. 🎯 Comando Django Mejorado: `populate_safe.py`

**Ubicación:** `condominio/management/commands/populate_safe.py`

**Características:**
- ✅ Integrado con Django ORM
- ✅ Parámetros de línea de comandos (`--clear`, `--force`, `--check-only`)
- ✅ Manejo seguro de excepciones
- ✅ Reportes coloridos y detallados
- ✅ Verificación previa de datos existentes

---

## 🚀 MÉTODOS DE POBLADO DISPONIBLES

### Método 1: Script Standalone (Recomendado para desarrollo)
```powershell
python poblar_db_mejorado.py
```

**Opciones del menú interactivo:**
1. 📊 Ver estado actual de la base de datos
2. 🚀 Poblar base de datos (mantener datos existentes)
3. 🧹 Limpiar y poblar desde cero
4. 🔍 Solo limpiar tablas
5. ❌ Salir

### Método 2: Comando Django (Recomendado para producción)
```powershell
# Verificar estado actual
python manage.py populate_safe --check-only

# Poblar manteniendo datos existentes
python manage.py populate_safe

# Limpiar y poblar desde cero
python manage.py populate_safe --clear

# Forzar poblado sin preguntas
python manage.py populate_safe --force
```

---

## 📊 DATOS QUE SE POBLAN

### 👥 Roles (6 roles)
- Administrador
- Propietario  
- Inquilino
- Seguridad
- Conserje
- Mantenimiento

### 🔐 Usuarios (4-5 usuarios iniciales)
- **Admin Principal:** admin@smartcondominium.com / admin123
- **Propietarios:** Carlos Rodríguez, María González, Juan Pérez
- **Seguridad:** Jorge Flores

### 🏛️ Áreas Comunes (6 áreas)
- Salón de Eventos (100 personas, $50/hora)
- Piscina (30 personas, $20/hora)
- Gimnasio (15 personas, $10/hora)
- Cancha de Tenis (4 personas, $15/hora)
- Biblioteca (15 personas, GRATIS)
- Terraza (25 personas, $25/hora)

### 🚨 Tipos de Eventos (6 tipos)
- Acceso no autorizado (severidad alta)
- Vehículo no reconocido (severidad media)
- Actividad sospechosa (severidad media)
- Emergencia médica (severidad alta)
- Acceso autorizado (severidad baja)
- Visitante registrado (severidad baja)

---

## 🔑 CREDENCIALES DE ACCESO

### Usuario Administrador:
- **Email:** admin@smartcondominium.com
- **Password:** admin123
- **Tipo:** Administrador del sistema

### Usuarios de Prueba:
- **Carlos:** carlos.rodriguez@email.com / password123
- **María:** maria.gonzalez@email.com / password123
- **Juan:** juan.perez@email.com / password123
- **Jorge (Seguridad):** jorge.flores@email.com / password123

---

## 🛡️ CARACTERÍSTICAS DE SEGURIDAD

### 🔒 Encriptación de Contraseñas
- Uso de `crypt()` con `gen_salt('bf')` (bcrypt)
- Todas las contraseñas están hasheadas
- Salt único para cada contraseña

### 🚫 Manejo de Duplicados
```sql
-- Manejo inteligente de duplicados:
ON CONFLICT (email) DO NOTHING;      -- Para usuarios
ON CONFLICT (nombre) DO NOTHING;     -- Para roles, áreas, tipos
```

### 🔍 Verificaciones Previas
- Conteo de registros existentes antes de insertar
- Confirmación explícita para operaciones destructivas
- Reportes detallados de cada operación

---

## 📈 VENTAJAS DE LA SOLUCIÓN

### ✅ Idempotencia
- El script se puede ejecutar múltiples veces sin errores
- No duplica datos existentes
- Insertar solo datos faltantes

### ✅ Flexibilidad
- Múltiples modos de operación
- Opciones para limpiar o mantener datos
- Verificación de estado sin modificar datos

### ✅ Usabilidad
- Menús interactivos claros
- Mensajes informativos con emojis
- Credenciales claramente mostradas

### ✅ Robustez
- Manejo de excepciones
- Rollback automático en caso de errores críticos
- Verificación de conectividad antes de operar

---

## 🚀 PRÓXIMOS PASOS

1. **Testing:**
   - Ejecutar `python poblar_db_mejorado.py` 
   - Seleccionar opción 2 (poblar manteniendo datos)
   - Verificar que no hay errores

2. **Verificación:**
   - Usar opción 1 para ver el estado de la base
   - Conectarse con pgAdmin para validar datos
   - Probar login en Django admin con admin@smartcondominium.com

3. **Desarrollo API:**
   - Crear serializers para cada modelo
   - Implementar views y endpoints REST
   - Configurar permisos por rol

---

## 💡 NOTAS TÉCNICAS

### Orden de Inserción
1. `rol` (sin dependencias)
2. `usuario` (sin dependencias FK)
3. `usuario_rol` (depende de usuario y rol)
4. `area_comun` (sin dependencias)
5. `tipo_evento` (sin dependencias)

### Restricciones Manejadas
- `uk_rol_nombre`: UNIQUE en rol.nombre
- `uk_usuario_email`: UNIQUE en usuario.email  
- `uk_area_nombre`: UNIQUE en area_comun.nombre
- `uk_tipo_evento_nombre`: UNIQUE en tipo_evento.nombre

---

*Documento generado automáticamente tras resolver los errores de poblado*
