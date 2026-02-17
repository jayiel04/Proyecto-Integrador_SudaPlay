from pathlib import Path
import shutil
import zipfile

from django.conf import settings


def _safe_extract(zip_file: zipfile.ZipFile, destination: Path) -> None:
    destination = destination.resolve()

    for member in zip_file.infolist():
        member_path = (destination / member.filename).resolve()
        if not str(member_path).startswith(str(destination)):
            raise ValueError("El archivo ZIP contiene rutas no permitidas.")

    zip_file.extractall(destination)


def _find_index_html(build_dir: Path) -> Path | None:
    candidates = [path for path in build_dir.rglob("index.html") if path.is_file()]
    if not candidates:
        return None

    # Prefer the shortest path to avoid selecting nested demo folders.
    return sorted(candidates, key=lambda p: (len(p.parts), len(str(p))))[0]


def process_uploaded_web_build(game):
    if not game.game_file:
        return False, "No se encontro un archivo para procesar."

    source_path = Path(game.game_file.path)
    if source_path.suffix.lower() != ".zip":
        return False, "Solo se permite ZIP para jugar dentro de la plataforma."

    build_dir = Path(settings.MEDIA_ROOT) / "games" / "builds" / str(game.id)
    if build_dir.exists():
        shutil.rmtree(build_dir, ignore_errors=True)
    build_dir.mkdir(parents=True, exist_ok=True)

    try:
        with zipfile.ZipFile(source_path, "r") as zip_file:
            _safe_extract(zip_file, build_dir)
    except Exception as exc:
        shutil.rmtree(build_dir, ignore_errors=True)
        return False, f"No se pudo extraer el ZIP: {exc}"

    index_path = _find_index_html(build_dir)
    if not index_path:
        shutil.rmtree(build_dir, ignore_errors=True)
        return False, "El ZIP debe contener un archivo index.html."

    relative_index = index_path.relative_to(Path(settings.MEDIA_ROOT)).as_posix()
    game.web_build_path = relative_index
    game.is_web_playable = True
    game.processing_error = ""
    game.save(update_fields=["web_build_path", "is_web_playable", "processing_error", "updated_at"])

    return True, ""
