"""
Archivo de configuración para pytest en el módulo analytics
"""

import os
import django
from django.conf import settings

# Configurar Django para los tests
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# Inicializar Django
django.setup()

# Configuración de pytest
pytest_plugins = [
    "pytest_django",
]

# Configuración de Django para pytest
def pytest_configure():
    settings.configure(
        DEBUG=True,
        DATABASES={
            'default': {
                'ENGINE': 'django.db.backends.sqlite3',
                'NAME': ':memory:',
            }
        },
        INSTALLED_APPS=[
            'django.contrib.auth',
            'django.contrib.contenttypes',
            'django.contrib.sessions',
            'django.contrib.messages',
            'rest_framework',
            'backend.apps.analytics',
            'backend.apps.users',
            'backend.apps.audit',
            'backend.apps.communications',
            'backend.apps.condominio',
            'backend.apps.finances',
            'backend.apps.maintenance',
            'backend.apps.modulo_ia',
            'backend.apps.api',
        ],
        SECRET_KEY='test-secret-key-for-analytics-module',
        USE_TZ=True,
        REST_FRAMEWORK={
            'DEFAULT_AUTHENTICATION_CLASSES': [
                'rest_framework.authentication.SessionAuthentication',
                'rest_framework.authentication.BasicAuthentication',
            ],
            'DEFAULT_PERMISSION_CLASSES': [
                'rest_framework.permissions.IsAuthenticated',
            ],
        },
        MIDDLEWARE=[
            'django.middleware.security.SecurityMiddleware',
            'django.contrib.sessions.middleware.SessionMiddleware',
            'django.middleware.common.CommonMiddleware',
            'django.middleware.csrf.CsrfViewMiddleware',
            'django.contrib.auth.middleware.AuthenticationMiddleware',
            'django.contrib.messages.middleware.MessageMiddleware',
        ],
    )