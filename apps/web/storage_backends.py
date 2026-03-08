from django.conf import settings
from django.core.files.storage import FileSystemStorage
from storages.backends.s3boto3 import S3Boto3Storage


def _supabase_public_url(location: str, name: str) -> str:
    """
    Construye la URL pública de Supabase Storage.

    El endpoint S3 (/storage/v1/s3/...) requiere firma aunque el bucket sea público.
    El endpoint público (/storage/v1/object/public/...) sirve archivos sin autenticación.
    """
    supabase_url = settings.SUPABASE_URL.rstrip("/")
    bucket = settings.AWS_STORAGE_BUCKET_NAME
    # location incluye la subcarpeta, name es el nombre del archivo
    path = f"{location}/{name}".lstrip("/")
    return f"{supabase_url}/storage/v1/object/public/{bucket}/{path}"


class GameFilesStorage(S3Boto3Storage):
    """
    Almacena los archivos .zip de los juegos en la carpeta 'games/files'
    dentro del bucket de Supabase.
    """
    location = 'games/files'
    file_overwrite = True   # Evita HeadObject check (incompatible con RLS de Supabase)

    def url(self, name):
        return _supabase_public_url(self.location, name)


class GameCoversStorage(S3Boto3Storage):
    """
    Almacena las imágenes de portada de los juegos en la carpeta 'games/covers'
    dentro del bucket de Supabase.
    """
    location = 'games/covers'
    file_overwrite = True   # Evita HeadObject check (incompatible con RLS de Supabase)

    def url(self, name):
        return _supabase_public_url(self.location, name)


class GameTempFilesStorage(FileSystemStorage):
    """
    Almacenamiento temporal LOCAL para los ZIPs recién subidos.
    El worker asíncrono sube el archivo a Supabase S3 en segundo plano,
    evitando que form.save() bloquee el request HTTP durante 10+ segundos.
    """
    def __init__(self):
        import os
        temp_root = os.path.join(settings.MEDIA_ROOT, 'games', 'temp')
        os.makedirs(temp_root, exist_ok=True)
        super().__init__(location=temp_root, base_url=None)
