import os
from django.core.management.base import BaseCommand
from django.core.files import File
from django.conf import settings
from apps.login.models import UserProfile

class Command(BaseCommand):
    help = 'Migra los avatares locales de los usuarios a Supabase Storage'

    def handle(self, *args, **kwargs):
        profiles = UserProfile.objects.exclude(avatar='')
        migrados = 0
        errores = 0

        for profile in profiles:
            if not profile.avatar:
                continue

            try:
                # Comprobar si ya está en Supabase leyendo su URL
                url = profile.avatar.url
                if 'supabase' in url:
                    self.stdout.write(self.style.WARNING(f'Omitiendo {profile.user.username}: ya tiene Storage remoto.'))
                    continue
            except Exception:
                pass

            # Generar la ruta local supuesta
            local_path = os.path.join(settings.MEDIA_ROOT, profile.avatar.name)
            if os.path.exists(local_path):
                try:
                    with open(local_path, 'rb') as f:
                        django_file = File(f)
                        # profile.avatar.name por lo general sera avatars/mi_foto.jpg
                        # al resguardar con el nuevo storage, se va a Subir a Supabase
                        name = os.path.basename(profile.avatar.name)
                        profile.avatar.save(name, django_file, save=True)
                    self.stdout.write(self.style.SUCCESS(f'Migrado exitosamente p/ {profile.user.username}'))
                    migrados += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error al migrar {profile.user.username}: {e}'))
                    errores += 1
            else:
                 self.stdout.write(self.style.WARNING(f'Archivo no encontrado para {profile.user.username} en {local_path}'))

        self.stdout.write(self.style.SUCCESS(f'Migración completada. Total migrados: {migrados}, Errores: {errores}'))
