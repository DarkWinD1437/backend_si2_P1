# 📡 API DOCUMENTATION - MÓDULO RESERVACIONES
## Endpoints Completos con Ejemplos

### 🔐 **Autenticación**
Todos los endpoints requieren autenticación mediante Token.

**Headers requeridos:**
```
Authorization: Token <your_token>
Content-Type: application/json
```

**Obtener Token:**
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "clave123"}'
```

---

## 🏢 **1. ÁREAS COMUNES**

### **GET /api/reservations/areas/**
Lista todas las áreas comunes disponibles.

**Respuesta Exitosa (200):**
```json
[
  {
    "id": 1,
    "nombre": "Gimnasio",
    "descripcion": "Gimnasio completamente equipado",
    "capacidad_maxima": 20,
    "costo_por_hora": "5.00",
    "costo_reserva": "2.00",
    "anticipacion_minima_horas": 24,
    "duracion_maxima_horas": 4,
    "activo": true,
    "imagen": null
  },
  {
    "id": 2,
    "nombre": "Piscina",
    "descripcion": "Piscina olímpica climatizada",
    "capacidad_maxima": 50,
    "costo_por_hora": "8.00",
    "costo_reserva": "3.00",
    "anticipacion_minima_horas": 48,
    "duracion_maxima_horas": 6,
    "activo": true,
    "imagen": null
  }
]
```

**Ejemplo de uso:**
```bash
curl -H "Authorization: Token eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
     http://localhost:8000/api/reservations/areas/
```

---

### **GET /api/reservations/areas/{id}/**
Obtiene detalles de un área específica.

**Parámetros URL:**
- `id`: ID del área común

**Respuesta Exitosa (200):**
```json
{
  "id": 1,
  "nombre": "Gimnasio",
  "descripcion": "Gimnasio completamente equipado",
  "capacidad_maxima": 20,
  "costo_por_hora": "5.00",
  "costo_reserva": "2.00",
  "anticipacion_minima_horas": 24,
  "duracion_maxima_horas": 4,
  "activo": true,
  "imagen": null,
  "horarios_disponibles": [
    {
      "id": 1,
      "dia_semana": 1,
      "hora_inicio": "06:00:00",
      "hora_fin": "22:00:00"
    }
  ]
}
```

---

### **GET /api/reservations/areas/{id}/disponibilidad/**
Consulta disponibilidad de slots para una fecha específica.

**Parámetros URL:**
- `id`: ID del área común

**Parámetros Query:**
- `fecha`: Fecha en formato YYYY-MM-DD (requerido)

**Respuesta Exitosa (200):**
```json
{
  "area": {
    "id": 1,
    "nombre": "Gimnasio"
  },
  "fecha": "2025-09-25",
  "slots_disponibles": [
    {
      "hora_inicio": "06:00",
      "hora_fin": "06:30",
      "disponible": true,
      "motivo_no_disponible": null
    },
    {
      "hora_inicio": "06:30",
      "hora_fin": "07:00",
      "disponible": true,
      "motivo_no_disponible": null
    },
    {
      "hora_inicio": "07:00",
      "hora_fin": "07:30",
      "disponible": false,
      "motivo_no_disponible": "Reservado"
    }
  ]
}
```

**Ejemplo de uso:**
```bash
curl -H "Authorization: Token eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
     "http://localhost:8000/api/reservations/areas/1/disponibilidad/?fecha=2025-09-25"
```

---

## 📅 **2. RESERVAS**

### **GET /api/reservations/reservas/**
Lista las reservas del usuario autenticado.

**Parámetros Query Opcionales:**
- `estado`: Filtrar por estado (PENDIENTE, CONFIRMADA, PAGADA, CANCELADA, USADA)
- `fecha_desde`: Fecha desde (YYYY-MM-DD)
- `fecha_hasta`: Fecha hasta (YYYY-MM-DD)

**Respuesta Exitosa (200):**
```json
[
  {
    "id": 1,
    "area_comun": {
      "id": 1,
      "nombre": "Gimnasio"
    },
    "usuario": {
      "id": 2,
      "username": "residente1",
      "first_name": "Juan",
      "last_name": "Pérez"
    },
    "fecha_reserva": "2025-09-25",
    "hora_inicio": "07:00:00",
    "hora_fin": "09:00:00",
    "numero_personas": 1,
    "costo_total": "12.00",
    "estado": "PENDIENTE",
    "observaciones": "Reserva para entrenamiento personal",
    "fecha_creacion": "2025-09-20T10:30:00Z",
    "fecha_confirmacion": null,
    "motivo_cancelacion": null
  }
]
```

---

### **POST /api/reservations/reservas/**
Crea una nueva reserva.

**Body requerido:**
```json
{
  "area_comun_id": 1,
  "fecha_reserva": "2025-09-25",
  "hora_inicio": "07:00",
  "hora_fin": "09:00",
  "numero_personas": 1,
  "observaciones": "Reserva para entrenamiento"
}
```

**Respuesta Exitosa (201):**
```json
{
  "id": 1,
  "area_comun": {
    "id": 1,
    "nombre": "Gimnasio"
  },
  "usuario": {
    "id": 2,
    "username": "residente1"
  },
  "fecha_reserva": "2025-09-25",
  "hora_inicio": "07:00:00",
  "hora_fin": "09:00:00",
  "numero_personas": 1,
  "costo_total": "12.00",
  "estado": "PENDIENTE",
  "observaciones": "Reserva para entrenamiento",
  "fecha_creacion": "2025-09-20T10:30:00Z"
}
```

**Ejemplo de uso:**
```bash
curl -X POST http://localhost:8000/api/reservations/reservas/ \
  -H "Authorization: Token eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..." \
  -H "Content-Type: application/json" \
  -d '{
    "area_comun_id": 1,
    "fecha_reserva": "2025-09-25",
    "hora_inicio": "07:00",
    "hora_fin": "09:00",
    "numero_personas": 1,
    "observaciones": "Reserva para entrenamiento"
  }'
```

---

### **GET /api/reservations/reservas/{id}/**
Obtiene detalles de una reserva específica.

**Parámetros URL:**
- `id`: ID de la reserva

---

### **PUT /api/reservations/reservas/{id}/confirmar/**
Confirma una reserva (solo administradores).

**Respuesta Exitosa (200):**
```json
{
  "id": 1,
  "estado": "CONFIRMADA",
  "fecha_confirmacion": "2025-09-20T11:00:00Z",
  "mensaje": "Reserva confirmada exitosamente"
}
```

---

### **PUT /api/reservations/reservas/{id}/cancelar/**
Cancela una reserva.

**Body opcional:**
```json
{
  "motivo_cancelacion": "Cambio de planes"
}
```

**Respuesta Exitosa (200):**
```json
{
  "id": 1,
  "estado": "CANCELADA",
  "motivo_cancelacion": "Cambio de planes",
  "mensaje": "Reserva cancelada exitosamente"
}
```

---

## 📊 **3. HORARIOS DISPONIBLES**

### **GET /api/reservations/horarios/**
Lista todos los horarios disponibles.

**Respuesta Exitosa (200):**
```json
[
  {
    "id": 1,
    "area_comun": {
      "id": 1,
      "nombre": "Gimnasio"
    },
    "dia_semana": 1,
    "hora_inicio": "06:00:00",
    "hora_fin": "22:00:00"
  }
]
```

---

## ❌ **CÓDIGOS DE ERROR**

### **400 Bad Request**
```json
{
  "error": "Datos inválidos",
  "detalles": {
    "fecha_reserva": ["La fecha debe ser futura"],
    "hora_inicio": ["El horario debe estar dentro del horario disponible"]
  }
}
```

### **401 Unauthorized**
```json
{
  "error": "Autenticación requerida",
  "detalles": "Token de autenticación inválido o expirado"
}
```

### **403 Forbidden**
```json
{
  "error": "Permisos insuficientes",
  "detalles": "No tiene permisos para realizar esta acción"
}
```

### **404 Not Found**
```json
{
  "error": "Recurso no encontrado",
  "detalles": "El área común o reserva especificada no existe"
}
```

### **409 Conflict**
```json
{
  "error": "Conflicto de reserva",
  "detalles": "El horario solicitado ya está reservado"
}
```

---

## 🔧 **EJEMPLOS PRÁCTICOS**

### **Flujo Completo de Reserva**

```bash
# 1. Login y obtener token
TOKEN=$(curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "residente1", "password": "clave123"}' \
  | jq -r '.token')

# 2. Listar áreas disponibles
curl -H "Authorization: Token $TOKEN" \
     http://localhost:8000/api/reservations/areas/

# 3. Consultar disponibilidad
curl -H "Authorization: Token $TOKEN" \
     "http://localhost:8000/api/reservations/areas/1/disponibilidad/?fecha=2025-09-25"

# 4. Crear reserva
curl -X POST http://localhost:8000/api/reservations/reservas/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "area_comun_id": 1,
    "fecha_reserva": "2025-09-25",
    "hora_inicio": "07:00",
    "hora_fin": "09:00",
    "numero_personas": 1,
    "observaciones": "Entrenamiento matutino"
  }'

# 5. Ver mis reservas
curl -H "Authorization: Token $TOKEN" \
     http://localhost:8000/api/reservations/reservas/

# 6. Cancelar reserva (si es necesario)
curl -X PUT http://localhost:8000/api/reservations/reservas/1/cancelar/ \
  -H "Authorization: Token $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"motivo_cancelacion": "Cambio de planes"}'
```

---

## 📱 **INTEGRACIÓN CON FRONTENDS**

### **React - Componente de Reserva**

```javascript
import React, { useState, useEffect } from 'react';

const ReservationForm = ({ areaId, onReservationCreated }) => {
  const [availability, setAvailability] = useState([]);
  const [selectedSlot, setSelectedSlot] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchAvailability();
  }, [areaId]);

  const fetchAvailability = async () => {
    const tomorrow = new Date();
    tomorrow.setDate(tomorrow.getDate() + 1);
    const fecha = tomorrow.toISOString().split('T')[0];

    try {
      const response = await fetch(
        `/api/reservations/areas/${areaId}/disponibilidad/?fecha=${fecha}`,
        {
          headers: {
            'Authorization': `Token ${localStorage.getItem('token')}`,
            'Content-Type': 'application/json'
          }
        }
      );
      const data = await response.json();
      setAvailability(data.slots_disponibles);
    } catch (error) {
      console.error('Error fetching availability:', error);
    }
  };

  const createReservation = async () => {
    if (!selectedSlot) return;

    setLoading(true);
    try {
      const response = await fetch('/api/reservations/reservas/', {
        method: 'POST',
        headers: {
          'Authorization': `Token ${localStorage.getItem('token')}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          area_comun_id: areaId,
          fecha_reserva: selectedSlot.fecha,
          hora_inicio: selectedSlot.hora_inicio,
          hora_fin: selectedSlot.hora_fin,
          numero_personas: 1,
          observaciones: 'Reserva desde React'
        })
      });

      if (response.ok) {
        const reservation = await response.json();
        onReservationCreated(reservation);
      } else {
        const error = await response.json();
        alert(`Error: ${error.error}`);
      }
    } catch (error) {
      console.error('Error creating reservation:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="reservation-form">
      <h3>Seleccionar Horario</h3>
      <div className="slots-grid">
        {availability.map((slot, index) => (
          <button
            key={index}
            className={`slot ${slot.disponible ? 'available' : 'unavailable'} ${
              selectedSlot === slot ? 'selected' : ''
            }`}
            disabled={!slot.disponible}
            onClick={() => setSelectedSlot(slot)}
          >
            {slot.hora_inicio} - {slot.hora_fin}
          </button>
        ))}
      </div>
      <button
        onClick={createReservation}
        disabled={!selectedSlot || loading}
        className="btn-reserve"
      >
        {loading ? 'Reservando...' : 'Reservar'}
      </button>
    </div>
  );
};

export default ReservationForm;
```

### **Flutter - Página de Reservas**

```dart
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'dart:convert';

class ReservationPage extends StatefulWidget {
  final int areaId;
  final String token;

  const ReservationPage({Key? key, required this.areaId, required this.token})
      : super(key: key);

  @override
  _ReservationPageState createState() => _ReservationPageState();
}

class _ReservationPageState extends State<ReservationPage> {
  List<dynamic> availability = [];
  Map<String, dynamic>? selectedSlot;
  bool loading = false;

  @override
  void initState() {
    super.initState();
    fetchAvailability();
  }

  Future<void> fetchAvailability() async {
    final tomorrow = DateTime.now().add(const Duration(days: 1));
    final fecha = "${tomorrow.year}-${tomorrow.month.toString().padLeft(2, '0')}-${tomorrow.day.toString().padLeft(2, '0')}";

    try {
      final response = await http.get(
        Uri.parse('http://localhost:8000/api/reservations/areas/${widget.areaId}/disponibilidad/?fecha=$fecha'),
        headers: {
          'Authorization': 'Token ${widget.token}',
          'Content-Type': 'application/json',
        },
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        setState(() {
          availability = data['slots_disponibles'];
        });
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error al cargar disponibilidad: $e')),
      );
    }
  }

  Future<void> createReservation() async {
    if (selectedSlot == null) return;

    setState(() => loading = true);

    try {
      final response = await http.post(
        Uri.parse('http://localhost:8000/api/reservations/reservas/'),
        headers: {
          'Authorization': 'Token ${widget.token}',
          'Content-Type': 'application/json',
        },
        body: json.encode({
          'area_comun_id': widget.areaId,
          'fecha_reserva': selectedSlot!['fecha'],
          'hora_inicio': selectedSlot!['hora_inicio'],
          'hora_fin': selectedSlot!['hora_fin'],
          'numero_personas': 1,
          'observaciones': 'Reserva desde Flutter',
        }),
      );

      if (response.statusCode == 201) {
        final reservation = json.decode(response.body);
        Navigator.pop(context, reservation);
      } else {
        final error = json.decode(response.body);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Error: ${error['error']}')),
        );
      }
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error al crear reserva: $e')),
      );
    } finally {
      setState(() => loading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Reservar Área')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            const Text(
              'Horarios Disponibles',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            Expanded(
              child: GridView.builder(
                gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                  crossAxisCount: 2,
                  childAspectRatio: 2,
                  crossAxisSpacing: 8,
                  mainAxisSpacing: 8,
                ),
                itemCount: availability.length,
                itemBuilder: (context, index) {
                  final slot = availability[index];
                  final isAvailable = slot['disponible'];
                  final isSelected = selectedSlot == slot;

                  return ElevatedButton(
                    onPressed: isAvailable ? () => setState(() => selectedSlot = slot) : null,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: isSelected
                          ? Colors.blue
                          : isAvailable
                              ? Colors.green
                              : Colors.grey,
                    ),
                    child: Text(
                      '${slot['hora_inicio']} - ${slot['hora_fin']}',
                      style: const TextStyle(color: Colors.white),
                    ),
                  );
                },
              ),
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: selectedSlot != null && !loading ? createReservation : null,
              style: ElevatedButton.styleFrom(
                minimumSize: const Size(double.infinity, 50),
              ),
              child: loading
                  ? const CircularProgressIndicator()
                  : const Text('Reservar'),
            ),
          ],
        ),
      ),
    );
  }
}
```

---

**📅 Versión:** 1.0
**📧 Soporte:** [Información de contacto]
**🔗 Documentación relacionada:** Ver `MODULO_RESERVATIONS_COMPLETO.md`