# Panel de Administración Personalizado

## Descripción

El panel de administración de Django ha sido personalizado para organizar los módulos en secciones temáticas que facilitan la navegación y gestión del sistema SmartCondominium.

## Secciones del Panel

### 🔧 Gestión de Mantenimiento
Esta sección incluye todos los modelos relacionados con el mantenimiento del condominio:

- **Solicitudes de Mantenimiento**: Gestión de solicitudes reportadas por residentes
- **Tareas de Mantenimiento**: Asignación y seguimiento de tareas de mantenimiento

### 📊 Reportes y Analíticas
Esta sección incluye todos los modelos relacionados con reportes y análisis de datos:

- **Reportes Financieros**: Análisis de ingresos, egresos y balances
- **Reportes de Seguridad**: Incidentes y eventos de seguridad
- **Reportes de Uso de Áreas**: Ocupación y uso de áreas comunes
- **Predicciones de Morosidad**: Análisis predictivo con IA

## Características del Panel Personalizado

### Navegación Organizada
- Los modelos están agrupados por funcionalidad
- Iconos visuales para identificar cada sección
- Nombres descriptivos en español

### Configuración de Modelos

#### Solicitudes de Mantenimiento
- **Campos principales**: Descripción, ubicación, prioridad, estado
- **Filtros**: Estado, prioridad, fecha, ubicación
- **Búsqueda**: Descripción, ubicación, usuario
- **Campos de solo lectura**: ID, fecha de solicitud

#### Tareas de Mantenimiento
- **Campos principales**: Solicitud relacionada, descripción, asignado a, estado
- **Filtros**: Estado, fechas, asignado a
- **Búsqueda**: Descripción, notas, asignado a
- **Enlaces**: Acceso directo a la solicitud relacionada

#### Reportes Financieros
- **Campos principales**: Título, tipo, período, formato
- **Filtros**: Tipo, período, formato, fecha, usuario
- **Búsqueda**: Título, descripción, usuario
- **Campos de solo lectura**: Datos del reporte, estadísticas

#### Reportes de Seguridad
- **Campos principales**: Título, tipo, período
- **Filtros**: Tipo, período, fecha, usuario
- **Búsqueda**: Título, descripción, usuario
- **Estadísticas**: Total eventos, eventos críticos, alertas

#### Reportes de Uso de Áreas
- **Campos principales**: Título, área, período, métrica principal
- **Filtros**: Área, período, métrica, fecha, usuario
- **Búsqueda**: Título, descripción, usuario
- **Estadísticas**: Total reservas, horas ocupación, tasa ocupación

#### Predicciones de Morosidad
- **Campos principales**: Título, modelo usado, nivel confianza
- **Filtros**: Modelo, confianza, fecha, usuario
- **Búsqueda**: Título, descripción, usuario
- **Estadísticas**: Residentes analizados, riesgos, precisión

## Personalización del Admin Site

### Configuración Personalizada
```python
class SmartCondominiumAdminSite(AdminSite):
    site_header = "Administración SmartCondominium"
    site_title = "SmartCondominium Admin"
    index_title = "Panel de Administración"
```

### Organización de Secciones
```python
def get_app_list(self, request):
    # Organiza aplicaciones en secciones temáticas
    # - Gestión de Mantenimiento
    # - Reportes y Analíticas
    # - Otras aplicaciones
```

## Acceso al Panel

### URL del Admin
- **URL principal**: `/admin/`
- **Login**: Credenciales de administrador del sistema

### Permisos de Acceso
- Solo usuarios con rol `admin` tienen acceso completo
- Los usuarios `staff` tienen acceso limitado según permisos
- Los residentes no tienen acceso al panel de administración

## Funcionalidades Avanzadas

### Enlaces Relacionados
- Las tareas de mantenimiento enlazan directamente a sus solicitudes
- Navegación intuitiva entre modelos relacionados

### Campos Calculados
- Porcentajes de riesgo en predicciones
- Estados visuales con colores
- Estadísticas automáticas

### Filtros y Búsqueda
- Filtros múltiples por fecha, estado, usuario
- Búsqueda en texto completo
- Ordenamiento personalizado

## Mantenimiento del Panel

### Actualización de Secciones
Para agregar nuevos modelos a las secciones:

1. Actualizar el diccionario `sections` en `admin_custom.py`
2. Registrar el modelo en el admin site correspondiente
3. Configurar los campos y opciones del ModelAdmin

### Personalización Visual
- Los iconos se pueden cambiar en la configuración de secciones
- Los colores y estilos se pueden personalizar con CSS
- Los nombres de sección se pueden traducir

## Documentación Relacionada

- [README Módulo Analytics](../docs/modulo8_analytics/README.md)
- [Permisos del Sistema](../docs/modulo8_analytics/permisos.md)
- [Guía de Testing](../docs/modulo8_analytics/testing.md)