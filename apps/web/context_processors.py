from django.conf import settings

def supabase_config(request):
    return {
        'SUPABASE_URL': settings.SUPABASE_URL.rstrip('/'),
    }
