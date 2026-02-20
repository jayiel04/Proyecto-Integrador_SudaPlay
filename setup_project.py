#!/usr/bin/env python
"""
Script de configuraciÃ³n inicial del proyecto.
Ejecutar con: python setup_project.py
"""

import os
import sys
import django
from pathlib import Path
from django.core.management import execute_from_command_line

def setup():
    """Configurar el proyecto automÃ¡ticamente."""
    print("=" * 60)
    print("ðŸš€ Configurando Proyecto Django")
    print("=" * 60)
    
    # 1. Crear archivo .env si no existe
    env_file = Path('.env')
    if not env_file.exists():
        print("\nðŸ“ Creando archivo .env...")
        env_file.write_text(
            "DEBUG=True\n"
            "ENVIRONMENT=development\n"
            "SECRET_KEY=\n"
            "ALLOWED_HOSTS=localhost,127.0.0.1\n",
            encoding="utf-8",
        )
        print("âœ… .env creado")
    else:
        print("âœ… .env ya existe")
    
    # 2. Crear carpeta logs
    logs_dir = Path('logs')
    if not logs_dir.exists():
        logs_dir.mkdir()
        print("âœ… Carpeta 'logs' creada")
    else:
        print("âœ… Carpeta 'logs' existe")
    
    # 3. Crear carpeta media
    media_dir = Path('media')
    if not media_dir.exists():
        media_dir.mkdir()
        # Crear subcarpetas
        (media_dir / 'avatars').mkdir(exist_ok=True)
        print("âœ… Carpeta 'media' creada")
    else:
        print("âœ… Carpeta 'media' existe")
    
    # 4. Configurar Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mi_proyecto.settings')
    django.setup()
    
    # 5. Hacer migraciones
    print("\nðŸ”„ Aplicando migraciones de Django...")
    try:
        execute_from_command_line(['manage.py', 'migrate'])
        print("âœ… Migraciones aplicadas")
    except Exception as e:
        print(f"âš ï¸  Error en migraciones: {e}")
    
    # 6. Hacer migraciones de apps locales
    print("\nðŸ”„ Creando migraciones de apps locales...")
    try:
        execute_from_command_line(['manage.py', 'makemigrations', 'login', 'web'])
        print("âœ… Migraciones locales creadas")
    except Exception as e:
        print(f"âš ï¸  Error: {e}")
    
    # 7. Aplicar migraciones locales
    print("\nðŸ”„ Aplicando migraciones locales...")
    try:
        execute_from_command_line(['manage.py', 'migrate'])
        print("âœ… Migraciones locales aplicadas")
    except Exception as e:
        print(f"âš ï¸  Error: {e}")
    
    # 8. Configurar Google SocialApp (Nuevo)
    print("\nâš™ï¸  Configurando Google OAuth...")
    try:
        from allauth.socialaccount.models import SocialApp
        from django.contrib.sites.models import Site
        from decouple import config, UndefinedValueError

        try:
            client_id = config('GOOGLE_CLIENT_ID')
            client_secret = config('GOOGLE_CLIENT_SECRET')

            if client_id and client_id != 'tu-google-client-id.apps.googleusercontent.com':
                # Asegurar que el sitio por defecto existe
                site, created = Site.objects.get_or_create(id=1, defaults={'domain': 'localhost:8000', 'name': 'localhost'})
                
                # Crear o actualizar la aplicaciÃ³n social
                app, created = SocialApp.objects.update_or_create(
                    provider='google',
                    defaults={
                        'name': 'Google Login',
                        'client_id': client_id,
                        'secret': client_secret,
                    }
                )
                app.sites.add(site)
                print(f"âœ… Google SocialApp {'creada' if created else 'actualizada'}")
            else:
                print("\nâŒ ERROR: GOOGLE_CLIENT_ID no configurado en .env")
                print("ðŸ‘‰ AsegÃºrate de copiar las credenciales reales en tu archivo .env")
                print("ðŸ‘‰ Se saltarÃ¡ la configuraciÃ³n de Google OAuth por ahora.")
        except (UndefinedValueError, KeyError):
            print("\nâŒ ERROR: No se encontraron las variables de Google en el .env")
            print("ðŸ‘‰ Verifica que el archivo .env exista y contenga GOOGLE_CLIENT_ID y GOOGLE_CLIENT_SECRET")
    except Exception as e:
        print(f"âš ï¸  Error configurando Google OAuth: {e}")

    # 9. Recolectar estÃ¡ticos (opcional)
    
    print("\n" + "=" * 60)
    print("âœ… CONFIGURACIÃ“N COMPLETADA")
    print("=" * 60)
    print("\nPrÃ³ximos pasos:")
    print("1. Crear superusuario: python manage.py createsuperuser")
    print("2. Ejecutar servidor: python manage.py runserver")
    print("3. Acceder a: http://localhost:8000/")
    print("4. Admin: http://localhost:8000/admin/")
    print("=" * 60)

if __name__ == '__main__':
    setup()

