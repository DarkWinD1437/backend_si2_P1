#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

# Configurar variables de entorno para eliminar advertencias de TensorFlow
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # Solo mostrar errores, no warnings
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'  # Desactivar oneDNN optimizations warnings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'backend.settings')


def main():
    """Run administrative tasks."""
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
