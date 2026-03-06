"""
Utilidades para interactuar con Supabase Storage.

Bucket por defecto: 'juegos'
  - covers/  → imágenes de portada
  - files/   → ZIPs del juego
  - builds/  → archivos extraídos del ZIP (index.html, assets, etc.)
"""
import mimetypes
from pathlib import PurePosixPath

from decouple import config
from supabase import create_client, Client


BUCKET = "juegos"


def _client() -> Client:
    """Crea y devuelve el cliente de Supabase usando la Service Key."""
    url = config("SUPABASE_URL")
    key = config("SUPABASE_SERVICE_KEY")
    return create_client(url, key)


def upload_file(file_bytes: bytes, storage_path: str, content_type: str = "") -> str:
    """
    Sube bytes a Supabase Storage.

    Args:
        file_bytes:    Contenido del archivo en bytes.
        storage_path:  Ruta dentro del bucket, e.g. 'covers/42/portada.jpg'.
        content_type:  MIME type del archivo. Se detecta automáticamente si está vacío.

    Returns:
        URL pública del archivo subido.
    """
    if not content_type:
        guessed, _ = mimetypes.guess_type(storage_path)
        content_type = guessed or "application/octet-stream"

    client = _client()
    client.storage.from_(BUCKET).upload(
        path=storage_path,
        file=file_bytes,
        file_options={"content-type": content_type, "upsert": "true"},
    )
    return client.storage.from_(BUCKET).get_public_url(storage_path)


def delete_files(storage_paths: list[str]) -> None:
    """
    Elimina uno o más archivos del bucket.

    Args:
        storage_paths: Lista de rutas dentro del bucket a eliminar.
    """
    if not storage_paths:
        return
    _client().storage.from_(BUCKET).remove(storage_paths)


def public_url(storage_path: str) -> str:
    """Devuelve la URL pública de un archivo ya existente en el bucket."""
    return _client().storage.from_(BUCKET).get_public_url(storage_path)
