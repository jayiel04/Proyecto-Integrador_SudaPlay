"""
Archivo de configuración centralizada para el proyecto.
Facilita cambios sin tocar settings.py
"""

# Configuración de la aplicación
APP_CONFIG = {
    'APP_NAME': 'Firegames',
    'APP_VERSION': '1.0.0',
    'APP_DESCRIPTION': 'Sistema de autenticación y gestión de usuarios',
    
    # URLs
    'LOGIN_REDIRECT_URL': '/',
    'LOGOUT_REDIRECT_URL': '/auth/login/',
    
    # Paginación
    'ITEMS_PER_PAGE': 25,
    
    # Sesiones
    'SESSION_TIMEOUT': 1800,  # 30 minutos
    
    # Límites
    'MAX_LOGIN_ATTEMPTS': 5,
    'LOCKOUT_TIME': 300,  # 5 minutos en segundos
}

# Configuración de seguridad adicional
SECURITY_CONFIG = {
    # CORS
    'ALLOWED_ORIGINS': [
        'http://localhost:3000',
        'http://localhost:8000',
    ],
    
    # Rate limiting
    'RATE_LIMIT_ENABLED': True,
    'RATE_LIMIT_REQUESTS': 100,  # requests
    'RATE_LIMIT_PERIOD': 3600,    # por hora
    
    # Validación de contraseña adicional
    'PASSWORD_MIN_LENGTH': 8,
    'REQUIRE_UPPERCASE': True,
    'REQUIRE_NUMBERS': True,
    'REQUIRE_SPECIAL': True,
}

# Configuración de email
EMAIL_CONFIG = {
    'SEND_EMAILS': True,
    'EMAIL_FROM': 'noreply@miproyecto.com',
    'VERIFICATION_EMAIL_TIMEOUT': 3600,  # 1 hora
    'PASSWORD_RESET_TIMEOUT': 3600,      # 1 hora
}

# Configuración de logging
LOGGING_CONFIG = {
    'LOG_LEVEL': 'INFO',
    'LOG_FORMAT': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'LOG_FILE': 'logs/django.log',
    'LOG_MAX_SIZE': 10485760,  # 10MB
    'LOG_BACKUP_COUNT': 5,
}

# Configuración de base de datos
DB_CONFIG = {
    'DEFAULT': 'sqlite',
    'DATABASES': {
        'sqlite': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': 'db.sqlite3',
        },
        'postgresql': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'mi_proyecto',
            'USER': 'postgres',
            'PASSWORD': 'password',
            'HOST': 'localhost',
            'PORT': '5432',
        },
    }
}

# Configuración de archivos
FILE_CONFIG = {
    'MAX_FILE_SIZE': 10485760,  # 10MB
    'ALLOWED_EXTENSIONS': ['jpg', 'jpeg', 'png', 'pdf', 'docx'],
    'UPLOAD_PATH': 'media/',
    'STATIC_PATH': 'static/',
}

# Configuración por ambiente
ENVIRONMENTS = {
    'development': {
        'DEBUG': True,
        'ALLOWED_HOSTS': ['localhost', '127.0.0.1'],
        'DATABASE': 'sqlite',
        'CACHE': 'locmem',
    },
    'production': {
        'DEBUG': False,
        'ALLOWED_HOSTS': ['.miproyecto.com', 'www.miproyecto.com'],
        'DATABASE': 'postgresql',
        'CACHE': 'redis',
        'SECURITY_FEATURES': {
            'HTTPS': True,
            'HSTS': True,
            'CSP': True,
        }
    },
    'testing': {
        'DEBUG': True,
        'ALLOWED_HOSTS': ['localhost'],
        'DATABASE': 'sqlite',
        'CACHE': 'locmem',
    }
}
