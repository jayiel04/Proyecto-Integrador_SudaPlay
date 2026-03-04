from supabase import create_client
from django.conf import settings

supabase = create_client(
    settings.SUPABASE_URL,
    settings.SUPABASE_KEY
)
# Esta conexión permite que Django se comunique con Supabase.
# Sirve para:
# - Subir imágenes
# - Guardar datos
# - Crear chats
# - Guardar progreso de juegos
# - Hacer rankings (leaderboards)