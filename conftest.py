"""
Configuración de Testing para Django.
"""

import os
from pathlib import Path

# Build paths
BASE_DIR = Path(__file__).resolve().parent

# Testing database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',  # Base de datos en memoria para tests
    }
}

# Keep other settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mi_proyecto.settings')

# Email backend para testing
EMAIL_BACKEND = 'django.core.mail.backends.locmem.EmailBackend'
