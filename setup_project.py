#!/usr/bin/env python
"""
Script de configuración inicial del proyecto.
Ejecutar con: python setup_project.py
"""

import os
import sys
import django
from pathlib import Path
from django.core.management import execute_from_command_line

def setup():
    """Configurar el proyecto automáticamente."""
    print("=" * 60)
    print("🚀 Configurando Proyecto Django")
    print("=" * 60)
    
    # 1. Crear archivo .env si no existe
    env_file = Path('.env')
    if not env_file.exists():
        print("\n📝 Creando archivo .env...")
        env_example = Path('.env.example')
        if env_example.exists():
            env_file.write_text(env_example.read_text())
            print("✅ .env creado desde .env.example")
        else:
            print("⚠️  .env.example no encontrado")
    else:
        print("✅ .env ya existe")
    
    # 2. Crear carpeta logs
    logs_dir = Path('logs')
    if not logs_dir.exists():
        logs_dir.mkdir()
        print("✅ Carpeta 'logs' creada")
    else:
        print("✅ Carpeta 'logs' existe")
    
    # 3. Crear carpeta media
    media_dir = Path('media')
    if not media_dir.exists():
        media_dir.mkdir()
        # Crear subcarpetas
        (media_dir / 'avatars').mkdir(exist_ok=True)
        print("✅ Carpeta 'media' creada")
    else:
        print("✅ Carpeta 'media' existe")
    
    # 4. Configurar Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mi_proyecto.settings')
    django.setup()
    
    # 5. Hacer migraciones
    print("\n🔄 Aplicando migraciones de Django...")
    try:
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Migraciones aplicadas")
    except Exception as e:
        print(f"⚠️  Error en migraciones: {e}")
    
    # 6. Hacer migraciones de apps locales
    print("\n🔄 Creando migraciones de apps locales...")
    try:
        execute_from_command_line(['manage.py', 'makemigrations', 'login', 'web'])
        print("✅ Migraciones locales creadas")
    except Exception as e:
        print(f"⚠️  Error: {e}")
    
    # 7. Aplicar migraciones locales
    print("\n🔄 Aplicando migraciones locales...")
    try:
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Migraciones locales aplicadas")
    except Exception as e:
        print(f"⚠️  Error: {e}")
    
    # 8. Recolectar estáticos (opcional)
    print("\n🎨 Recolectando archivos estáticos...")
    try:
        execute_from_command_line(['manage.py', 'collectstatic', '--noinput'])
        print("✅ Estáticos recolectados")
    except Exception as e:
        print(f"⚠️  Error: {e}")
    
    print("\n" + "=" * 60)
    print("✅ CONFIGURACIÓN COMPLETADA")
    print("=" * 60)
    print("\nPróximos pasos:")
    print("1. Crear superusuario: python manage.py createsuperuser")
    print("2. Ejecutar servidor: python manage.py runserver")
    print("3. Acceder a: http://localhost:8000/")
    print("4. Admin: http://localhost:8000/admin/")
    print("=" * 60)

if __name__ == '__main__':
    setup()
