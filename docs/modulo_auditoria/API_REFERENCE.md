# 🔗 **API REFERENCE - MÓDULO DE AUDITORÍA**

## 📋 **Índice de APIs**
- [Base URL](#base-url)
- [Autenticación](#autenticación)
- [Registros de Auditoría](#registros-de-auditoría)
- [Sesiones de Usuario](#sesiones-de-usuario)
- [Estadísticas](#estadísticas)
- [Códigos de Error](#códigos-de-error)
- [Ejemplos de Integración](#ejemplos-de-integración)

---

## 🌐 **Base URL**
```
http://127.0.0.1:8000/api/audit/
```

## 🔐 **Autenticación**
Todas las APIs requieren autenticación mediante token:

```http
Authorization: Token <tu_token_de_acceso>
```

**Obtener token**:
```http
POST /api/auth/login/
Content-Type: application/json

{
  "username": "tu_usuario",
  "password": "tu_contraseña"
}
```

---

## 📝 **Registros de Auditoría**

### **GET** `/api/audit/registros/`
**Descripción**: Obtiene lista paginada de registros de auditoría.

**Permisos**:
- Administradores: Ven todos los registros
- Usuarios normales: Solo sus propios registros

**Parámetros de consulta**:
| Parámetro | Tipo | Descripción | Ejemplo |
|-----------|------|-------------|---------|
| `page` | integer | Número de página | `?page=2` |
| `page_size` | integer | Registros por página (máx. 100) | `?page_size=50` |
| `usuario` | integer | ID del usuario (solo admin) | `?usuario=5` |
| `tipo_actividad` | string | Tipo de actividad | `?tipo_actividad=login` |
| `nivel_importancia` | string | Nivel de importancia | `?nivel_importancia=critico` |
| `es_exitoso` | boolean | Si fue exitosa | `?es_exitoso=true` |
| `fecha_inicio` | datetime | Desde fecha | `?fecha_inicio=2025-09-01T00:00:00Z` |
| `fecha_fin` | datetime | Hasta fecha | `?fecha_fin=2025-09-13T23:59:59Z` |
| `busqueda` | string | Buscar en descripción | `?busqueda=pago` |

**Respuesta exitosa (200)**:
```json
{
  "count": 45,
  "next": "http://127.0.0.1:8000/api/audit/registros/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "timestamp": "2025-09-13T10:30:15.123456Z",
      "usuario_info": {
        "id": 3,
        "username": "maria_garcia",
        "nombre_completo": "María García",
        "email": "maria@condominio.com"
      },
      "tipo_actividad": "pago",
      "tipo_actividad_display": "Procesamiento de pago",
      "descripcion": "Pago procesado exitosamente",
      "nivel_importancia": "alto",
      "nivel_importancia_display": "Alto",
      "nivel_color": "#fd7e14",
      "ip_address": "192.168.1.105",
      "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
      "es_exitoso": true,
      "mensaje_error": null,
      "objeto_afectado_str": "Cargo #15",
      "datos_adicionales": {
        "referencia_pago": "PAG-2025-001",
        "monto": "150000.00",
        "metodo": "transferencia"
      },
      "datos_anteriores": null,
      "datos_nuevos": {
        "estado": "pagado",
        "fecha_pago": "2025-09-13"
      }
    }
  ]
}
```

---

### **GET** `/api/audit/registros/resumen/`
**Descripción**: Obtiene resumen ejecutivo de actividades de auditoría.

**Permisos**: Solo administradores

**Respuesta exitosa (200)**:
```json
{
  "total_registros": 45,
  "registros_hoy": 12,
  "registros_semana": 32,
  "registros_mes": 45,
  "logins_exitosos_hoy": 8,
  "logins_fallidos_hoy": 2,
  "usuarios_activos_hoy": 4,
  "sesiones_activas": 2,
  "errores_criticos_hoy": 1,
  "actividades_por_tipo": {
    "login": 15,
    "logout": 12,
    "crear": 8,
    "pago": 4,
    "error_sistema": 3,
    "actualizar": 2,
    "acceso_denegado": 1
  },
  "usuarios_mas_activos": [
    {
      "usuario__id": 1,
      "usuario__username": "admin",
      "usuario__email": "admin@condominio.com",
      "count": 18
    },
    {
      "usuario__id": 3,
      "usuario__username": "maria_garcia",
      "usuario__email": "maria@condominio.com", 
      "count": 12
    }
  ],
  "ips_mas_frecuentes": [
    {
      "ip_address": "192.168.1.100",
      "count": 15
    },
    {
      "ip_address": "192.168.1.105",
      "count": 8
    }
  ]
}
```

---

### **GET** `/api/audit/registros/mis_actividades/`
**Descripción**: Obtiene solo las actividades del usuario autenticado.

**Permisos**: Todos los usuarios autenticados

**Parámetros**: Los mismos que `/registros/` excepto `usuario`

**Respuesta**: Igual que `/registros/` pero filtrada por usuario

---

### **GET** `/api/audit/registros/exportar/`
**Descripción**: Exporta registros de auditoría en formato JSON.

**Permisos**: Solo administradores

**Parámetros de consulta**: Los mismos filtros que `/registros/`

**Respuesta exitosa (200)**:
```json
{
  "fecha_exportacion": "2025-09-13T14:30:00Z",
  "total_registros": 25,
  "filtros_aplicados": {
    "fecha_inicio": "2025-09-01",
    "tipo_actividad": "pago"
  },
  "registros": [
    // Array completo de registros sin paginación
  ]
}
```

---

## 🔑 **Sesiones de Usuario**

### **GET** `/api/audit/sesiones/`
**Descripción**: Lista las sesiones de usuario.

**Permisos**:
- Administradores: Ven todas las sesiones
- Usuarios normales: Solo sus propias sesiones

**Parámetros de consulta**:
| Parámetro | Tipo | Descripción | Ejemplo |
|-----------|------|-------------|---------|
| `activas_solo` | boolean | Solo sesiones activas | `?activas_solo=true` |
| `usuario` | integer | ID del usuario (solo admin) | `?usuario=3` |
| `fecha_inicio` | datetime | Desde fecha | `?fecha_inicio=2025-09-01T00:00:00Z` |

**Respuesta exitosa (200)**:
```json
{
  "count": 14,
  "next": null,
  "previous": null,
  "results": [
    {
      "id": 1,
      "usuario_info": {
        "id": 3,
        "username": "maria_garcia",
        "nombre_completo": "María García"
      },
      "token_session": "a1b2c3d4e5f6...",
      "ip_address": "192.168.1.105",
      "user_agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 15_0 like Mac OS X)",
      "fecha_inicio": "2025-09-13T08:00:00Z",
      "fecha_ultimo_acceso": "2025-09-13T14:30:00Z",
      "esta_activa": true,
      "fecha_cierre": null,
      "duracion_sesion_str": "6 horas, 30 minutos"
    }
  ]
}
```

---

### **GET** `/api/audit/sesiones/mis_sesiones/`
**Descripción**: Obtiene solo las sesiones del usuario autenticado.

**Permisos**: Todos los usuarios autenticados

**Parámetros**: Los mismos que `/sesiones/` excepto `usuario`

**Respuesta**: Igual que `/sesiones/` pero filtrada por usuario

---

## 📊 **Estadísticas**

### **GET** `/api/audit/estadisticas/`
**Descripción**: Lista las estadísticas diarias del sistema.

**Permisos**: Solo administradores

**Parámetros de consulta**:
| Parámetro | Tipo | Descripción | Ejemplo |
|-----------|------|-------------|---------|
| `fecha_inicio` | date | Desde fecha | `?fecha_inicio=2025-09-01` |
| `fecha_fin` | date | Hasta fecha | `?fecha_fin=2025-09-13` |

**Respuesta exitosa (200)**:
```json
{
  "count": 12,
  "results": [
    {
      "id": 1,
      "fecha": "2025-09-13",
      "total_actividades": 25,
      "total_logins": 8,
      "total_usuarios_activos": 4,
      "actividades_criticas": 1,
      "errores_sistema": 0,
      "datos_estadisticas": {
        "actividades_por_hora": {
          "08": 3,
          "09": 5,
          "10": 7,
          "11": 4,
          "12": 2,
          "13": 3,
          "14": 1
        },
        "tipos_mas_frecuentes": {
          "login": 8,
          "pago": 6,
          "crear": 4
        },
        "dispositivos": {
          "desktop": 15,
          "mobile": 8,
          "tablet": 2
        }
      }
    }
  ]
}
```

---

### **GET** `/api/audit/estadisticas/tendencias/`
**Descripción**: Obtiene tendencias y métricas calculadas.

**Permisos**: Solo administradores

**Parámetros de consulta**:
| Parámetro | Tipo | Descripción | Ejemplo |
|-----------|------|-------------|---------|
| `periodo` | string | Período de análisis (7d, 30d, 90d) | `?periodo=30d` |

**Respuesta exitosa (200)**:
```json
{
  "periodo_analizado": "30d",
  "fecha_inicio": "2025-08-14",
  "fecha_fin": "2025-09-13",
  "metricas_generales": {
    "total_actividades": 450,
    "promedio_diario": 15.0,
    "pico_maximo": 35,
    "dia_pico": "2025-09-10"
  },
  "tendencias": {
    "actividades_crecimiento": 12.5,
    "usuarios_activos_crecimiento": 8.3,
    "errores_reduccion": -25.0
  },
  "patrones_horarios": {
    "hora_mas_activa": "10:00",
    "hora_menos_activa": "03:00",
    "actividad_promedio_por_hora": {
      "08": 5.2,
      "09": 8.7,
      "10": 12.3,
      "11": 9.8
    }
  },
  "analisis_usuarios": {
    "usuarios_mas_activos": [
      {
        "usuario": "admin",
        "actividades_totales": 85,
        "promedio_diario": 2.8
      }
    ],
    "nuevos_usuarios_periodo": 3,
    "usuarios_inactivos": 2
  }
}
```

---

## ⚠️ **Códigos de Error**

### **Errores de Autenticación**

```json
// 401 Unauthorized
{
  "detail": "Authentication credentials were not provided."
}

// 403 Forbidden
{
  "detail": "You do not have permission to perform this action."
}
```

### **Errores de Validación**

```json
// 400 Bad Request
{
  "error": "Filtro de fecha inválido",
  "details": {
    "fecha_inicio": "Formato de fecha requerido: YYYY-MM-DDTHH:MM:SSZ"
  }
}
```

### **Errores de Recursos**

```json
// 404 Not Found
{
  "detail": "No encontrado."
}

// 500 Internal Server Error
{
  "error": "Error interno del servidor",
  "message": "Error al procesar la solicitud de auditoría"
}
```

---

## 💻 **Ejemplos de Integración**

### **JavaScript/React - Dashboard de Auditoría**

```javascript
class AuditDashboard extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      resumen: {},
      registros: [],
      loading: true
    };
  }

  async componentDidMount() {
    await this.cargarDatos();
  }

  async cargarDatos() {
    try {
      const token = localStorage.getItem('authToken');
      const headers = {
        'Authorization': `Token ${token}`,
        'Content-Type': 'application/json'
      };

      // Cargar resumen
      const resumenResponse = await fetch(
        'http://127.0.0.1:8000/api/audit/registros/resumen/',
        { headers }
      );
      const resumen = await resumenResponse.json();

      // Cargar registros recientes
      const registrosResponse = await fetch(
        'http://127.0.0.1:8000/api/audit/registros/?page_size=10',
        { headers }
      );
      const registrosData = await registrosResponse.json();

      this.setState({
        resumen,
        registros: registrosData.results,
        loading: false
      });
    } catch (error) {
      console.error('Error al cargar datos de auditoría:', error);
      this.setState({ loading: false });
    }
  }

  render() {
    const { resumen, registros, loading } = this.state;

    if (loading) {
      return <div>Cargando dashboard...</div>;
    }

    return (
      <div className="audit-dashboard">
        <h2>Dashboard de Auditoría</h2>
        
        {/* Métricas principales */}
        <div className="metrics-grid">
          <div className="metric-card">
            <h3>Actividades Hoy</h3>
            <p className="metric-value">{resumen.registros_hoy}</p>
          </div>
          <div className="metric-card">
            <h3>Usuarios Activos</h3>
            <p className="metric-value">{resumen.usuarios_activos_hoy}</p>
          </div>
          <div className="metric-card">
            <h3>Errores Críticos</h3>
            <p className="metric-value error">{resumen.errores_criticos_hoy}</p>
          </div>
        </div>

        {/* Lista de actividades recientes */}
        <div className="recent-activities">
          <h3>Actividades Recientes</h3>
          <ul>
            {registros.map(registro => (
              <li key={registro.id} className={`activity-item ${registro.nivel_importancia}`}>
                <div className="activity-info">
                  <strong>{registro.usuario_info.nombre_completo}</strong>
                  <span className="activity-type">{registro.tipo_actividad_display}</span>
                </div>
                <div className="activity-details">
                  <p>{registro.descripcion}</p>
                  <small>{new Date(registro.timestamp).toLocaleString()}</small>
                </div>
              </li>
            ))}
          </ul>
        </div>
      </div>
    );
  }
}
```

### **Python - Cliente para Análisis**

```python
import requests
import json
from datetime import datetime, timedelta

class AuditAPIClient:
    def __init__(self, base_url, token):
        self.base_url = base_url.rstrip('/')
        self.headers = {
            'Authorization': f'Token {token}',
            'Content-Type': 'application/json'
        }
    
    def get_registros(self, **filtros):
        """Obtiene registros de auditoría con filtros"""
        url = f"{self.base_url}/api/audit/registros/"
        response = requests.get(url, headers=self.headers, params=filtros)
        response.raise_for_status()
        return response.json()
    
    def get_resumen(self):
        """Obtiene resumen de auditoría"""
        url = f"{self.base_url}/api/audit/registros/resumen/"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def exportar_registros(self, fecha_inicio=None, fecha_fin=None):
        """Exporta registros para análisis"""
        params = {}
        if fecha_inicio:
            params['fecha_inicio'] = fecha_inicio.isoformat()
        if fecha_fin:
            params['fecha_fin'] = fecha_fin.isoformat()
        
        url = f"{self.base_url}/api/audit/registros/exportar/"
        response = requests.get(url, headers=self.headers, params=params)
        response.raise_for_status()
        return response.json()
    
    def analizar_patrones_login(self, dias=7):
        """Analiza patrones de login de los últimos días"""
        fecha_inicio = datetime.now() - timedelta(days=dias)
        
        registros = self.get_registros(
            tipo_actividad='login',
            fecha_inicio=fecha_inicio.isoformat()
        )
        
        # Análisis de patrones
        usuarios_unicos = set()
        logins_por_hora = {}
        ips_frecuentes = {}
        
        for registro in registros['results']:
            usuarios_unicos.add(registro['usuario_info']['username'])
            
            # Análisis por hora
            timestamp = datetime.fromisoformat(registro['timestamp'].replace('Z', '+00:00'))
            hora = timestamp.hour
            logins_por_hora[hora] = logins_por_hora.get(hora, 0) + 1
            
            # IPs frecuentes
            ip = registro['ip_address']
            ips_frecuentes[ip] = ips_frecuentes.get(ip, 0) + 1
        
        return {
            'periodo_dias': dias,
            'total_logins': registros['count'],
            'usuarios_unicos': len(usuarios_unicos),
            'hora_pico': max(logins_por_hora, key=logins_por_hora.get),
            'ips_mas_frecuentes': sorted(ips_frecuentes.items(), key=lambda x: x[1], reverse=True)[:5]
        }

# Uso del cliente
client = AuditAPIClient('http://127.0.0.1:8000', 'tu_token_admin')

# Obtener resumen general
resumen = client.get_resumen()
print(f"Actividades hoy: {resumen['registros_hoy']}")
print(f"Usuarios activos: {resumen['usuarios_activos_hoy']}")

# Analizar patrones de login
patrones = client.analizar_patrones_login(dias=30)
print(f"Logins en 30 días: {patrones['total_logins']}")
print(f"Hora pico: {patrones['hora_pico']}:00")

# Exportar datos para análisis externo
fecha_inicio = datetime.now() - timedelta(days=30)
datos_exportados = client.exportar_registros(fecha_inicio=fecha_inicio)
print(f"Registros exportados: {datos_exportados['total_registros']}")
```

### **Flutter - Widget de Sesiones**

```dart
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class MisSesionesPage extends StatefulWidget {
  final String authToken;
  
  MisSesionesPage({required this.authToken});

  @override
  _MisSesionesPageState createState() => _MisSesionesPageState();
}

class _MisSesionesPageState extends State<MisSesionesPage> {
  List<dynamic> sesiones = [];
  bool loading = true;
  String? error;

  @override
  void initState() {
    super.initState();
    cargarSesiones();
  }

  Future<void> cargarSesiones() async {
    try {
      final response = await http.get(
        Uri.parse('http://127.0.0.1:8000/api/audit/sesiones/mis_sesiones/'),
        headers: {
          'Authorization': 'Token ${widget.authToken}',
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          sesiones = data;
          loading = false;
        });
      } else {
        throw Exception('Error ${response.statusCode}');
      }
    } catch (e) {
      setState(() {
        error = 'Error al cargar sesiones: $e';
        loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    if (loading) {
      return Scaffold(
        appBar: AppBar(title: Text('Mis Sesiones')),
        body: Center(child: CircularProgressIndicator()),
      );
    }

    if (error != null) {
      return Scaffold(
        appBar: AppBar(title: Text('Mis Sesiones')),
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.error, size: 64, color: Colors.red),
              SizedBox(height: 16),
              Text(error!, textAlign: TextAlign.center),
              SizedBox(height: 16),
              ElevatedButton(
                onPressed: () {
                  setState(() {
                    loading = true;
                    error = null;
                  });
                  cargarSesiones();
                },
                child: Text('Reintentar'),
              ),
            ],
          ),
        ),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: Text('Mis Sesiones'),
        actions: [
          IconButton(
            icon: Icon(Icons.refresh),
            onPressed: () {
              setState(() => loading = true);
              cargarSesiones();
            },
          ),
        ],
      ),
      body: ListView.builder(
        itemCount: sesiones.length,
        itemBuilder: (context, index) {
          final sesion = sesiones[index];
          final esActiva = sesion['esta_activa'];
          
          return Card(
            margin: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            child: ListTile(
              leading: Icon(
                esActiva ? Icons.radio_button_checked : Icons.radio_button_unchecked,
                color: esActiva ? Colors.green : Colors.grey,
              ),
              title: Text('IP: ${sesion['ip_address']}'),
              subtitle: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Duración: ${sesion['duracion_sesion_str']}'),
                  Text(
                    'Inicio: ${_formatDateTime(sesion['fecha_inicio'])}',
                    style: TextStyle(fontSize: 12),
                  ),
                  if (!esActiva && sesion['fecha_cierre'] != null)
                    Text(
                      'Cierre: ${_formatDateTime(sesion['fecha_cierre'])}',
                      style: TextStyle(fontSize: 12),
                    ),
                ],
              ),
              trailing: Chip(
                label: Text(esActiva ? 'Activa' : 'Cerrada'),
                backgroundColor: esActiva ? Colors.green.shade100 : Colors.grey.shade200,
              ),
              onTap: () => _mostrarDetallesSesion(sesion),
            ),
          );
        },
      ),
    );
  }

  String _formatDateTime(String dateTimeStr) {
    final dateTime = DateTime.parse(dateTimeStr);
    return '${dateTime.day}/${dateTime.month}/${dateTime.year} ${dateTime.hour}:${dateTime.minute.toString().padLeft(2, '0')}';
  }

  void _mostrarDetallesSesion(dynamic sesion) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('Detalles de Sesión'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildDetailRow('IP:', sesion['ip_address']),
            _buildDetailRow('Estado:', sesion['esta_activa'] ? 'Activa' : 'Cerrada'),
            _buildDetailRow('Duración:', sesion['duracion_sesion_str']),
            _buildDetailRow('Inicio:', _formatDateTime(sesion['fecha_inicio'])),
            if (sesion['fecha_cierre'] != null)
              _buildDetailRow('Cierre:', _formatDateTime(sesion['fecha_cierre'])),
            SizedBox(height: 8),
            Text('Navegador:', style: TextStyle(fontWeight: FontWeight.bold)),
            Text(sesion['user_agent'], style: TextStyle(fontSize: 11)),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.of(context).pop(),
            child: Text('Cerrar'),
          ),
        ],
      ),
    );
  }

  Widget _buildDetailRow(String label, String value) {
    return Padding(
      padding: EdgeInsets.only(bottom: 4),
      child: Row(
        children: [
          Text(label, style: TextStyle(fontWeight: FontWeight.bold)),
          SizedBox(width: 8),
          Expanded(child: Text(value)),
        ],
      ),
    );
  }
}
```

---

## 🔄 **Versionado de API**

**Versión actual**: `v1`

**URLs versionadas**:
- `/api/audit/v1/registros/`
- `/api/audit/v1/sesiones/`
- `/api/audit/v1/estadisticas/`

---

## 📈 **Límites y Cuotas**

| Endpoint | Límite por minuto | Límite de página |
|----------|-------------------|------------------|
| `/registros/` | 60 requests | 100 registros |
| `/resumen/` | 10 requests | N/A |
| `/exportar/` | 5 requests | 1000 registros |
| `/sesiones/` | 30 requests | 50 sesiones |

---

**📅 Fecha de referencia**: 13 de septiembre de 2025  
**🔄 Versión de API**: 1.0.0  
**📧 Soporte técnico**: Disponible en documentación del módulo