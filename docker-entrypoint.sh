#!/bin/bash

# Debug: Mostrar variables de entorno
echo "🔍 DEBUG: Variables de entorno disponibles:"
echo "DATABASE_URL: $DATABASE_URL"
echo "DB_HOST: $DB_HOST"
echo "DB_NAME: $DB_NAME"
echo "DB_USER: $DB_USER"
echo "SECRET_KEY existe: $([ -n "$SECRET_KEY" ] && echo "✅ SÍ" || echo "❌ NO")"
echo "DEBUG: $DEBUG"
echo "ALLOWED_HOSTS: $ALLOWED_HOSTS"
echo "----------------------------------------"

# Esperar a que PostgreSQL esté disponible
echo "Esperando a que PostgreSQL esté disponible..."

# Función para parsear DATABASE_URL si existe
if [ -n "$DATABASE_URL" ]; then
    echo "✅ Usando DATABASE_URL para conexión..."
    python -c "
import os
import time
import sys
from urllib.parse import urlparse

database_url = os.environ.get('DATABASE_URL')
if database_url:
    url = urlparse(database_url)
    db_host = url.hostname
    db_port = url.port or 5432
    db_name = url.path[1:]  # Remove leading slash
    db_user = url.username
    db_password = url.password
else:
    db_host = os.environ.get('DB_HOST', 'localhost')
    db_port = os.environ.get('DB_PORT', '5432')
    db_name = os.environ.get('DB_NAME', 'Smart_Condominium')
    db_user = os.environ.get('DB_USER', 'postgres')
    db_password = os.environ.get('DB_PASSWORD', '123456')

print(f'Conectando a: {db_host}:{db_port}/{db_name}')

import psycopg2

max_retries = 30
retry_count = 0

while retry_count < max_retries:
    try:
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password
        )
        conn.close()
        print('PostgreSQL está listo!')
        sys.exit(0)
    except psycopg2.OperationalError as e:
        retry_count += 1
        print(f'PostgreSQL no está listo - intento {retry_count}/{max_retries}')
        print(f'Error: {e}')
        time.sleep(2)

print('No se pudo conectar a PostgreSQL después de todos los intentos')
sys.exit(1)
"
else
    echo "❌ DATABASE_URL no encontrada, usando variables individuales..."
    echo "🔍 Verificando variables individuales:"
    echo "DB_HOST: $DB_HOST"
    echo "DB_PORT: $DB_PORT"  
    echo "DB_NAME: $DB_NAME"
    echo "DB_USER: $DB_USER"
    echo "DB_PASSWORD existe: $([ -n "$DB_PASSWORD" ] && echo "✅ SÍ" || echo "❌ NO")"
    python -c "
import psycopg2
import time
import os
import sys

db_host = os.environ.get('DB_HOST', 'localhost')
db_port = os.environ.get('DB_PORT', '5432')
db_name = os.environ.get('DB_NAME', 'Smart_Condominium')
db_user = os.environ.get('DB_USER', 'postgres')
db_password = os.environ.get('DB_PASSWORD', '123456')

print(f'Conectando a: {db_host}:{db_port}/{db_name}')

max_retries = 30
retry_count = 0

while retry_count < max_retries:
    try:
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password
        )
        conn.close()
        print('PostgreSQL está listo!')
        sys.exit(0)
    except psycopg2.OperationalError as e:
        retry_count += 1
        print(f'PostgreSQL no está listo - intento {retry_count}/{max_retries}')
        print(f'Error: {e}')
        time.sleep(2)

print('No se pudo conectar a PostgreSQL después de todos los intentos')
sys.exit(1)
"
fi

# Ejecutar migraciones
echo "Aplicando migraciones..."
python manage.py makemigrations
python manage.py migrate

# Crear superusuario si no existe
echo "Creando superusuario..."
python manage.py shell -c "
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@admin.com', 'clave123')
    print('Superusuario creado: admin / clave123')
else:
    print('Superusuario ya existe')
"

# Recolectar archivos estáticos
echo "Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

echo "Inicialización completada!"

# Ejecutar el comando pasado como argumento
exec "$@"