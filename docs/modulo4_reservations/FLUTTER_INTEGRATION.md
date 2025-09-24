# 📱 EJEMPLOS FLUTTER - MÓDULO RESERVACIONES

## Configuración del Proyecto

### **1. Dependencias en pubspec.yaml**
```yaml
dependencies:
  flutter:
    sdk: flutter
  http: ^1.1.0
  shared_preferences: ^2.2.2
  intl: ^0.19.0
  provider: ^6.0.5
  fluttertoast: ^8.2.4
```

### **2. Configuración de API**
```dart
// lib/services/api_service.dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';

class ApiService {
  static const String baseUrl = 'http://localhost:8000/api';
  static const String tokenKey = 'auth_token';

  static Future<String?> getToken() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(tokenKey);
  }

  static Future<void> setToken(String token) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(tokenKey, token);
  }

  static Future<void> clearToken() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(tokenKey);
  }

  static Future<Map<String, String>> getHeaders() async {
    final token = await getToken();
    return {
      'Content-Type': 'application/json',
      if (token != null) 'Authorization': 'Token $token',
    };
  }

  static Future<http.Response> get(String endpoint) async {
    final headers = await getHeaders();
    final response = await http.get(
      Uri.parse('$baseUrl$endpoint'),
      headers: headers,
    );
    return _handleResponse(response);
  }

  static Future<http.Response> post(String endpoint, Map<String, dynamic> data) async {
    final headers = await getHeaders();
    final response = await http.post(
      Uri.parse('$baseUrl$endpoint'),
      headers: headers,
      body: json.encode(data),
    );
    return _handleResponse(response);
  }

  static Future<http.Response> put(String endpoint, Map<String, dynamic> data) async {
    final headers = await getHeaders();
    final response = await http.put(
      Uri.parse('$baseUrl$endpoint'),
      headers: headers,
      body: json.encode(data),
    );
    return _handleResponse(response);
  }

  static http.Response _handleResponse(http.Response response) {
    if (response.statusCode == 401) {
      clearToken();
      throw Exception('Sesión expirada');
    }
    return response;
  }
}
```

---

## 🔐 **Autenticación**

### **Modelo de Usuario**
```dart
// lib/models/user.dart
class User {
  final int id;
  final String username;
  final String firstName;
  final String lastName;
  final String email;
  final String role;

  User({
    required this.id,
    required this.username,
    required this.firstName,
    required this.lastName,
    required this.email,
    required this.role,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'],
      username: json['username'],
      firstName: json['first_name'],
      lastName: json['last_name'],
      email: json['email'] ?? '',
      role: json['role'] ?? 'residente',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'username': username,
      'first_name': firstName,
      'last_name': lastName,
      'email': email,
      'role': role,
    };
  }
}
```

### **Servicio de Autenticación**
```dart
// lib/services/auth_service.dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import '../models/user.dart';
import 'api_service.dart';

class AuthService {
  static const String loginEndpoint = '/auth/login/';

  static Future<Map<String, dynamic>> login(String username, String password) async {
    final response = await http.post(
      Uri.parse('${ApiService.baseUrl}$loginEndpoint'),
      headers: {'Content-Type': 'application/json'},
      body: json.encode({
        'username': username,
        'password': password,
      }),
    );

    if (response.statusCode == 200) {
      final data = json.decode(response.body);
      final token = data['token'];
      final user = User.fromJson(data['user']);

      await ApiService.setToken(token);

      return {
        'token': token,
        'user': user,
      };
    } else {
      final error = json.decode(response.body);
      throw Exception(error['error'] ?? 'Error de autenticación');
    }
  }

  static Future<void> logout() async {
    await ApiService.clearToken();
  }

  static Future<bool> isLoggedIn() async {
    final token = await ApiService.getToken();
    return token != null;
  }
}
```

### **Pantalla de Login**
```dart
// lib/screens/login_screen.dart
import 'package:flutter/material.dart';
import 'package:fluttertoast/fluttertoast.dart';
import '../services/auth_service.dart';
import '../models/user.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({Key? key}) : super(key: key);

  @override
  _LoginScreenState createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _usernameController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _isLoading = false;

  @override
  void dispose() {
    _usernameController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _login() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isLoading = true);

    try {
      final result = await AuthService.login(
        _usernameController.text.trim(),
        _passwordController.text.trim(),
      );

      final user = result['user'] as User;

      Fluttertoast.showToast(
        msg: 'Bienvenido ${user.firstName}',
        toastLength: Toast.LENGTH_SHORT,
        gravity: ToastGravity.BOTTOM,
      );

      Navigator.pushReplacementNamed(context, '/home');
    } catch (e) {
      Fluttertoast.showToast(
        msg: e.toString(),
        toastLength: Toast.LENGTH_LONG,
        gravity: ToastGravity.BOTTOM,
        backgroundColor: Colors.red,
      );
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24.0),
          child: Form(
            key: _formKey,
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                const Text(
                  'SmartCondominium',
                  style: TextStyle(
                    fontSize: 32,
                    fontWeight: FontWeight.bold,
                    color: Colors.blue,
                  ),
                  textAlign: TextAlign.center,
                ),
                const SizedBox(height: 48),

                TextFormField(
                  controller: _usernameController,
                  decoration: const InputDecoration(
                    labelText: 'Usuario',
                    border: OutlineInputBorder(),
                    prefixIcon: Icon(Icons.person),
                  ),
                  validator: (value) {
                    if (value == null || value.isEmpty) {
                      return 'Por favor ingrese su usuario';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 16),

                TextFormField(
                  controller: _passwordController,
                  decoration: const InputDecoration(
                    labelText: 'Contraseña',
                    border: OutlineInputBorder(),
                    prefixIcon: Icon(Icons.lock),
                  ),
                  obscureText: true,
                  validator: (value) {
                    if (value == null || value.isEmpty) {
                      return 'Por favor ingrese su contraseña';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 24),

                ElevatedButton(
                  onPressed: _isLoading ? null : _login,
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 16),
                  ),
                  child: _isLoading
                      ? const CircularProgressIndicator()
                      : const Text('Iniciar Sesión'),
                ),

                const SizedBox(height: 16),
                TextButton(
                  onPressed: () {
                    // Implementar recuperación de contraseña
                  },
                  child: const Text('¿Olvidaste tu contraseña?'),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
```

---

## 🏢 **Modelos de Datos**

### **Modelo de Área Común**
```dart
// lib/models/area_comun.dart
class AreaComun {
  final int id;
  final String nombre;
  final String descripcion;
  final int capacidadMaxima;
  final String costoPorHora;
  final String costoReserva;
  final int anticipacionMinimaHoras;
  final int duracionMaximaHoras;
  final bool activo;
  final String? imagen;

  AreaComun({
    required this.id,
    required this.nombre,
    required this.descripcion,
    required this.capacidadMaxima,
    required this.costoPorHora,
    required this.costoReserva,
    required this.anticipacionMinimaHoras,
    required this.duracionMaximaHoras,
    required this.activo,
    this.imagen,
  });

  factory AreaComun.fromJson(Map<String, dynamic> json) {
    return AreaComun(
      id: json['id'],
      nombre: json['nombre'],
      descripcion: json['descripcion'],
      capacidadMaxima: json['capacidad_maxima'],
      costoPorHora: json['costo_por_hora'],
      costoReserva: json['costo_reserva'],
      anticipacionMinimaHoras: json['anticipacion_minima_horas'],
      duracionMaximaHoras: json['duracion_maxima_horas'],
      activo: json['activo'],
      imagen: json['imagen'],
    );
  }

  double get costoPorHoraDouble => double.parse(costoPorHora);
  double get costoReservaDouble => double.parse(costoReserva);
}
```

### **Modelo de Reserva**
```dart
// lib/models/reserva.dart
import 'area_comun.dart';
import 'user.dart';

class Reserva {
  final int id;
  final AreaComun areaComun;
  final User usuario;
  final String fechaReserva;
  final String horaInicio;
  final String horaFin;
  final int numeroPersonas;
  final String costoTotal;
  final String estado;
  final String? observaciones;
  final String fechaCreacion;
  final String? fechaConfirmacion;
  final String? motivoCancelacion;

  Reserva({
    required this.id,
    required this.areaComun,
    required this.usuario,
    required this.fechaReserva,
    required this.horaInicio,
    required this.horaFin,
    required this.numeroPersonas,
    required this.costoTotal,
    required this.estado,
    this.observaciones,
    required this.fechaCreacion,
    this.fechaConfirmacion,
    this.motivoCancelacion,
  });

  factory Reserva.fromJson(Map<String, dynamic> json) {
    return Reserva(
      id: json['id'],
      areaComun: AreaComun.fromJson(json['area_comun']),
      usuario: User.fromJson(json['usuario']),
      fechaReserva: json['fecha_reserva'],
      horaInicio: json['hora_inicio'],
      horaFin: json['hora_fin'],
      numeroPersonas: json['numero_personas'],
      costoTotal: json['costo_total'],
      estado: json['estado'],
      observaciones: json['observaciones'],
      fechaCreacion: json['fecha_creacion'],
      fechaConfirmacion: json['fecha_confirmacion'],
      motivoCancelacion: json['motivo_cancelacion'],
    );
  }

  bool get puedeCancelar => estado == 'PENDIENTE';
  bool get estaConfirmada => estado == 'CONFIRMADA';
  bool get estaPagada => estado == 'PAGADA';
  bool get estaCancelada => estado == 'CANCELADA';
  bool get estaUsada => estado == 'USADA';

  Color get estadoColor {
    switch (estado) {
      case 'PENDIENTE':
        return Colors.orange;
      case 'CONFIRMADA':
        return Colors.blue;
      case 'PAGADA':
        return Colors.green;
      case 'CANCELADA':
        return Colors.red;
      case 'USADA':
        return Colors.grey;
      default:
        return Colors.grey;
    }
  }
}
```

### **Modelo de Disponibilidad**
```dart
// lib/models/disponibilidad.dart
class SlotDisponible {
  final String horaInicio;
  final String horaFin;
  final bool disponible;
  final String? motivoNoDisponible;

  SlotDisponible({
    required this.horaInicio,
    required this.horaFin,
    required this.disponible,
    this.motivoNoDisponible,
  });

  factory SlotDisponible.fromJson(Map<String, dynamic> json) {
    return SlotDisponible(
      horaInicio: json['hora_inicio'],
      horaFin: json['hora_fin'],
      disponible: json['disponible'],
      motivoNoDisponible: json['motivo_no_disponible'],
    );
  }
}

class Disponibilidad {
  final AreaComun area;
  final String fecha;
  final List<SlotDisponible> slotsDisponibles;

  Disponibilidad({
    required this.area,
    required this.fecha,
    required this.slotsDisponibles,
  });

  factory Disponibilidad.fromJson(Map<String, dynamic> json) {
    return Disponibilidad(
      area: AreaComun.fromJson(json['area']),
      fecha: json['fecha'],
      slotsDisponibles: (json['slots_disponibles'] as List)
          .map((slot) => SlotDisponible.fromJson(slot))
          .toList(),
    );
  }
}
```

---

## 🏢 **Servicio de Áreas Comunes**

### **Servicio de Áreas**
```dart
// lib/services/areas_service.dart
import '../models/area_comun.dart';
import 'api_service.dart';

class AreasService {
  static Future<List<AreaComun>> getAreasComunes() async {
    final response = await ApiService.get('/reservations/areas/');

    if (response.statusCode == 200) {
      final List<dynamic> data = json.decode(response.body);
      return data.map((json) => AreaComun.fromJson(json)).toList();
    } else {
      throw Exception('Error al cargar áreas comunes');
    }
  }

  static Future<AreaComun> getAreaComun(int id) async {
    final response = await ApiService.get('/reservations/areas/$id/');

    if (response.statusCode == 200) {
      return AreaComun.fromJson(json.decode(response.body));
    } else {
      throw Exception('Error al cargar área común');
    }
  }
}
```

### **Pantalla de Áreas Comunes**
```dart
// lib/screens/areas_screen.dart
import 'package:flutter/material.dart';
import '../models/area_comun.dart';
import '../services/areas_service.dart';
import 'area_detail_screen.dart';

class AreasScreen extends StatefulWidget {
  const AreasScreen({Key? key}) : super(key: key);

  @override
  _AreasScreenState createState() => _AreasScreenState();
}

class _AreasScreenState extends State<AreasScreen> {
  List<AreaComun> _areas = [];
  bool _isLoading = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _loadAreas();
  }

  Future<void> _loadAreas() async {
    try {
      setState(() => _isLoading = true);
      final areas = await AreasService.getAreasComunes();
      setState(() {
        _areas = areas;
        _error = null;
      });
    } catch (e) {
      setState(() => _error = e.toString());
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Áreas Comunes'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: _loadAreas,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Text(_error!),
                      ElevatedButton(
                        onPressed: _loadAreas,
                        child: const Text('Reintentar'),
                      ),
                    ],
                  ),
                )
              : ListView.builder(
                  itemCount: _areas.length,
                  itemBuilder: (context, index) {
                    final area = _areas[index];
                    return Card(
                      margin: const EdgeInsets.symmetric(
                        horizontal: 16,
                        vertical: 8,
                      ),
                      child: ListTile(
                        leading: const Icon(Icons.business),
                        title: Text(area.nombre),
                        subtitle: Text(area.descripcion),
                        trailing: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          crossAxisAlignment: CrossAxisAlignment.end,
                          children: [
                            Text('\$${area.costoPorHora}/hora'),
                            Text('Cap: ${area.capacidadMaxima}'),
                          ],
                        ),
                        onTap: () {
                          Navigator.push(
                            context,
                            MaterialPageRoute(
                              builder: (context) => AreaDetailScreen(area: area),
                            ),
                          );
                        },
                      ),
                    );
                  },
                ),
    );
  }
}
```

### **Pantalla de Detalle de Área**
```dart
// lib/screens/area_detail_screen.dart
import 'package:flutter/material.dart';
import '../models/area_comun.dart';
import 'reservation_screen.dart';

class AreaDetailScreen extends StatelessWidget {
  final AreaComun area;

  const AreaDetailScreen({Key? key, required this.area}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(area.nombre),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      area.nombre,
                      style: const TextStyle(
                        fontSize: 24,
                        fontWeight: FontWeight.bold,
                      ),
                    ),
                    const SizedBox(height: 8),
                    Text(area.descripcion),
                    const SizedBox(height: 16),
                    _buildInfoRow('Capacidad máxima', '${area.capacidadMaxima} personas'),
                    _buildInfoRow('Costo por hora', '\$${area.costoPorHora}'),
                    _buildInfoRow('Costo de reserva', '\$${area.costoReserva}'),
                    _buildInfoRow('Anticipación mínima', '${area.anticipacionMinimaHoras} horas'),
                    _buildInfoRow('Duración máxima', '${area.duracionMaximaHoras} horas'),
                  ],
                ),
              ),
            ),
            const SizedBox(height: 24),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: () {
                  Navigator.push(
                    context,
                    MaterialPageRoute(
                      builder: (context) => ReservationScreen(area: area),
                    ),
                  );
                },
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 16),
                ),
                child: const Text('Reservar Área'),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInfoRow(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: const TextStyle(fontWeight: FontWeight.w500)),
          Text(value),
        ],
      ),
    );
  }
}
```

---

## 📅 **Sistema de Reservas**

### **Servicio de Reservas**
```dart
// lib/services/reservations_service.dart
import '../models/reserva.dart';
import '../models/disponibilidad.dart';
import 'api_service.dart';

class ReservationsService {
  static Future<List<Reserva>> getMyReservations({String? estado}) async {
    final queryParams = estado != null ? '?estado=$estado' : '';
    final response = await ApiService.get('/reservations/reservas/$queryParams');

    if (response.statusCode == 200) {
      final List<dynamic> data = json.decode(response.body);
      return data.map((json) => Reserva.fromJson(json)).toList();
    } else {
      throw Exception('Error al cargar reservas');
    }
  }

  static Future<Disponibilidad> getDisponibilidad(int areaId, String fecha) async {
    final response = await ApiService.get(
      '/reservations/areas/$areaId/disponibilidad/?fecha=$fecha'
    );

    if (response.statusCode == 200) {
      return Disponibilidad.fromJson(json.decode(response.body));
    } else {
      throw Exception('Error al cargar disponibilidad');
    }
  }

  static Future<Reserva> createReservation(Map<String, dynamic> data) async {
    final response = await ApiService.post('/reservations/reservas/', data);

    if (response.statusCode == 201) {
      return Reserva.fromJson(json.decode(response.body));
    } else {
      final error = json.decode(response.body);
      throw Exception(error['error'] ?? 'Error al crear reserva');
    }
  }

  static Future<void> cancelReservation(int reservationId, {String? motivo}) async {
    final data = motivo != null ? {'motivo_cancelacion': motivo} : {};
    final response = await ApiService.put(
      '/reservations/reservas/$reservationId/cancelar/',
      data
    );

    if (response.statusCode != 200) {
      final error = json.decode(response.body);
      throw Exception(error['error'] ?? 'Error al cancelar reserva');
    }
  }
}
```

### **Pantalla de Creación de Reserva**
```dart
// lib/screens/reservation_screen.dart
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../models/area_comun.dart';
import '../models/disponibilidad.dart';
import '../services/reservations_service.dart';

class ReservationScreen extends StatefulWidget {
  final AreaComun area;

  const ReservationScreen({Key? key, required this.area}) : super(key: key);

  @override
  _ReservationScreenState createState() => _ReservationScreenState();
}

class _ReservationScreenState extends State<ReservationScreen> {
  DateTime? _selectedDate;
  Disponibilidad? _availability;
  SlotDisponible? _selectedSlot;
  int _numeroPersonas = 1;
  String _observaciones = '';
  bool _isLoading = false;

  Future<void> _selectDate(BuildContext context) async {
    final DateTime? picked = await showDatePicker(
      context: context,
      initialDate: DateTime.now().add(const Duration(days: 1)),
      firstDate: DateTime.now().add(const Duration(days: 1)),
      lastDate: DateTime.now().add(const Duration(days: 30)),
    );

    if (picked != null && picked != _selectedDate) {
      setState(() => _selectedDate = picked);
      _loadAvailability();
    }
  }

  Future<void> _loadAvailability() async {
    if (_selectedDate == null) return;

    setState(() => _isLoading = true);
    try {
      final fecha = DateFormat('yyyy-MM-dd').format(_selectedDate!);
      final availability = await ReservationsService.getDisponibilidad(
        widget.area.id,
        fecha,
      );
      setState(() {
        _availability = availability;
        _selectedSlot = null;
      });
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: $e')),
      );
    } finally {
      setState(() => _isLoading = false);
    }
  }

  double _calculateCost() {
    if (_selectedSlot == null) return 0;

    final start = DateFormat('HH:mm').parse(_selectedSlot!.horaInicio);
    final end = DateFormat('HH:mm').parse(_selectedSlot!.horaFin);
    final hours = end.difference(start).inHours.toDouble();

    return (hours * widget.area.costoPorHoraDouble) + widget.area.costoReservaDouble;
  }

  Future<void> _createReservation() async {
    if (_selectedDate == null || _selectedSlot == null) return;

    setState(() => _isLoading = true);

    try {
      final data = {
        'area_comun_id': widget.area.id,
        'fecha_reserva': DateFormat('yyyy-MM-dd').format(_selectedDate!),
        'hora_inicio': _selectedSlot!.horaInicio,
        'hora_fin': _selectedSlot!.horaFin,
        'numero_personas': _numeroPersonas,
        'observaciones': _observaciones,
      };

      final reservation = await ReservationsService.createReservation(data);

      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Reserva creada exitosamente')),
      );

      Navigator.pop(context, reservation);
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error: $e')),
      );
    } finally {
      setState(() => _isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Reservar ${widget.area.nombre}'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Selector de fecha
            Card(
              child: ListTile(
                title: const Text('Fecha de Reserva'),
                subtitle: _selectedDate != null
                    ? Text(DateFormat('EEEE, dd/MM/yyyy').format(_selectedDate!))
                    : const Text('Selecciona una fecha'),
                trailing: const Icon(Icons.calendar_today),
                onTap: () => _selectDate(context),
              ),
            ),

            if (_availability != null) ...[
              const SizedBox(height: 16),
              const Text(
                'Horarios Disponibles',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),

              _isLoading
                  ? const Center(child: CircularProgressIndicator())
                  : GridView.builder(
                      shrinkWrap: true,
                      physics: const NeverScrollableScrollPhysics(),
                      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                        crossAxisCount: 2,
                        childAspectRatio: 2,
                        crossAxisSpacing: 8,
                        mainAxisSpacing: 8,
                      ),
                      itemCount: _availability!.slotsDisponibles.length,
                      itemBuilder: (context, index) {
                        final slot = _availability!.slotsDisponibles[index];
                        final isSelected = _selectedSlot == slot;

                        return ElevatedButton(
                          onPressed: slot.disponible ? () => setState(() => _selectedSlot = slot) : null,
                          style: ElevatedButton.styleFrom(
                            backgroundColor: isSelected
                                ? Colors.blue
                                : slot.disponible
                                    ? Colors.green
                                    : Colors.grey,
                          ),
                          child: Text(
                            '${slot.horaInicio}\n${slot.horaFin}',
                            textAlign: TextAlign.center,
                            style: const TextStyle(color: Colors.white),
                          ),
                        );
                      },
                    ),
            ],

            if (_selectedSlot != null) ...[
              const SizedBox(height: 16),
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Detalles de la Reserva',
                        style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                      ),
                      const SizedBox(height: 16),

                      // Número de personas
                      Row(
                        children: [
                          const Text('Número de personas: '),
                          DropdownButton<int>(
                            value: _numeroPersonas,
                            items: List.generate(
                              widget.area.capacidadMaxima,
                              (index) => DropdownMenuItem(
                                value: index + 1,
                                child: Text('${index + 1}'),
                              ),
                            ),
                            onChanged: (value) => setState(() => _numeroPersonas = value!),
                          ),
                        ],
                      ),

                      const SizedBox(height: 16),

                      // Observaciones
                      TextField(
                        decoration: const InputDecoration(
                          labelText: 'Observaciones (opcional)',
                          border: OutlineInputBorder(),
                        ),
                        maxLines: 3,
                        onChanged: (value) => _observaciones = value,
                      ),

                      const SizedBox(height: 16),

                      // Costo total
                      Container(
                        padding: const EdgeInsets.all(12),
                        decoration: BoxDecoration(
                          color: Colors.blue.shade50,
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: Row(
                          mainAxisAlignment: MainAxisAlignment.spaceBetween,
                          children: [
                            const Text(
                              'Costo Total:',
                              style: TextStyle(fontWeight: FontWeight.bold),
                            ),
                            Text(
                              '\$${_calculateCost().toStringAsFixed(2)}',
                              style: const TextStyle(
                                fontSize: 18,
                                fontWeight: FontWeight.bold,
                                color: Colors.green,
                              ),
                            ),
                          ],
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],

            const SizedBox(height: 24),

            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: (_selectedDate != null && _selectedSlot != null && !_isLoading)
                    ? _createReservation
                    : null,
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 16),
                ),
                child: _isLoading
                    ? const CircularProgressIndicator()
                    : const Text('Confirmar Reserva'),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
```

---

## 📋 **Gestión de Mis Reservas**

### **Pantalla de Mis Reservas**
```dart
// lib/screens/my_reservations_screen.dart
import 'package:flutter/material.dart';
import '../models/reserva.dart';
import '../services/reservations_service.dart';

class MyReservationsScreen extends StatefulWidget {
  const MyReservationsScreen({Key? key}) : super(key: key);

  @override
  _MyReservationsScreenState createState() => _MyReservationsScreenState();
}

class _MyReservationsScreenState extends State<MyReservationsScreen> {
  List<Reserva> _reservations = [];
  bool _isLoading = true;
  String _filter = 'todas';

  @override
  void initState() {
    super.initState();
    _loadReservations();
  }

  Future<void> _loadReservations() async {
    try {
      setState(() => _isLoading = true);
      final reservations = await ReservationsService.getMyReservations(
        estado: _filter != 'todas' ? _filter : null,
      );
      setState(() => _reservations = reservations);
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error al cargar reservas: $e')),
      );
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _cancelReservation(int reservationId) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Cancelar Reserva'),
        content: const Text('¿Está seguro de que desea cancelar esta reserva?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('No'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Sí'),
          ),
        ],
      ),
    );

    if (confirmed != true) return;

    try {
      await ReservationsService.cancelReservation(reservationId);
      _loadReservations();
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Reserva cancelada exitosamente')),
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error al cancelar reserva: $e')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Mis Reservas'),
        actions: [
          PopupMenuButton<String>(
            onSelected: (value) {
              setState(() => _filter = value);
              _loadReservations();
            },
            itemBuilder: (context) => [
              const PopupMenuItem(value: 'todas', child: Text('Todas')),
              const PopupMenuItem(value: 'PENDIENTE', child: Text('Pendientes')),
              const PopupMenuItem(value: 'CONFIRMADA', child: Text('Confirmadas')),
              const PopupMenuItem(value: 'PAGADA', child: Text('Pagadas')),
              const PopupMenuItem(value: 'CANCELADA', child: Text('Canceladas')),
              const PopupMenuItem(value: 'USADA', child: Text('Usadas')),
            ],
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _reservations.isEmpty
              ? const Center(
                  child: Text('No tienes reservas'),
                )
              : RefreshIndicator(
                  onRefresh: _loadReservations,
                  child: ListView.builder(
                    itemCount: _reservations.length,
                    itemBuilder: (context, index) {
                      final reservation = _reservations[index];
                      return Card(
                        margin: const EdgeInsets.symmetric(
                          horizontal: 16,
                          vertical: 8,
                        ),
                        child: Padding(
                          padding: const EdgeInsets.all(16),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Row(
                                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                                children: [
                                  Text(
                                    reservation.areaComun.nombre,
                                    style: const TextStyle(
                                      fontSize: 18,
                                      fontWeight: FontWeight.bold,
                                    ),
                                  ),
                                  Container(
                                    padding: const EdgeInsets.symmetric(
                                      horizontal: 8,
                                      vertical: 4,
                                    ),
                                    decoration: BoxDecoration(
                                      color: reservation.estadoColor.withOpacity(0.2),
                                      borderRadius: BorderRadius.circular(12),
                                    ),
                                    child: Text(
                                      reservation.estado,
                                      style: TextStyle(
                                        color: reservation.estadoColor,
                                        fontWeight: FontWeight.bold,
                                      ),
                                    ),
                                  ),
                                ],
                              ),
                              const SizedBox(height: 8),
                              Text('Fecha: ${reservation.fechaReserva}'),
                              Text('Horario: ${reservation.horaInicio} - ${reservation.horaFin}'),
                              Text('Personas: ${reservation.numeroPersonas}'),
                              Text('Costo: \$${reservation.costoTotal}'),
                              if (reservation.observaciones != null) ...[
                                const SizedBox(height: 8),
                                Text('Observaciones: ${reservation.observaciones}'),
                              ],
                              if (reservation.puedeCancelar) ...[
                                const SizedBox(height: 16),
                                SizedBox(
                                  width: double.infinity,
                                  child: OutlinedButton(
                                    onPressed: () => _cancelReservation(reservation.id),
                                    style: OutlinedButton.styleFrom(
                                      side: const BorderSide(color: Colors.red),
                                    ),
                                    child: const Text(
                                      'Cancelar Reserva',
                                      style: TextStyle(color: Colors.red),
                                    ),
                                  ),
                                ),
                              ],
                            ],
                          ),
                        ),
                      );
                    },
                  ),
                ),
    );
  }
}
```

---

## 🎨 **Tema y Estilos**

### **Configuración del Tema**
```dart
// lib/main.dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'screens/login_screen.dart';
import 'screens/home_screen.dart';
import 'services/auth_service.dart';

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'SmartCondominium',
      theme: ThemeData(
        primarySwatch: Colors.blue,
        visualDensity: VisualDensity.adaptivePlatformDensity,
        inputDecorationTheme: const InputDecorationTheme(
          border: OutlineInputBorder(),
          contentPadding: EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        ),
        elevatedButtonTheme: ElevatedButtonThemeData(
          style: ElevatedButton.styleFrom(
            padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 12),
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(8),
            ),
          ),
        ),
        cardTheme: CardTheme(
          elevation: 4,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(12),
          ),
        ),
      ),
      home: const AuthWrapper(),
      routes: {
        '/home': (context) => const HomeScreen(),
        '/areas': (context) => const AreasScreen(),
        '/reservations': (context) => const MyReservationsScreen(),
      },
    );
  }
}

class AuthWrapper extends StatefulWidget {
  const AuthWrapper({Key? key}) : super(key: key);

  @override
  _AuthWrapperState createState() => _AuthWrapperState();
}

class _AuthWrapperState extends State<AuthWrapper> {
  bool _isLoggedIn = false;
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _checkAuthStatus();
  }

  Future<void> _checkAuthStatus() async {
    final isLoggedIn = await AuthService.isLoggedIn();
    setState(() {
      _isLoggedIn = isLoggedIn;
      _isLoading = false;
    });
  }

  @override
  Widget build(BuildContext context) {
    if (_isLoading) {
      return const Scaffold(
        body: Center(child: CircularProgressIndicator()),
      );
    }

    return _isLoggedIn ? const HomeScreen() : const LoginScreen();
  }
}
```

---

## 🚀 **Pantalla Principal (Home)**

### **Pantalla Home**
```dart
// lib/screens/home_screen.dart
import 'package:flutter/material.dart';
import 'areas_screen.dart';
import 'my_reservations_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  _HomeScreenState createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  int _selectedIndex = 0;

  static const List<Widget> _screens = [
    AreasScreen(),
    MyReservationsScreen(),
  ];

  void _onItemTapped(int index) {
    setState(() => _selectedIndex = index);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: _screens[_selectedIndex],
      bottomNavigationBar: BottomNavigationBar(
        items: const [
          BottomNavigationBarItem(
            icon: Icon(Icons.business),
            label: 'Áreas Comunes',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.calendar_today),
            label: 'Mis Reservas',
          ),
        ],
        currentIndex: _selectedIndex,
        onTap: _onItemTapped,
      ),
    );
  }
}
```

---

**💡 Consejos para Implementación:**

1. **Manejo de Estado**: Considera usar Provider o Riverpod para manejo de estado global
2. **Navegación**: Implementa navegación con nombre para mejor organización
3. **Validación**: Agrega validación de formularios más robusta
4. **Offline**: Implementa caché local para mejor UX
5. **Notificaciones**: Agrega notificaciones push para recordatorios de reservas
6. **Testing**: Implementa tests unitarios y de integración

**🔗 Recursos Adicionales:**
- [Flutter Documentation](https://flutter.dev/docs)
- [Dart Documentation](https://dart.dev/guides)
- [Provider Package](https://pub.dev/packages/provider)