#!/bin/bash
# Build script para Render

set -o errexit

pip install -r requirements.txt

python manage.py migrate
python manage.py collectstatic --noinput

# Crear superusuario
python manage.py shell -c "
from django.contrib.auth import get_user_model
import os
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@admin.com', os.environ.get('ADMIN_PASSWORD', 'clave123'))
    print('Superusuario creado')
"