"""
Servicio de procesamiento de juegos web.

Extrae el ZIP enviado por el usuario en memoria y sube cada archivo
al bucket de Supabase Storage bajo la ruta:
    builds/<game_id>/<ruta relativa del archivo>

El index.html raíz determina si el juego es jugable en web.
"""
import io
import zipfile

from .supabase_storage import upload_file, delete_files, public_url, BUCKET


def _find_index_path(names: list[str]) -> str | None:
    """
    Devuelve la ruta del index.html más cercano a la raíz del ZIP.
    Ignora rutas que parezcan ejemplos o demos (contienen 'demo', 'example', 'sample').
    """
    candidates = [
        name for name in names
        if name.lower().endswith("index.html")
        and not any(word in name.lower() for word in ("demo", "example", "sample"))
    ]
    if not candidates:
        return None
    # El más corto (menos niveles de directorio) es el principal
    return sorted(candidates, key=lambda p: (p.count("/"), len(p)))[0]


def process_uploaded_web_build(game) -> tuple[bool, str]:
    """
    Procesa el ZIP del juego y lo publica en Supabase Storage.

    1. Lee el ZIP desde el campo `game_file` del modelo.
    2. Extrae cada archivo en memoria.
    3. Sube cada archivo a Supabase bajo builds/<game.id>/...
    4. Localiza el index.html principal.
    5. Actualiza los campos del modelo (web_build_path, is_web_playable).

    Returns:
        (True, "")          si todo salió bien.
        (False, mensaje)    si hubo un error.
    """
    if not game.game_file:
        return False, "No se encontró un archivo para procesar."

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
        with zipfile.ZipFile(io.BytesIO(zip_bytes), "r") as zf:
            for member in zf.infolist():
                if member.is_dir():
                    continue
                file_data = zf.read(member.filename)
                storage_path = f"{build_prefix}/{member.filename}"
                upload_file(file_data, storage_path)
    except Exception as exc:
        return False, f"Error subiendo archivos a Supabase: {exc}"

    # URL del index.html principal
    index_storage_path = f"{build_prefix}/{index_member}"
    index_url = public_url(index_storage_path)

    game.web_build_path = index_url
    game.is_web_playable = True
    game.processing_error = ""
    game.save(update_fields=["web_build_path", "is_web_playable", "processing_error", "updated_at"])

    return True, ""
