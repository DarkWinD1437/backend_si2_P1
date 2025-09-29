#!/usr/bin/env python
"""
Script de inicio limpio para el backend Django
Elimina advertencias innecesarias de TensorFlow y otras librerías
"""
import os
import sys
import warnings

# Configurar variables de entorno para TensorFlow
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # Solo errores fatales
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'  # Desactivar oneDNN warnings

# Suprimir warnings específicos antes de cualquier importación
warnings.filterwarnings('ignore', category=UserWarning, module='rest_framework_simplejwt')
warnings.filterwarnings('ignore', category=DeprecationWarning, module='pkg_resources')
warnings.filterwarnings('ignore', category=UserWarning, message='.*pkg_resources.*')
warnings.filterwarnings('ignore', category=DeprecationWarning, message='.*pkg_resources.*')
warnings.filterwarnings('ignore', category=UserWarning, message='.*deprecated.*')
warnings.filterwarnings('ignore', category=DeprecationWarning, message='.*deprecated.*')

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')

# Ejecutar Django
try:
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)
except ImportError as exc:
    raise ImportError(
        "Couldn't import Django. Are you sure it's installed and "
        "available on your PYTHONPATH environment variable? Did you "
        "forget to activate a virtual environment?"
    ) from exc