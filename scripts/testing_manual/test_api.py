import requests
import json

def test_api():
    # URL base
    base_url = "http://127.0.0.1:8000/api/"
    
    print("🧪 PROBANDO APIs DEL BACKEND")
    print("=" * 40)
    
    # 1. Probar Login
    print("🔐 Probando Login API...")
    login_url = f"{base_url}login/"
    
    # Credenciales de prueba
    credentials = [
        {"username": "admin", "password": "clave123"},  # Admin funcional corregido
        {"username": "carlos", "password": "password123"},
        {"username": "maria", "password": "password123"},
        {"username": "seguridad", "password": "security123"}
    ]
    
    tokens = {}
    
    for cred in credentials:
        try:
            response = requests.post(login_url, json=cred, timeout=5)
            print(f"  👤 Usuario: {cred['username']}")
            print(f"  📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                tokens[cred['username']] = data.get('token')
                print(f"  ✅ Login exitoso - Token: {data.get('token')[:20]}...")
                print(f"  📧 User ID: {data.get('user_id')}, Superuser: {data.get('is_superuser')}")
            else:
                print(f"  ❌ Error: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"  💥 Error de conexión: {e}")
            
        print("-" * 30)
    
    # 2. Probar endpoint /me/ con token
    if tokens:
        print("\n👤 Probando API /me/ (perfil usuario)...")
        me_url = f"{base_url}me/"
        
        # Usar el primer token disponible
        first_user = list(tokens.keys())[0]
        token = tokens[first_user]
        
        headers = {
            'Authorization': f'Token {token}',
            'Content-Type': 'application/json'
        }
        
        try:
            response = requests.get(me_url, headers=headers, timeout=5)
            print(f"  📊 Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"  ✅ Perfil obtenido:")
                print(f"    ID: {data.get('id')}")
                print(f"    Username: {data.get('username')}")
                print(f"    Email: {data.get('email')}")
                print(f"    Nombre: {data.get('first_name')} {data.get('last_name')}")
                print(f"    Rol: {data.get('role')}")
            else:
                print(f"  ❌ Error: {response.text}")
                
        except requests.exceptions.RequestException as e:
            print(f"  💥 Error de conexión: {e}")
    
    print("\n" + "=" * 40)
    print("✅ BACKEND LISTO PARA REACT-VITE Y FLUTTER")
    print("📖 Ver archivo CREDENCIALES_REACT_FLUTTER.md para detalles")

if __name__ == "__main__":
    test_api()
