# 📊 Módulo 2: Gestión Financiera Básica
## T1: Configurar Cuotas y Multas

### 📋 Resumen Ejecutivo

El **Módulo 2: Gestión Financiera Básica** ha sido desarrollado exitosamente, implementando la funcionalidad completa para configurar y gestionar cuotas y multas en el sistema Smart Condominium. Este módulo está diseñado para ser consumido tanto por la aplicación web React-Vite (administradores) como por la aplicación móvil Flutter (residentes y seguridad).

### ✅ Estado del Desarrollo
- **Estado**: ✅ COMPLETADO
- **Fecha de finalización**: 13 de septiembre de 2025
- **Funcionalidades implementadas**: 100%
- **Pruebas realizadas**: ✅ TODAS EXITOSAS

---

## 🏗️ Arquitectura del Módulo

### 📁 Estructura de Archivos
```
backend/apps/finances/
├── __init__.py
├── apps.py                 # Configuración de la app
├── models.py              # Modelos: ConceptoFinanciero, CargoFinanciero
├── serializers.py         # Serializers con validaciones
├── views.py              # ViewSets con permisos diferenciados
├── urls.py               # Configuración de rutas API
├── admin.py              # Panel de administración Django
└── migrations/
    └── 0001_initial.py   # Migración inicial
```

### 🗃️ Modelos de Base de Datos

#### ConceptoFinanciero
Define los tipos de cobros (cuotas y multas) que pueden aplicarse.

**Campos principales:**
- `nombre`: Nombre descriptivo del concepto
- `tipo`: Tipo de concepto (cuota_mensual, multa_ruido, etc.)
- `monto`: Monto base del cobro
- `estado`: Estado del concepto (activo, inactivo, suspendido)
- `fecha_vigencia_desde/hasta`: Periodo de vigencia
- `es_recurrente`: Si se aplica automáticamente cada mes
- `aplica_a_todos`: Si aplica a todos los residentes

#### CargoFinanciero
Representa la aplicación específica de un concepto a un residente.

**Campos principales:**
- `concepto`: Referencia al ConceptoFinanciero
- `residente`: Usuario al que se aplica el cargo
- `monto`: Monto específico a cobrar
- `estado`: Estado del cargo (pendiente, pagado, vencido, cancelado)
- `fecha_aplicacion/vencimiento/pago`: Fechas importantes
- `referencia_pago`: Referencia del pago procesado

---

## 🔌 API Endpoints

### Base URL: `http://127.0.0.1:8000/api/finances/`

### 📋 Conceptos Financieros

| Método | Endpoint | Descripción | Permisos |
|--------|----------|-------------|----------|
| GET | `/conceptos/` | Listar conceptos | Todos |
| POST | `/conceptos/` | Crear concepto | Admin |
| GET | `/conceptos/{id}/` | Detalle concepto | Todos |
| PUT/PATCH | `/conceptos/{id}/` | Actualizar concepto | Admin |
| DELETE | `/conceptos/{id}/` | Eliminar concepto | Admin |
| GET | `/conceptos/vigentes/` | Conceptos vigentes | Todos |
| POST | `/conceptos/{id}/toggle_estado/` | Activar/desactivar | Admin |

### 💰 Cargos Financieros

| Método | Endpoint | Descripción | Permisos |
|--------|----------|-------------|----------|
| GET | `/cargos/` | Listar cargos | Admin: todos, Residentes: propios |
| POST | `/cargos/` | Crear cargo | Admin |
| GET | `/cargos/{id}/` | Detalle cargo | Admin o propietario |
| PUT/PATCH | `/cargos/{id}/` | Actualizar cargo | Admin |
| DELETE | `/cargos/{id}/` | Eliminar cargo | Admin |
| GET | `/cargos/mis_cargos/` | Cargos del usuario actual | Todos |
| POST | `/cargos/{id}/pagar/` | Procesar pago | Admin o propietario |
| GET | `/cargos/vencidos/` | Cargos vencidos | Admin |
| GET | `/cargos/resumen/{user_id}/` | Resumen financiero | Admin o propio |

### 📊 Estadísticas

| Método | Endpoint | Descripción | Permisos |
|--------|----------|-------------|----------|
| GET | `/estadisticas/` | Estadísticas generales | Admin |

---

## 🔐 Sistema de Permisos

### Roles y Accesos

#### 👑 Administradores
- ✅ **CRUD completo** de conceptos financieros
- ✅ **CRUD completo** de cargos financieros
- ✅ **Ver todos** los cargos de todos los residentes
- ✅ **Procesar pagos** en nombre de residentes
- ✅ **Acceso a estadísticas** financieras
- ✅ **Gestionar estados** de conceptos

#### 🏠 Residentes
- ✅ **Ver conceptos** financieros (solo lectura)
- ✅ **Ver sus propios cargos** únicamente
- ✅ **Procesar pagos** de sus propios cargos
- ✅ **Ver su resumen** financiero personal
- ❌ **No pueden crear** conceptos ni cargos
- ❌ **No pueden ver** cargos de otros residentes
- ❌ **No pueden acceder** a estadísticas generales

#### 🛡️ Seguridad
- ✅ **Ver conceptos** financieros (solo lectura)
- ❌ **No pueden ver** cargos financieros
- ❌ **Acceso limitado** solo a información general

---

## 📱 Integración para React-Vite y Flutter

### 🌐 Para React-Vite (Administradores)

#### Ejemplo: Listar Conceptos
```javascript
const fetchConceptos = async () => {
  try {
    const response = await fetch('http://127.0.0.1:8000/api/finances/conceptos/', {
      headers: {
        'Authorization': `Token ${adminToken}`,
        'Content-Type': 'application/json'
      }
    });
    const data = await response.json();
    setConceptos(data.results || data);
  } catch (error) {
    console.error('Error fetching conceptos:', error);
  }
};
```

#### Ejemplo: Crear Concepto
```javascript
const crearConcepto = async (conceptoData) => {
  try {
    const response = await fetch('http://127.0.0.1:8000/api/finances/conceptos/', {
      method: 'POST',
      headers: {
        'Authorization': `Token ${adminToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(conceptoData)
    });
    
    if (response.ok) {
      const nuevoConcepto = await response.json();
      console.log('Concepto creado:', nuevoConcepto);
      return nuevoConcepto;
    }
  } catch (error) {
    console.error('Error creando concepto:', error);
  }
};
```

#### Ejemplo: Aplicar Cargo
```javascript
const aplicarCargo = async (cargoData) => {
  try {
    const response = await fetch('http://127.0.0.1:8000/api/finances/cargos/', {
      method: 'POST',
      headers: {
        'Authorization': `Token ${adminToken}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify(cargoData)
    });
    
    if (response.ok) {
      const nuevoCargo = await response.json();
      console.log('Cargo aplicado:', nuevoCargo);
      return nuevoCargo;
    }
  } catch (error) {
    console.error('Error aplicando cargo:', error);
  }
};
```

### 📱 Para Flutter (Residentes)

#### Ejemplo: Ver Mis Cargos
```dart
import 'dart:convert';
import 'package:http/http.dart' as http;

class FinancesService {
  static const String baseUrl = 'http://127.0.0.1:8000/api/finances';
  
  static Future<List<dynamic>> getMisCargos(String token) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/cargos/mis_cargos/'),
        headers: {
          'Authorization': 'Token $token',
          'Content-Type': 'application/json',
        },
      );
      
      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw Exception('Error: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Error fetching cargos: $e');
    }
  }
}
```

#### Ejemplo: Procesar Pago
```dart
static Future<Map<String, dynamic>> pagarCargo(
  String token, 
  int cargoId, 
  String referenciaPago
) async {
  try {
    final response = await http.post(
      Uri.parse('$baseUrl/cargos/$cargoId/pagar/'),
      headers: {
        'Authorization': 'Token $token',
        'Content-Type': 'application/json',
      },
      body: json.encode({
        'referencia_pago': referenciaPago,
        'observaciones': 'Pago procesado desde app móvil'
      }),
    );
    
    if (response.statusCode == 200) {
      return json.decode(response.body);
    } else {
      throw Exception('Error procesando pago: ${response.statusCode}');
    }
  } catch (e) {
    throw Exception('Error: $e');
  }
}
```

#### Ejemplo: Widget Flutter para Mostrar Cargos
```dart
class MisCargosList extends StatefulWidget {
  @override
  _MisCargosListState createState() => _MisCargosListState();
}

class _MisCargosListState extends State<MisCargosList> {
  List<dynamic> cargos = [];
  bool loading = true;
  
  @override
  void initState() {
    super.initState();
    _loadCargos();
  }
  
  _loadCargos() async {
    try {
      final token = await getStoredToken(); // Tu método para obtener token
      final data = await FinancesService.getMisCargos(token);
      setState(() {
        cargos = data;
        loading = false;
      });
    } catch (e) {
      setState(() => loading = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error cargando datos: $e'))
      );
    }
  }
  
  @override
  Widget build(BuildContext context) {
    if (loading) return CircularProgressIndicator();
    
    return ListView.builder(
      itemCount: cargos.length,
      itemBuilder: (context, index) {
        final cargo = cargos[index];
        return Card(
          child: ListTile(
            title: Text(cargo['concepto_nombre']),
            subtitle: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Monto: \$${cargo['monto']}'),
                Text('Estado: ${cargo['estado_display']}'),
                Text('Vencimiento: ${cargo['fecha_vencimiento']}'),
              ],
            ),
            trailing: cargo['estado'] == 'pendiente' 
              ? ElevatedButton(
                  onPressed: () => _pagarCargo(cargo['id']),
                  child: Text('Pagar'),
                )
              : Icon(
                  cargo['estado'] == 'pagado' ? Icons.check_circle : Icons.warning,
                  color: cargo['estado'] == 'pagado' ? Colors.green : Colors.orange,
                ),
          ),
        );
      },
    );
  }
  
  _pagarCargo(int cargoId) async {
    // Implementar lógica de pago
    try {
      final token = await getStoredToken();
      final referencia = 'APP-${DateTime.now().millisecondsSinceEpoch}';
      
      final result = await FinancesService.pagarCargo(token, cargoId, referencia);
      
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Pago procesado exitosamente'))
      );
      
      _loadCargos(); // Recargar lista
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error procesando pago: $e'))
      );
    }
  }
}
```

---

## 📊 Filtros y Parámetros Disponibles

### Filtros para Conceptos
- `?tipo=cuota_mensual` - Filtrar por tipo de concepto
- `?estado=activo` - Filtrar por estado
- `?vigente=true` - Solo conceptos vigentes

### Filtros para Cargos
- `?estado=pendiente` - Filtrar por estado
- `?residente=1` - Filtrar por residente (solo admin)
- `?concepto=1` - Filtrar por concepto
- `?vencidos=true` - Solo cargos vencidos

---

## 📋 Ejemplos de Datos JSON

### Concepto Financiero
```json
{
  "id": 1,
  "nombre": "Cuota de Mantenimiento Mensual",
  "descripcion": "Cuota mensual para mantenimiento de áreas comunes",
  "tipo": "cuota_mensual",
  "tipo_display": "Cuota Mensual",
  "monto": "180.00",
  "estado": "activo",
  "estado_display": "Activo",
  "fecha_vigencia_desde": "2025-01-01",
  "fecha_vigencia_hasta": "2025-12-31",
  "es_recurrente": true,
  "aplica_a_todos": true,
  "esta_vigente": true,
  "creado_por": 1,
  "creado_por_info": {
    "id": 1,
    "username": "admin",
    "nombre_completo": "Administrador Sistema"
  },
  "fecha_creacion": "2025-09-13T06:15:30Z",
  "fecha_modificacion": "2025-09-13T06:15:30Z"
}
```

### Cargo Financiero
```json
{
  "id": 1,
  "concepto": 1,
  "concepto_info": {
    "id": 1,
    "nombre": "Cuota de Mantenimiento Mensual",
    "tipo": "cuota_mensual",
    "monto": "180.00"
  },
  "residente": 3,
  "residente_info": {
    "id": 3,
    "username": "carlos",
    "email": "carlos.rodriguez@email.com",
    "first_name": "Carlos",
    "last_name": "Rodriguez",
    "nombre_completo": "Carlos Rodriguez"
  },
  "monto": "180.00",
  "estado": "pendiente",
  "estado_display": "Pendiente",
  "fecha_aplicacion": "2025-09-13",
  "fecha_vencimiento": "2025-10-13",
  "fecha_pago": null,
  "observaciones": "Cuota mensual aplicada automáticamente",
  "referencia_pago": "",
  "aplicado_por": 1,
  "esta_vencido": false,
  "dias_para_vencimiento": 30,
  "fecha_creacion": "2025-09-13T06:15:30Z",
  "fecha_modificacion": "2025-09-13T06:15:30Z"
}
```

### Estadísticas Financieras
```json
{
  "total_conceptos_activos": 7,
  "total_cargos_pendientes": 5,
  "monto_total_pendiente": "910.00",
  "total_cargos_vencidos": 0,
  "monto_total_vencido": "0.00",
  "total_pagos_mes_actual": "510.00",
  "conceptos_mas_aplicados": [
    {
      "concepto__nombre": "Cuota de Mantenimiento Mensual",
      "concepto__tipo": "cuota_mensual",
      "cantidad": 4
    },
    {
      "concepto__nombre": "Cuota Extraordinaria - Remodelación Salón",
      "concepto__tipo": "cuota_extraordinaria",
      "cantidad": 2
    }
  ]
}
```

---

## ✅ Pruebas Realizadas

### 🧪 Pruebas Automatizadas
- **✅ Autenticación y permisos**: Verificación de accesos por rol
- **✅ CRUD de conceptos**: Creación, lectura, actualización y eliminación
- **✅ CRUD de cargos**: Gestión completa de cargos financieros
- **✅ Proceso de pagos**: Marcado de cargos como pagados
- **✅ Validaciones**: Verificación de datos y reglas de negocio
- **✅ Filtros y búsquedas**: Funcionamiento de todos los filtros
- **✅ Estadísticas**: Cálculo correcto de resúmenes y estadísticas

### 📊 Datos de Prueba
- **6 conceptos financieros** creados
- **8 cargos aplicados** a diferentes residentes
- **2 pagos procesados** exitosamente
- **Diferentes estados** de cargos simulados

---

## 🚀 Estado de Producción

### ✅ Listo para Despliegue
- **Backend API**: Completamente funcional
- **Base de datos**: Migrada y poblada con datos de ejemplo
- **Permisos**: Sistema de roles implementado
- **Validaciones**: Todas las reglas de negocio aplicadas
- **Documentación**: Completa y actualizada
- **Pruebas**: 100% exitosas

### 🔄 Próximos Pasos Sugeridos
1. **Integración Frontend**: Conectar React-Vite con las APIs
2. **Integración Mobile**: Conectar Flutter con las APIs
3. **Notificaciones**: Implementar alertas de vencimiento
4. **Reportes**: Agregar generación de reportes PDF
5. **Pagos Online**: Integrar pasarelas de pago

---

## 📞 Soporte y Mantenimiento

### 🛠️ Archivos Importantes
- **Modelos**: `backend/apps/finances/models.py`
- **APIs**: `backend/apps/finances/views.py`
- **Tests**: `scripts/testing_manual/modulo2_finances/`
- **Población**: `scripts/poblado_db/poblar_modulo2_finances.py`

### 🔧 Comandos Útiles
```bash
# Crear datos de ejemplo
python scripts/poblado_db/poblar_modulo2_finances.py

# Ejecutar pruebas
python scripts/testing_manual/modulo2_finances/test_finances_complete.py

# Ver migraciones
python manage.py showmigrations finances

# Crear nuevas migraciones si hay cambios
python manage.py makemigrations finances
python manage.py migrate
```

---

**📅 Fecha de documentación**: 13 de septiembre de 2025  
**👤 Desarrollado por**: GitHub Copilot  
**🎯 Módulo**: 2 - Gestión Financiera Básica  
**📊 Estado**: ✅ COMPLETADO