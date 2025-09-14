#!/bin/bash
# Script de deployment para Railway

echo "🚀 Iniciando deployment..."

# Aplicar migraciones
echo "📦 Aplicando migraciones..."
python manage.py migrate --noinput

# Crear superusuario si no existe
echo "👤 Creando superusuario..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
import os
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@admin.com', os.environ.get('ADMIN_PASSWORD', 'clave123'))
    print('✅ Superusuario creado')
else:
    print('ℹ️  Superusuario ya existe')
"

# Recolectar archivos estáticos
echo "🎨 Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

echo "✅ Deployment completado!"