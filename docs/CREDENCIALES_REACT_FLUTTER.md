📋 CREDENCIALES PARA REACT-VITE Y FLUTTER
==============================================

🔑 USUARIOS DE PRUEBA:

1. ADMINISTRADOR:
   - Username: admin_smart
   - Password: admin123
   - Email: admin@smartcondominium.com
   - Rol: Administrador

2. RESIDENTE 1:
   - Username: carlos
   - Password: password123
   - Email: carlos.rodriguez@email.com
   - Rol: Residente

3. RESIDENTE 2:
   - Username: maria
   - Password: password123
   - Email: maria.gonzalez@email.com
   - Rol: Residente

4. SEGURIDAD:
   - Username: seguridad
   - Password: security123
   - Email: jorge.flores@email.com
   - Rol: Seguridad

5. SUPERUSUARIO (Django Admin):
   - Username: admin
   - Password: (la que configuraste)
   - Email: admin@correo.com

🔗 URLS IMPORTANTES:
- API Base: http://127.0.0.1:8000/api/
- Django Admin: http://127.0.0.1:8000/admin/
- Login API: http://127.0.0.1:8000/api/login/
- User Profile: http://127.0.0.1:8000/api/me/

📝 EJEMPLO DE PETICIÓN LOGIN (React/Flutter):
```javascript
// JavaScript/React
fetch('http://127.0.0.1:8000/api/login/', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    username: 'admin_smart',
    password: 'admin123'
  })
})
.then(response => response.json())
.then(data => {
  console.log('Token:', data.token);
  localStorage.setItem('auth-token', data.token);
});
```

```dart
// Flutter/Dart
import 'dart:convert';
import 'package:http/http.dart' as http;

Future<String> login(String username, String password) async {
  final response = await http.post(
    Uri.parse('http://127.0.0.1:8000/api/login/'),
    headers: {'Content-Type': 'application/json'},
    body: jsonEncode({
      'username': username,
      'password': password,
    }),
  );
  
  if (response.statusCode == 200) {
    final data = jsonDecode(response.body);
    return data['token'];
  }
  throw Exception('Login failed');
}
```

🛡️ EJEMPLO DE PETICIÓN AUTENTICADA:
```javascript
// Con el token obtenido
fetch('http://127.0.0.1:8000/api/me/', {
  method: 'GET',
  headers: {
    'Authorization': 'Token ' + token,
    'Content-Type': 'application/json',
  }
})
```
