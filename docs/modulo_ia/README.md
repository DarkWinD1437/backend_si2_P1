# Módulo de Seguridad con IA

Este módulo implementa funcionalidades avanzadas de seguridad para el condominio SmartCondominium utilizando **Grok Vision API via OpenRouter** para procesamiento real de imágenes con inteligencia artificial.

## ⚠️ Configuración Requerida

### API Key de Grok via OpenRouter
Para que las funcionalidades de IA funcionen correctamente, necesitas configurar tu API key de OpenRouter para Grok:

1. **Obtén tu API key** desde [OpenRouter](https://openrouter.ai/keys)
2. **Agrega al archivo `.env`**:
   ```bash
   GROK_API_KEY=sk-or-v1-your-openrouter-api-key-here
   ```
3. **Reinicia el servidor** para que tome la nueva configuración

### Sin API Key
Si no configuras la API key, el módulo funcionará en **modo simulado** con datos de ejemplo.

## Características

### 1. Registro y Reconocimiento Facial
- **Registro de rostros**: Permite a los residentes registrar sus rostros usando OpenAI Vision API
- **Reconocimiento facial**: Sistema de IA que identifica rostros en tiempo real usando embeddings faciales
- **Similitud coseno**: Algoritmo avanzado para comparar rostros con precisión
- **Confianza configurable**: Nivel mínimo de confianza ajustable para validación

### 2. Registro y Lectura de Placas Vehiculares
- **Registro de vehículos**: Gestión de vehículos autorizados con formato de placa boliviano
- **Lectura automática**: OCR con OpenAI Vision API para reconocimiento de texto en placas
- **Formato boliviano**: Soporte para placas en formato `123ABC` o `1234ABC`

### 3. Historial de Accesos
- **Registro completo**: Historial detallado de todos los intentos de acceso
- **Filtros avanzados**: Búsqueda por tipo, estado, fecha y ubicación
- **Auditoría**: Seguimiento completo de accesos permitidos y denegados

## Endpoints API

### Rostros Registrados
```
GET    /api/security/rostros/           # Listar rostros del usuario
POST   /api/security/rostros/           # Registrar nuevo rostro
GET    /api/security/rostros/{id}/      # Detalle de rostro
PUT    /api/security/rostros/{id}/      # Actualizar rostro
DELETE /api/security/rostros/{id}/      # Eliminar rostro
POST   /api/security/rostros/registrar_con_ia/  # Registro con IA
```

### Vehículos Registrados
```
GET    /api/security/vehiculos/         # Listar vehículos del usuario
POST   /api/security/vehiculos/         # Registrar nuevo vehículo
GET    /api/security/vehiculos/{id}/    # Detalle de vehículo
PUT    /api/security/vehiculos/{id}/    # Actualizar vehículo
DELETE /api/security/vehiculos/{id}/    # Eliminar vehículo
```

### Historial de Accesos
```
GET    /api/security/accesos/           # Listar historial de accesos
```

### Funcionalidades de IA
```
POST   /api/security/reconocimiento-facial/    # Reconocimiento facial en tiempo real
POST   /api/security/lectura-placa/           # Lectura automática de placas
```

## Modelos de Datos

### RostroRegistrado
- `usuario`: Usuario propietario del rostro
- `nombre_identificador`: Nombre descriptivo
- `imagen_rostro`: Imagen para reconocimiento
- `embedding_ia`: Vector de características extraído por IA
- `confianza_minima`: Umbral de confianza para validación
- `activo`: Estado del registro

### VehiculoRegistrado
- `usuario`: Usuario propietario del vehículo
- `placa`: Placa en formato boliviano (ej: 1234ABC)
- `marca`, `modelo`, `color`: Información del vehículo
- `activo`: Estado del registro

### Acceso
- `usuario`: Usuario que intentó acceder
- `tipo_acceso`: facial, placa, manual, codigo
- `estado`: permitido, denegado, pendiente
- `ubicacion`: Punto de acceso
- `confianza_ia`: Nivel de confianza de la IA
- `fecha_hora`: Timestamp del acceso

## Integración con Grok via OpenRouter

El módulo utiliza **Grok 4 Fast Vision API via OpenRouter** para procesamiento real de imágenes:

### Reconocimiento Facial
- **Modelo**: `x-ai/grok-4-fast:free`
- **Función**: Extrae embeddings faciales de 512 dimensiones
- **Similitud**: Calcula similitud coseno entre rostros
- **Precisión**: Basado en análisis de rasgos faciales únicos

### Lectura de Placas (OCR)
- **Modelo**: `x-ai/grok-4-fast:free`
- **Función**: Reconoce texto en imágenes de placas vehiculares
- **Formato**: Especialmente entrenado para formato boliviano
- **Validación**: Verifica formato `###ABC` o `####ABC`

### Configuración
Asegúrate de tener configurada la variable de entorno `GROK_API_KEY` en tu archivo `.env`.

### Modo Simulado
Si no hay API key configurada, el sistema funciona con datos simulados para desarrollo.

## Uso desde Frontend

### React/Flutter Integration

#### Registro Facial
```javascript
// Enviar imagen base64 para registro
const response = await fetch('/api/security/rostros/registrar_con_ia/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    imagen_base64: 'data:image/jpeg;base64,...',
    nombre_identificador: 'Mi rostro principal',
    confianza_minima: 0.85
  })
});
```

#### Reconocimiento Facial
```javascript
// Verificar acceso facial
const response = await fetch('/api/security/reconocimiento-facial/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    imagen_base64: 'data:image/jpeg;base64,...',
    ubicacion: 'Puerta Principal'
  })
});
```

#### Lectura de Placa
```javascript
// Procesar imagen de placa
const response = await fetch('/api/security/lectura-placa/', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    imagen_base64: 'data:image/jpeg;base64,...',
    ubicacion: 'Entrada Vehicular'
  })
});
```

## Validaciones

### Formato de Placas
- **Boliviano**: `^\d{3,4}[A-Z]{3}$`
- Ejemplos válidos: `123ABC`, `1234ABC`
- Longitud máxima: 7 caracteres

### Confianza IA
- Rango: 0.0 a 1.0
- Recomendado: 0.85 para rostros, 0.95 para placas

## Pruebas

### Ejecutar Tests
```bash
# Tests específicos del módulo
python manage.py test backend.apps.modulo_ia

# Tests con coverage
coverage run --source=backend.apps.modulo_ia manage.py test
coverage report
```

### Casos de Prueba
1. **Registro facial exitoso**
2. **Reconocimiento facial válido**
3. **Acceso denegado por baja confianza**
4. **Registro de placa válido**
5. **Lectura automática de placa**
6. **Consulta de historial filtrada**

## Seguridad

- **Autenticación requerida**: Todos los endpoints requieren token JWT
- **Permisos de usuario**: Solo acceso a datos propios
- **Validación de entrada**: Sanitización de datos y validaciones estrictas
- **Auditoría completa**: Registro de todas las operaciones

## Próximas Mejoras

- [ ] Integración con cámaras IP en tiempo real
- [ ] Modelo de IA personalizado entrenado con datos locales
- [ ] Notificaciones push para accesos denegados
- [ ] Dashboard de analytics de seguridad
- [ ] Integración con sistemas de alarma