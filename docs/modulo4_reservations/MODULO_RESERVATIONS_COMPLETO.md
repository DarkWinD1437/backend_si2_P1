# 📋 MÓDULO 4: RESERVAS DE ÁREAS COMUNES
## Documentación Completa

### 🎯 **Descripción General**
El Módulo de Reservas de Áreas Comunes permite a los residentes del condominio reservar espacios compartidos como gimnasios, piscinas, canchas deportivas, salones de eventos, etc. Incluye funcionalidades completas de consulta de disponibilidad, reserva, confirmación con pago y cancelación.

### 🏗️ **Arquitectura del Sistema**

#### **Componentes Principales**
- **Modelos**: `AreaComun`, `HorarioDisponible`, `Reserva`
- **APIs REST**: Endpoints para gestión completa de reservas
- **Permisos**: Control de acceso basado en roles (Admin, Residente, Seguridad)
- **Validaciones**: Reglas de negocio integradas
- **Integración**: Preparado para conectar con módulos financiero y de auditoría

#### **Estados de Reserva**
- `PENDIENTE`: Reserva creada, esperando confirmación
- `CONFIRMADA`: Reserva confirmada por administrador
- `PAGADA`: Reserva pagada y confirmada
- `CANCELADA`: Reserva cancelada
- `USADA`: Reserva completada

### 📋 **Funcionalidades Principales**

#### **T1: Consultar Disponibilidad**
- Visualización de áreas comunes disponibles
- Consulta de horarios disponibles por fecha
- Generación automática de slots de tiempo (30 min)
- Verificación de conflictos con reservas existentes

#### **T2: Reservar Área Común**
- Creación de reservas con validaciones
- Control de capacidad máxima
- Cálculo automático de costos
- Verificación de anticipación mínima

#### **T3: Confirmar Reserva con Pago**
- Confirmación de reservas pendientes
- Integración con sistema de pagos
- Cambio de estado automático

#### **T4: Cancelar Reserva**
- Cancelación con motivos
- Validación de permisos
- Prevención de cancelaciones inválidas

### 🔐 **Permisos y Roles**

| Rol | Listar Áreas | Ver Disponibilidad | Reservar | Confirmar | Cancelar |
|-----|-------------|-------------------|----------|-----------|----------|
| **Admin** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **Residente** | ✅ | ✅ | ✅ | ❌ | ✅ (propias) |
| **Seguridad** | ✅ | ✅ | ❌ | ❌ | ❌ |

### 💰 **Sistema de Costos**

#### **Estructura de Costos**
- **Costo por Hora**: Tarifa base por hora de uso
- **Costo Fijo**: Cargo adicional por reserva
- **Cálculo Total**: `(horas × costo_hora) + costo_fijo`

#### **Ejemplo de Cálculo**
```
Área: Gimnasio
- Costo por hora: $5.000
- Costo fijo: $2.000
- Reserva: 2 horas
- Total: (2 × $5.000) + $2.000 = $12.000
```

### ⏰ **Reglas de Negocio**

#### **Anticipación Mínima**
- Reservas requieren mínimo 24 horas de anticipación
- Configurable por área común

#### **Duración de Reservas**
- Mínimo: 30 minutos
- Máximo: Configurable por área (ej: 4 horas)
- Intervalos: 30 minutos

#### **Capacidad**
- Control de personas por reserva
- No superar capacidad máxima del área

### 🔧 **Configuración Técnica**

#### **Dependencias**
```python
# settings.py - INSTALLED_APPS
INSTALLED_APPS = [
    # ... otras apps
    'backend.apps.reservations',
    'rest_framework',
    'rest_framework.authtoken',
]
```

#### **URLs**
```python
# backend/urls.py
urlpatterns = [
    # ... otras rutas
    path('api/reservations/', include('backend.apps.reservations.urls')),
]
```

### 📊 **Base de Datos**

#### **Tablas Principales**
- `reservations_areacomun`: Áreas comunes disponibles
- `reservations_horariodisponible`: Horarios por día de semana
- `reservations_reserva`: Reservas realizadas

#### **Relaciones**
- AreaComun → HorarioDisponible (1:N)
- AreaComun → Reserva (1:N)
- User → Reserva (1:N)

### 🚀 **Guía de Inicio Rápido**

#### **1. Verificar Datos Iniciales**
```bash
# Verificar áreas comunes
python manage.py shell
>>> from backend.apps.reservations.models import AreaComun
>>> AreaComun.objects.all().count()
5

# Verificar horarios
>>> from backend.apps.reservations.models import HorarioDisponible
>>> HorarioDisponible.objects.all().count()
7  # Uno por día de semana
```

#### **2. Probar API Básica**
```bash
# Listar áreas comunes
curl -H "Authorization: Token <token>" \
     http://localhost:8000/api/reservations/areas/

# Consultar disponibilidad
curl -H "Authorization: Token <token>" \
     "http://localhost:8000/api/reservations/areas/1/disponibilidad/?fecha=2025-09-25"
```

### 📱 **Integración con Frontends**

#### **React - Hooks Personalizados**
```javascript
// hooks/useReservations.js
import { useState, useEffect } from 'react';

export const useReservations = () => {
  const [areas, setAreas] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchAreas();
  }, []);

  const fetchAreas = async () => {
    try {
      const response = await fetch('/api/reservations/areas/', {
        headers: {
          'Authorization': `Token ${token}`,
          'Content-Type': 'application/json'
        }
      });
      const data = await response.json();
      setAreas(data);
    } catch (error) {
      console.error('Error fetching areas:', error);
    } finally {
      setLoading(false);
    }
  };

  return { areas, loading, refetch: fetchAreas };
};
```

#### **Flutter - Servicios**
```dart
// services/reservation_service.dart
class ReservationService {
  final String baseUrl = 'http://localhost:8000/api';
  final String token;

  ReservationService(this.token);

  Future<List<AreaComun>> getAreasComunes() async {
    final response = await http.get(
      Uri.parse('$baseUrl/reservations/areas/'),
      headers: {
        'Authorization': 'Token $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      List<dynamic> data = json.decode(response.body);
      return data.map((json) => AreaComun.fromJson(json)).toList();
    } else {
      throw Exception('Failed to load areas');
    }
  }

  Future<Disponibilidad> consultarDisponibilidad(int areaId, String fecha) async {
    final response = await http.get(
      Uri.parse('$baseUrl/reservations/areas/$areaId/disponibilidad/?fecha=$fecha'),
      headers: {
        'Authorization': 'Token $token',
        'Content-Type': 'application/json',
      },
    );

    if (response.statusCode == 200) {
      return Disponibilidad.fromJson(json.decode(response.body));
    } else {
      throw Exception('Failed to load availability');
    }
  }
}
```

### 🧪 **Testing y Validación**

#### **Pruebas Unitarias**
```python
# tests/test_reservations.py
from django.test import TestCase
from backend.apps.reservations.models import AreaComun, Reserva

class ReservationTestCase(TestCase):
    def test_calculo_costo_total(self):
        area = AreaComun.objects.create(
            nombre="Gimnasio",
            costo_por_hora=5.00,
            costo_reserva=2.00
        )
        costo = area.calcular_costo_total(2)  # 2 horas
        self.assertEqual(costo, 12.00)  # (2*5) + 2
```

#### **Pruebas de API**
```python
# tests/test_api_reservations.py
from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model

class ReservationAPITestCase(APITestCase):
    def setUp(self):
        self.user = get_user_model().objects.create_user(
            username='testuser',
            password='testpass123'
        )
        self.client.force_authenticate(user=self.user)

    def test_listar_areas_comunes(self):
        response = self.client.get('/api/reservations/areas/')
        self.assertEqual(response.status_code, 200)
```

### 🔍 **Monitoreo y Logs**

#### **Eventos Importantes**
- Creación de reservas
- Confirmación de pagos
- Cancelaciones
- Errores de validación

#### **Métricas Sugeridas**
- Número de reservas por día
- Tasa de ocupación por área
- Ingresos generados
- Tiempo promedio de respuesta

### 🚨 **Troubleshooting**

#### **Problemas Comunes**

**Error: "No hay slots disponibles"**
- Verificar que existan horarios configurados para el día
- Revisar reservas existentes que puedan estar bloqueando

**Error: "No tiene permisos"**
- Verificar rol del usuario
- Confirmar que el token sea válido

**Error: "Fecha en el pasado"**
- Las reservas requieren anticipación mínima
- Verificar zona horaria del servidor

#### **Comandos Útiles**
```bash
# Ver reservas activas
python manage.py shell
>>> from backend.apps.reservations.models import Reserva
>>> Reserva.objects.filter(estado='pagada').count()

# Limpiar reservas de prueba
>>> Reserva.objects.filter(observaciones__contains='prueba').delete()
```

### 📈 **Mejoras Futuras**

#### **Funcionalidades Avanzadas**
- Sistema de notificaciones push
- Calendarios integrados (Google Calendar, Outlook)
- Reservas recurrentes
- Sistema de espera para áreas populares

#### **Optimizaciones**
- Caché de disponibilidad
- Índices de base de datos
- API de tiempo real con WebSockets

---

**📅 Última actualización:** Septiembre 2025
**👨‍💻 Desarrollado por:** Sistema de Información 2 - Parcial 1
**📧 Contacto:** [Información del desarrollador]</content>
<parameter name="filePath">c:\Users\PG\Desktop\Materias\Sistemas de informacion 2\Proyectos\Parcial 1\Backend_Django\docs\modulo4_reservations\README.md