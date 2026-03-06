"""
Procesamiento de archivos ZIP subidos como juegos web.

Soporta tanto almacenamiento LOCAL (media/) como almacenamiento S3/Supabase.
"""
import io
import mimetypes
import zipfile
import requests

from django.conf import settings
from django.core.files.base import ContentFile


def _find_index_html_in_zip(zip_file: zipfile.ZipFile) -> str | None:
    """
    Devuelve el nombre del archivo index.html más superficial dentro del ZIP.
    Ignora carpetas __MACOSX generadas por macOS.
    """
    candidates = [
        name for name in zip_file.namelist()
        if name.lower().endswith("index.html") and not name.startswith("__MACOSX")
    ]
    if not candidates:
        return None
    return sorted(candidates, key=lambda p: (p.count("/"), len(p)))[0]


def _is_s3_storage() -> bool:
    """Devuelve True si el proyecto está usando almacenamiento S3."""
    storages = getattr(settings, "STORAGES", {})
    if "default" in storages:
        backend = storages["default"].get("BACKEND", "")
    else:
        backend = getattr(settings, "DEFAULT_FILE_STORAGE", "")
        
    return "s3" in backend.lower() or "boto" in backend.lower()


def _supabase_public_url(path: str) -> str:
    """
    Construye la URL pública de Supabase Storage para un archivo.
    La URL pública usa /storage/v1/object/public/<bucket>/<path>
    que es DISTINTA a la URL del endpoint S3 (/storage/v1/s3/<bucket>/<path>).
    """
    supabase_url = settings.SUPABASE_URL.rstrip("/")
    bucket = settings.AWS_STORAGE_BUCKET_NAME
    clean_path = path.lstrip("/")
    return f"{supabase_url}/storage/v1/object/public/{bucket}/{clean_path}"


def _process_s3(game) -> tuple[bool, str]:
    """
    Procesa un ZIP almacenado en Supabase S3:
    1. Lee el ZIP desde S3 en memoria.
    2. Extrae TODOS los archivos y los sube a games/builds/<id>/ en S3.
    3. Actualiza web_build_path con la URL PÚBLICA (object/public) del index.html.

    Requisito: el bucket de Supabase debe ser PÚBLICO.
    """
    from django.core.files.storage import default_storage

    # 1. Leer el ZIP desde S3
    try:
        with game.game_file.open("rb") as f:
            zip_bytes = f.read()
    except Exception as exc:
        return False, f"No se pudo leer el archivo desde el almacenamiento: {exc}"

    # 2. Abrir el ZIP y verificar que tiene index.html
    try:
        zf = zipfile.ZipFile(io.BytesIO(zip_bytes))
    except zipfile.BadZipFile:
        return False, "El archivo no es un ZIP válido."
    except Exception as exc:
        return False, f"No se pudo abrir el ZIP: {exc}"

    index_entry = _find_index_html_in_zip(zf)
    if not index_entry:
        return False, "El ZIP debe contener un archivo index.html."

    # 3. Extraer y subir cada archivo a games/builds/<game.id>/ en Supabase
    build_prefix = f"games/builds/{game.id}/"
    index_s3_path = None
    
    # ⚠️ FIX URGENCE: La API S3 de Supabase ignora el ContentType y fuerza text/plain.
    # Usamos la API REST nativa de Supabase Storage directamente.
    supabase_url = settings.SUPABASE_URL.rstrip("/")
    bucket_name = settings.AWS_STORAGE_BUCKET_NAME
    
    # Intentar obtener la clave de servicio (Service Role Key) que ignora RLS.
    # Si no existe, usamos la anónima, pero requeriría RLS configurado a público para INSERT.
    from decouple import config
    api_key = config("SUPABASE_SERVICE_ROLE_KEY", default=getattr(settings, "SUPABASE_KEY", ""))
    
    api_url_base = f"{supabase_url}/storage/v1/object/{bucket_name}"
    headers_base = {
        "apikey": api_key,
        "Authorization": f"Bearer {api_key}"
    }

    try:
        for item in zf.infolist():
            if item.is_dir() or item.filename.startswith("__MACOSX"):
                continue

            dest_path = build_prefix + item.filename

            with zf.open(item) as file_content:
                data = file_content.read()
                
                # Adivinar o forzar Content-Type
                content_type, _ = mimetypes.guess_type(item.filename)
                ext = item.filename.lower()
                if ext.endswith('.html') or ext.endswith('.htm'):
                    content_type = 'text/html'
                elif ext.endswith('.js'):
                    content_type = 'application/javascript'
                elif ext.endswith('.css'):
                    content_type = 'text/css'
                elif ext.endswith('.wasm'):
                    content_type = 'application/wasm'
                elif ext.endswith('.json'):
                    content_type = 'application/json'
                elif ext.endswith('.png'):
                    content_type = 'image/png'
                elif ext.endswith('.jpg') or ext.endswith('.jpeg'):
                    content_type = 'image/jpeg'
                
                if not content_type:
                    content_type = 'application/octet-stream'

                # Subida via API REST nativa de Supabase
                upload_url = f"{api_url_base}/{dest_path}"
                headers = headers_base.copy()
                headers["Content-Type"] = content_type
                
                # Usar requests para hacer un POST/PUT directo a Supabase
                resp = requests.post(upload_url, headers=headers, data=data)
                
                # Si falla por "Duplicate", hacer un PUT para sobreescribir
                if resp.status_code == 400 and b"Duplicate" in resp.content:
                    resp = requests.put(upload_url, headers=headers, data=data)
                    
                resp.raise_for_status()

            if item.filename == index_entry:
                index_s3_path = dest_path

    except Exception as exc:
        return False, f"Error al subir archivos extraídos a Supabase: {exc}"
    finally:
        zf.close()

    if not index_s3_path:
        return False, "No se pudo localizar el index.html tras la extracción."

    # 4. Construir la URL PÚBLICA de Supabase (NO la URL del endpoint S3)
    index_url = _supabase_public_url(index_s3_path)

    game.web_build_path = index_url
    game.is_web_playable = True
    game.processing_error = ""
    game.save(update_fields=["web_build_path", "is_web_playable", "processing_error", "updated_at"])

    return True, ""


def _process_local(game) -> tuple[bool, str]:
    """
    Procesa un ZIP almacenado localmente (desarrollo sin S3).
    Extrae los archivos en media/games/builds/<id>/ y sirve el index.html.
    """
    from pathlib import Path
    import shutil

    # Leer el ZIP (puede ser una URL de Supabase o un archivo local temporal)
    try:
        import urllib.request
        zip_bytes = urllib.request.urlopen(game.game_file).read()
    except Exception:
        try:
            zip_bytes = game.game_file.read()
        except Exception as exc:
            return False, f"No se pudo leer el archivo: {exc}"

    # Validar que sea un ZIP real
    try:
        zip_buffer = io.BytesIO(zip_bytes)
        with zipfile.ZipFile(zip_buffer, "r") as zf:
            names = zf.namelist()
    except zipfile.BadZipFile:
        return False, "El archivo subido no es un ZIP válido."

    # Buscar index.html
    index_member = _find_index_path(names)
    if not index_member:
        return False, "El ZIP debe contener un archivo index.html."

    # Prefijo de la carpeta de build en Supabase
    build_prefix = f"builds/{game.id}"

    # Limpiar build anterior si existe
    old_paths = [f"{build_prefix}/{name}" for name in names if not name.endswith("/")]
    delete_files(old_paths)

    # Extraer y subir cada archivo
    try:
        with zipfile.ZipFile(source_path, "r") as zip_file:
            build_dir_resolved = build_dir.resolve()
            for member in zip_file.infolist():
                member_path = (build_dir_resolved / member.filename).resolve()
                if not str(member_path).startswith(str(build_dir_resolved)):
                    shutil.rmtree(build_dir, ignore_errors=True)
                    return False, "El archivo ZIP contiene rutas no permitidas."
            zip_file.extractall(build_dir)
    except Exception as exc:
        return False, f"Error subiendo archivos a Supabase: {exc}"

    candidates = [p for p in build_dir.rglob("index.html") if p.is_file()]
    if not candidates:
        shutil.rmtree(build_dir, ignore_errors=True)
        return False, "El ZIP debe contener un archivo index.html."

    index_path = sorted(candidates, key=lambda p: (len(p.parts), len(str(p))))[0]
    relative_index = index_path.relative_to(Path(settings.MEDIA_ROOT)).as_posix()

    game.web_build_path = relative_index
    game.is_web_playable = True
    game.processing_error = ""
    game.save(update_fields=["web_build_path", "is_web_playable", "processing_error", "updated_at"])

    return True, ""


def process_uploaded_web_build(game) -> tuple[bool, str]:
    """
    Punto de entrada: detecta si se usa S3 o almacenamiento local y procesa
    el ZIP del juego, extrayendo sus archivos para servir el index.html.
    """
    if not game.game_file:
        return False, "No se encontró un archivo para procesar."

    if _is_s3_storage():
        return _process_s3(game)
    else:
        return _process_local(game)
