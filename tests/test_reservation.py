import os
os.chdir('c:/Users/PG/Desktop/Materias/Sistemas de informacion 2/Proyectos/Parcial 1/Backend_Django')
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')
django.setup()

from django.test import Client
from django.contrib.auth import get_user_model
import json

# Create test client
client = Client()

# Login
User = get_user_model()
try:
    user = User.objects.get(username='admin')
    client.force_login(user)
    print('User logged in successfully')

    # Test reservation
    from datetime import datetime, timedelta
    tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    data = {
        'fecha': tomorrow,
        'hora_inicio': '14:00',
        'hora_fin': '16:00',
        'numero_personas': 5,
        'observaciones': 'Test reservation'
    }

    response = client.post('/api/reservations/areas/4/reservar/',
                          data=json.dumps(data),
                          content_type='application/json')

    print(f'Status: {response.status_code}')
    print(f'Response: {response.content.decode()}')

except Exception as e:
    print(f'Error: {e}')
    import traceback
    traceback.print_exc()