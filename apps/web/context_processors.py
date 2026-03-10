from django.conf import settings

def supabase_config(request):
    supabase_url = settings.SUPABASE_URL.rstrip('/')
    return {
        'SUPABASE_URL': supabase_url,
        'SUPABASE_ADORNOS_BASE': f"{supabase_url}/storage/v1/object/public/imagenes/Adornos",
    }
