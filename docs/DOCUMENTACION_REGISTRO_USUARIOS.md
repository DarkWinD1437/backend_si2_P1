# 📋 DOCUMENTACIÓN API - MÓDULO 1: GESTIÓN DE USUARIOS Y AUTENTICACIÓN

## ✅ ESTADO DEL BACKEND
- **Estado**: ✅ LISTO PARA PRODUCCIÓN
- **Servidor**: http://localhost:8000
- **Compatible con**: React ✅ | Flutter ✅

---

## 🔐 T1: REGISTRAR USUARIO

### Endpoint Principal
```
POST /api/register/
Content-Type: application/json
```

### Datos Requeridos
```json
{
  "username": "string (único)",
  "email": "string (único, formato email)",
  "password": "string (mínimo 8 caracteres)",
  "password_confirm": "string (debe coincidir con password)",
  "first_name": "string",
  "last_name": "string",
  "role": "resident | admin | security",
  "phone": "string (opcional)",
  "address": "string (opcional)"
}
```

### Respuesta Exitosa (201)
```json
{
  "success": true,
  "message": "Usuario registrado exitosamente",
  "user": {
    "id": 7,
    "username": "user_20250911_140726",
    "email": "user_20250911_140726@example.com",
    "first_name": "Usuario",
    "last_name": "Prueba",
    "role": "resident"
  },
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token": "9944b09199c62bcf9418ad846dd0e4bbdfc6ee4b"
  }
}
```

### Respuesta Error (400)
```json
{
  "success": false,
  "message": "Error en el registro",
  "errors": {
    "username": ["A user with that username already exists."],
    "email": ["Este email ya está registrado"],
    "password": ["This password is too short."]
  }
}
```

---

## 🚀 EJEMPLOS DE IMPLEMENTACIÓN

### Para React (JavaScript/TypeScript)
```javascript
const registerUser = async (userData) => {
  try {
    const response = await fetch('http://localhost:8000/api/register/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData)
    });
    
    const data = await response.json();
    
    if (response.ok) {
      // Guardar tokens en localStorage o context
      localStorage.setItem('access_token', data.tokens.access);
      localStorage.setItem('refresh_token', data.tokens.refresh);
      localStorage.setItem('auth_token', data.tokens.token);
      
      console.log('Usuario registrado:', data.user);
      return { success: true, user: data.user };
    } else {
      console.error('Errores de validación:', data.errors);
      return { success: false, errors: data.errors };
    }
  } catch (error) {
    console.error('Error de conexión:', error);
    return { success: false, error: 'Error de conexión' };
  }
};

// Ejemplo de uso
const userData = {
  username: "nuevo_usuario",
  email: "usuario@example.com",
  password: "mipassword123",
  password_confirm: "mipassword123",
  first_name: "Juan",
  last_name: "Pérez",
  role: "resident",
  phone: "+1234567890",
  address: "Apt 101, Torre A"
};

registerUser(userData);
```

### Para Flutter (Dart)
```dart
import 'dart:convert';
import 'package:http/http.dart' as http;

class AuthService {
  static const String baseUrl = 'http://localhost:8000/api';
  
  Future<Map<String, dynamic>> registerUser(Map<String, dynamic> userData) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/register/'),
        headers: {
          'Content-Type': 'application/json',
        },
        body: jsonEncode(userData),
      );
      
      final data = jsonDecode(response.body);
      
      if (response.statusCode == 201) {
        // Guardar tokens en SharedPreferences
        // await saveTokens(data['tokens']);
        
        print('Usuario registrado: ${data['user']}');
        return {'success': true, 'user': data['user']};
      } else {
        print('Errores de validación: ${data['errors']}');
        return {'success': false, 'errors': data['errors']};
      }
    } catch (e) {
      print('Error de conexión: $e');
      return {'success': false, 'error': 'Error de conexión'};
    }
  }
}

// Ejemplo de uso
final authService = AuthService();

final userData = {
  'username': 'nuevo_usuario',
  'email': 'usuario@example.com',
  'password': 'mipassword123',
  'password_confirm': 'mipassword123',
  'first_name': 'Juan',
  'last_name': 'Pérez',
  'role': 'resident',
  'phone': '+1234567890',
  'address': 'Apt 101, Torre A',
};

final result = await authService.registerUser(userData);
```

---

## 🔑 ENDPOINTS ADICIONALES DISPONIBLES

### 1. Login JWT
```
POST /api/token/
{
  "username": "string",
  "password": "string"
}
```

### 2. Refresh Token
```
POST /api/token/refresh/
{
  "refresh": "refresh_token_aquí"
}
```

### 3. Perfil Usuario
```
GET /api/users/me/
Authorization: Bearer access_token_aquí
```

### 4. Status API
```
GET /api/status/
```

---

## ✨ CARACTERÍSTICAS IMPLEMENTADAS

- ✅ Registro de usuarios con validación completa
- ✅ Autenticación JWT (access + refresh tokens)
- ✅ Autenticación por Token (compatible con DRF)
- ✅ Validación de campos únicos (username, email)
- ✅ Validación de contraseñas coincidentes
- ✅ Roles de usuario (admin, resident, security)
- ✅ CORS configurado para React y Flutter
- ✅ Respuestas JSON consistentes
- ✅ Manejo de errores detallado

---

## 🛠️ CONFIGURACIÓN CORS

El backend está configurado para aceptar requests desde:
- `http://localhost:3000` (React)
- `http://localhost:5173` (Vite)
- `http://localhost:5174` (Vite alternativo)
- `http://localhost:8080` (Flutter web)

---

## 📝 NOTAS IMPORTANTES

1. **Tokens**: El endpoint devuelve 3 tipos de tokens para máxima compatibilidad
2. **Validación**: Todos los campos se validan en el servidor
3. **Unicidad**: Username y email deben ser únicos
4. **Roles**: Por defecto se asigna rol 'resident'
5. **HTTPS**: En producción, cambiar a HTTPS

---

## 🎯 SIGUIENTE PASO

El **Módulo 1: Gestión de Usuarios y Autenticación, T1: Registrar Usuario** está 100% funcional y listo para ser consumido tanto por React como por Flutter.
