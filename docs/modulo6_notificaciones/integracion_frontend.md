# Integración Frontend - Módulo de Notificaciones

## React Integration

### Instalación de dependencias:
```bash
npm install firebase web-push
```

### Configuración Firebase:
```javascript
// src/services/firebase.js
import { initializeApp } from 'firebase/app';
import { getMessaging, getToken } from 'firebase/messaging';

const firebaseConfig = {
  apiKey: process.env.REACT_APP_FIREBASE_API_KEY,
  authDomain: process.env.REACT_APP_FIREBASE_AUTH_DOMAIN,
  projectId: process.env.REACT_APP_FIREBASE_PROJECT_ID,
  messagingSenderId: process.env.REACT_APP_FIREBASE_MESSAGING_SENDER_ID,
  appId: process.env.REACT_APP_FIREBASE_APP_ID
};

const app = initializeApp(firebaseConfig);
const messaging = getMessaging(app);

export { messaging, getToken };
```

### Servicio de Notificaciones:
```javascript
// src/services/notificationService.js
import { getToken } from './firebase';
import api from './api'; // Tu instancia de axios

class NotificationService {
  async registerDevice(vapidKey) {
    try {
      const token = await getToken(messaging, {
        vapidKey: vapidKey
      });

      const response = await api.post('/api/notificaciones/dispositivos/', {
        token_push: token,
        tipo_dispositivo: 'web',
        nombre_dispositivo: navigator.userAgent
      });

      return response.data;
    } catch (error) {
      console.error('Error registering device:', error);
      throw error;
    }
  }

  async getPreferences() {
    const response = await api.get('/api/notificaciones/preferencias/');
    return response.data;
  }

  async updatePreferences(preferences) {
    const response = await api.patch('/api/notificaciones/preferencias/bulk-update/', {
      preferencias: preferences
    });
    return response.data;
  }

  async getNotifications(page = 1, filters = {}) {
    const params = new URLSearchParams({ page, ...filters });
    const response = await api.get(`/api/notificaciones/?${params}`);
    return response.data;
  }

  async markAsRead(notificationId) {
    const response = await api.patch(`/api/notificaciones/${notificationId}/marcar-leida/`);
    return response.data;
  }

  async markAllAsRead() {
    const response = await api.patch('/api/notificaciones/marcar-todas-leidas/');
    return response.data;
  }
}

export default new NotificationService();
```

### Hook de React para Notificaciones:
```javascript
// src/hooks/useNotifications.js
import { useState, useEffect } from 'react';
import { onMessage } from 'firebase/messaging';
import { messaging } from '../services/firebase';
import notificationService from '../services/notificationService';

export const useNotifications = (vapidKey) => {
  const [notifications, setNotifications] = useState([]);
  const [preferences, setPreferences] = useState([]);
  const [loading, setLoading] = useState(false);

  // Registrar dispositivo al montar
  useEffect(() => {
    const registerDevice = async () => {
      try {
        await notificationService.registerDevice(vapidKey);
      } catch (error) {
        console.error('Failed to register device:', error);
      }
    };

    if (vapidKey) {
      registerDevice();
    }
  }, [vapidKey]);

  // Escuchar mensajes en foreground
  useEffect(() => {
    const unsubscribe = onMessage(messaging, (payload) => {
      console.log('Message received:', payload);

      // Mostrar notificación del navegador
      if (Notification.permission === 'granted') {
        new Notification(payload.notification.title, {
          body: payload.notification.body,
          icon: '/icon.png'
        });
      }

      // Recargar notificaciones
      loadNotifications();
    });

    return () => unsubscribe();
  }, []);

  const loadNotifications = async (page = 1, filters = {}) => {
    setLoading(true);
    try {
      const data = await notificationService.getNotifications(page, filters);
      setNotifications(prev => page === 1 ? data.results : [...prev, ...data.results]);
      return data;
    } catch (error) {
      console.error('Failed to load notifications:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const loadPreferences = async () => {
    try {
      const data = await notificationService.getPreferences();
      setPreferences(data);
      return data;
    } catch (error) {
      console.error('Failed to load preferences:', error);
      throw error;
    }
  };

  const updatePreferences = async (newPreferences) => {
    try {
      await notificationService.updatePreferences(newPreferences);
      await loadPreferences(); // Recargar preferencias
    } catch (error) {
      console.error('Failed to update preferences:', error);
      throw error;
    }
  };

  const markAsRead = async (notificationId) => {
    try {
      await notificationService.markAsRead(notificationId);
      // Actualizar estado local
      setNotifications(prev =>
        prev.map(notif =>
          notif.id === notificationId
            ? { ...notif, estado: 'leida', fecha_lectura: new Date().toISOString() }
            : notif
        )
      );
    } catch (error) {
      console.error('Failed to mark as read:', error);
      throw error;
    }
  };

  const markAllAsRead = async () => {
    try {
      await notificationService.markAllAsRead();
      // Actualizar estado local
      setNotifications(prev =>
        prev.map(notif => ({
          ...notif,
          estado: 'leida',
          fecha_lectura: notif.fecha_lectura || new Date().toISOString()
        }))
      );
    } catch (error) {
      console.error('Failed to mark all as read:', error);
      throw error;
    }
  };

  return {
    notifications,
    preferences,
    loading,
    loadNotifications,
    loadPreferences,
    updatePreferences,
    markAsRead,
    markAllAsRead
  };
};
```

### Componente de Notificaciones:
```jsx
// src/components/Notifications.jsx
import React, { useEffect, useState } from 'react';
import { useNotifications } from '../hooks/useNotifications';

const Notifications = ({ vapidKey }) => {
  const {
    notifications,
    preferences,
    loading,
    loadNotifications,
    loadPreferences,
    updatePreferences,
    markAsRead,
    markAllAsRead
  } = useNotifications(vapidKey);

  const [activeTab, setActiveTab] = useState('notifications');

  useEffect(() => {
    loadNotifications();
    loadPreferences();
  }, []);

  const handleMarkAsRead = async (notificationId) => {
    try {
      await markAsRead(notificationId);
    } catch (error) {
      alert('Error al marcar como leída');
    }
  };

  const handleMarkAllAsRead = async () => {
    try {
      await markAllAsRead();
    } catch (error) {
      alert('Error al marcar todas como leídas');
    }
  };

  const handlePreferenceChange = async (tipo, channel, value) => {
    const updatedPreferences = preferences.map(pref =>
      pref.tipo_notificacion === tipo
        ? { ...pref, [channel]: value }
        : pref
    );

    try {
      await updatePreferences(updatedPreferences);
    } catch (error) {
      alert('Error al actualizar preferencias');
    }
  };

  if (loading && notifications.length === 0) {
    return <div>Cargando...</div>;
  }

  return (
    <div className="notifications-container">
      <div className="tabs">
        <button
          className={activeTab === 'notifications' ? 'active' : ''}
          onClick={() => setActiveTab('notifications')}
        >
          Notificaciones ({notifications.filter(n => n.estado !== 'leida').length})
        </button>
        <button
          className={activeTab === 'preferences' ? 'active' : ''}
          onClick={() => setActiveTab('preferences')}
        >
          Preferencias
        </button>
      </div>

      {activeTab === 'notifications' && (
        <div className="notifications-list">
          <div className="actions">
            <button onClick={handleMarkAllAsRead}>
              Marcar todas como leídas
            </button>
          </div>

          {notifications.map(notification => (
            <div
              key={notification.id}
              className={`notification ${notification.estado === 'leida' ? 'read' : 'unread'}`}
            >
              <div className="notification-header">
                <h4>{notification.titulo}</h4>
                <span className={`priority priority-${notification.prioridad}`}>
                  Prioridad {notification.prioridad}
                </span>
              </div>
              <p>{notification.mensaje}</p>
              <div className="notification-footer">
                <small>{new Date(notification.fecha_creacion).toLocaleString()}</small>
                {notification.estado !== 'leida' && (
                  <button onClick={() => handleMarkAsRead(notification.id)}>
                    Marcar como leída
                  </button>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {activeTab === 'preferences' && (
        <div className="preferences-list">
          {preferences.map(pref => (
            <div key={pref.id} className="preference-item">
              <h4>{pref.tipo_notificacion.replace('_', ' ').toUpperCase()}</h4>
              <div className="channels">
                <label>
                  <input
                    type="checkbox"
                    checked={pref.push_enabled}
                    onChange={(e) => handlePreferenceChange(pref.tipo_notificacion, 'push_enabled', e.target.checked)}
                  />
                  Push
                </label>
                <label>
                  <input
                    type="checkbox"
                    checked={pref.email_enabled}
                    onChange={(e) => handlePreferenceChange(pref.tipo_notificacion, 'email_enabled', e.target.checked)}
                  />
                  Email
                </label>
                <label>
                  <input
                    type="checkbox"
                    checked={pref.sms_enabled}
                    onChange={(e) => handlePreferenceChange(pref.tipo_notificacion, 'sms_enabled', e.target.checked)}
                  />
                  SMS
                </label>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default Notifications;
```

---

## Flutter Integration

### Dependencias en pubspec.yaml:
```yaml
dependencies:
  firebase_messaging: ^14.6.0
  http: ^1.1.0
  provider: ^6.0.5
```

### Configuración Firebase:
```dart
// lib/main.dart
import 'package:firebase_messaging/firebase_messaging.dart';
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  await Firebase.initializeApp();

  // Configurar Firebase Messaging
  FirebaseMessaging messaging = FirebaseMessaging.instance;

  // Solicitar permisos
  NotificationSettings settings = await messaging.requestPermission(
    alert: true,
    badge: true,
    sound: true,
  );

  runApp(
    MultiProvider(
      providers: [
        ChangeNotifierProvider(create: (_) => NotificationProvider()),
      ],
      child: MyApp(),
    ),
  );
}
```

### Modelo de Notificación:
```dart
// lib/models/notification.dart
class AppNotification {
  final int id;
  final String titulo;
  final String mensaje;
  final String tipo;
  final String estado;
  final int prioridad;
  final DateTime fechaCreacion;
  final DateTime? fechaEnvio;
  final DateTime? fechaLectura;
  final Map<String, dynamic>? datosExtra;

  AppNotification({
    required this.id,
    required this.titulo,
    required this.mensaje,
    required this.tipo,
    required this.estado,
    required this.prioridad,
    required this.fechaCreacion,
    this.fechaEnvio,
    this.fechaLectura,
    this.datosExtra,
  });

  factory AppNotification.fromJson(Map<String, dynamic> json) {
    return AppNotification(
      id: json['id'],
      titulo: json['titulo'],
      mensaje: json['mensaje'],
      tipo: json['tipo'],
      estado: json['estado'],
      prioridad: json['prioridad'],
      fechaCreacion: DateTime.parse(json['fecha_creacion']),
      fechaEnvio: json['fecha_envio'] != null ? DateTime.parse(json['fecha_envio']) : null,
      fechaLectura: json['fecha_lectura'] != null ? DateTime.parse(json['fecha_lectura']) : null,
      datosExtra: json['datos_extra'],
    );
  }
}
```

### Servicio de Notificaciones:
```dart
// lib/services/notification_service.dart
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:firebase_messaging/firebase_messaging.dart';
import '../models/notification.dart';

class NotificationService {
  final String baseUrl;
  final String? authToken;

  NotificationService({required this.baseUrl, this.authToken});

  Future<String?> getToken() async {
    return await FirebaseMessaging.instance.getToken();
  }

  Future<void> registerDevice(String token, String tipoDispositivo) async {
    final response = await http.post(
      Uri.parse('$baseUrl/api/notificaciones/dispositivos/'),
      headers: {
        'Content-Type': 'application/json',
        if (authToken != null) 'Authorization': 'Bearer $authToken',
      },
      body: jsonEncode({
        'token_push': token,
        'tipo_dispositivo': tipoDispositivo,
        'nombre_dispositivo': 'Device Model', // Puedes obtener el modelo real
      }),
    );

    if (response.statusCode != 201) {
      throw Exception('Failed to register device');
    }
  }

  Future<List<AppNotification>> getNotifications({
    int page = 1,
    String? estado,
    String? tipo,
  }) async {
    final queryParams = {
      'page': page.toString(),
      if (estado != null) 'estado': estado,
      if (tipo != null) 'tipo': tipo,
    };

    final uri = Uri.parse('$baseUrl/api/notificaciones/').replace(queryParameters: queryParams);

    final response = await http.get(
      uri,
      headers: {
        if (authToken != null) 'Authorization': 'Bearer $authToken',
      },
    );

    if (response.statusCode == 200) {
      final data = jsonDecode(response.body);
      return (data['results'] as List)
          .map((json) => AppNotification.fromJson(json))
          .toList();
    } else {
      throw Exception('Failed to load notifications');
    }
  }

  Future<void> markAsRead(int notificationId) async {
    final response = await http.patch(
      Uri.parse('$baseUrl/api/notificaciones/$notificationId/marcar-leida/'),
      headers: {
        'Content-Type': 'application/json',
        if (authToken != null) 'Authorization': 'Bearer $authToken',
      },
    );

    if (response.statusCode != 200) {
      throw Exception('Failed to mark as read');
    }
  }

  Future<void> markAllAsRead() async {
    final response = await http.patch(
      Uri.parse('$baseUrl/api/notificaciones/marcar-todas-leidas/'),
      headers: {
        if (authToken != null) 'Authorization': 'Bearer $authToken',
      },
    );

    if (response.statusCode != 200) {
      throw Exception('Failed to mark all as read');
    }
  }
}
```

### Provider de Notificaciones:
```dart
// lib/providers/notification_provider.dart
import 'package:flutter/foundation.dart';
import '../models/notification.dart';
import '../services/notification_service.dart';

class NotificationProvider with ChangeNotifier {
  final NotificationService _service;
  List<AppNotification> _notifications = [];
  bool _loading = false;

  NotificationProvider() : _service = NotificationService(baseUrl: 'YOUR_API_BASE_URL');

  void setAuthToken(String token) {
    // Actualizar el servicio con el nuevo token
  }

  List<AppNotification> get notifications => _notifications;
  bool get loading => _loading;

  int get unreadCount => _notifications.where((n) => n.estado != 'leida').length;

  Future<void> loadNotifications({
    int page = 1,
    String? estado,
    String? tipo,
    bool append = false,
  }) async {
    _loading = true;
    notifyListeners();

    try {
      final newNotifications = await _service.getNotifications(
        page: page,
        estado: estado,
        tipo: tipo,
      );

      if (append) {
        _notifications.addAll(newNotifications);
      } else {
        _notifications = newNotifications;
      }
    } catch (error) {
      debugPrint('Error loading notifications: $error');
    } finally {
      _loading = false;
      notifyListeners();
    }
  }

  Future<void> markAsRead(int notificationId) async {
    try {
      await _service.markAsRead(notificationId);

      final index = _notifications.indexWhere((n) => n.id == notificationId);
      if (index != -1) {
        _notifications[index] = AppNotification(
          id: _notifications[index].id,
          titulo: _notifications[index].titulo,
          mensaje: _notifications[index].mensaje,
          tipo: _notifications[index].tipo,
          estado: 'leida',
          prioridad: _notifications[index].prioridad,
          fechaCreacion: _notifications[index].fechaCreacion,
          fechaEnvio: _notifications[index].fechaEnvio,
          fechaLectura: DateTime.now(),
          datosExtra: _notifications[index].datosExtra,
        );
        notifyListeners();
      }
    } catch (error) {
      debugPrint('Error marking as read: $error');
      throw error;
    }
  }

  Future<void> markAllAsRead() async {
    try {
      await _service.markAllAsRead();

      _notifications = _notifications.map((notification) {
        if (notification.estado != 'leida') {
          return AppNotification(
            id: notification.id,
            titulo: notification.titulo,
            mensaje: notification.mensaje,
            tipo: notification.tipo,
            estado: 'leida',
            prioridad: notification.prioridad,
            fechaCreacion: notification.fechaCreacion,
            fechaEnvio: notification.fechaEnvio,
            fechaLectura: DateTime.now(),
            datosExtra: notification.datosExtra,
          );
        }
        return notification;
      }).toList();

      notifyListeners();
    } catch (error) {
      debugPrint('Error marking all as read: $error');
      throw error;
    }
  }
}
```

### Widget de Notificaciones:
```dart
// lib/widgets/notifications_list.dart
import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../providers/notification_provider.dart';
import '../models/notification.dart';

class NotificationsList extends StatefulWidget {
  @override
  _NotificationsListState createState() => _NotificationsListState();
}

class _NotificationsListState extends State<NotificationsList> {
  final ScrollController _scrollController = ScrollController();
  int _currentPage = 1;

  @override
  void initState() {
    super.initState();
    _loadNotifications();

    _scrollController.addListener(() {
      if (_scrollController.position.pixels == _scrollController.position.maxScrollExtent) {
        _loadMoreNotifications();
      }
    });
  }

  @override
  void dispose() {
    _scrollController.dispose();
    super.dispose();
  }

  void _loadNotifications() {
    context.read<NotificationProvider>().loadNotifications(page: 1);
  }

  void _loadMoreNotifications() {
    _currentPage++;
    context.read<NotificationProvider>().loadNotifications(
      page: _currentPage,
      append: true,
    );
  }

  @override
  Widget build(BuildContext context) {
    return Consumer<NotificationProvider>(
      builder: (context, provider, child) {
        if (provider.loading && provider.notifications.isEmpty) {
          return Center(child: CircularProgressIndicator());
        }

        return RefreshIndicator(
          onRefresh: () async {
            _currentPage = 1;
            await provider.loadNotifications(page: 1);
          },
          child: ListView.builder(
            controller: _scrollController,
            itemCount: provider.notifications.length + (provider.loading ? 1 : 0),
            itemBuilder: (context, index) {
              if (index == provider.notifications.length) {
                return Center(child: CircularProgressIndicator());
              }

              final notification = provider.notifications[index];
              return NotificationCard(
                notification: notification,
                onMarkAsRead: () => provider.markAsRead(notification.id),
              );
            },
          ),
        );
      },
    );
  }
}

class NotificationCard extends StatelessWidget {
  final AppNotification notification;
  final VoidCallback onMarkAsRead;

  const NotificationCard({
    Key? key,
    required this.notification,
    required this.onMarkAsRead,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: Padding(
        padding: EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    notification.titulo,
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                Container(
                  padding: EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  decoration: BoxDecoration(
                    color: _getPriorityColor(notification.prioridad),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Text(
                    'P${notification.prioridad}',
                    style: TextStyle(color: Colors.white, fontSize: 12),
                  ),
                ),
              ],
            ),
            SizedBox(height: 8),
            Text(notification.mensaje),
            SizedBox(height: 8),
            Row(
              children: [
                Text(
                  _formatDate(notification.fechaCreacion),
                  style: TextStyle(color: Colors.grey, fontSize: 12),
                ),
                Spacer(),
                if (notification.estado != 'leida')
                  TextButton(
                    onPressed: onMarkAsRead,
                    child: Text('Marcar como leída'),
                  ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Color _getPriorityColor(int priority) {
    switch (priority) {
      case 1:
        return Colors.grey;
      case 2:
        return Colors.blue;
      case 3:
        return Colors.orange;
      case 4:
        return Colors.red;
      case 5:
        return Colors.red.shade900;
      default:
        return Colors.grey;
    }
  }

  String _formatDate(DateTime date) {
    return '${date.day}/${date.month}/${date.year} ${date.hour}:${date.minute.toString().padLeft(2, '0')}';
  }
}
```

### Inicialización en App:
```dart
// En tu widget principal
@override
void initState() {
  super.initState();

  // Configurar Firebase Messaging
  FirebaseMessaging.instance.getToken().then((token) {
    if (token != null) {
      // Registrar dispositivo
      context.read<NotificationProvider>()._service.registerDevice(
        token,
        Platform.isAndroid ? 'android' : 'ios',
      );
    }
  });

  // Listener para mensajes en foreground
  FirebaseMessaging.onMessage.listen((RemoteMessage message) {
    // Mostrar notificación local o actualizar lista
    context.read<NotificationProvider>().loadNotifications();
  });

  // Listener para notificaciones cuando la app está en background
  FirebaseMessaging.onMessageOpenedApp.listen((RemoteMessage message) {
    // Navegar a la pantalla de notificaciones
    Navigator.pushNamed(context, '/notifications');
  });
}
```

---

## Configuración de Firebase

### Para React:
1. Crear proyecto en Firebase Console
2. Habilitar Firebase Cloud Messaging
3. Obtener las claves de configuración
4. Configurar VAPID keys para Web Push

### Para Flutter:
1. Crear proyecto en Firebase Console
2. Agregar app Android/iOS
3. Descargar google-services.json (Android) / GoogleService-Info.plist (iOS)
4. Configurar en el proyecto Flutter

### Variables de Entorno Necesarias:
```env
# Firebase
FIREBASE_API_KEY=your_api_key
FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
FIREBASE_PROJECT_ID=your_project_id
FIREBASE_MESSAGING_SENDER_ID=123456789
FIREBASE_APP_ID=your_app_id

# VAPID para Web Push
VAPID_PUBLIC_KEY=your_vapid_public_key
VAPID_PRIVATE_KEY=your_vapid_private_key
```