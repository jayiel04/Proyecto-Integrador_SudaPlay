from pathlib import Path

from django.conf import settings
from django.core.cache import cache
from django.templatetags.static import static

from .models import UserProfile
from apps.web.storage_backends import AvatarStorage

_AVATAR_CACHE = None
_AVATAR_NAME_CACHE = [
    "Psicologo.png", "acostado.png", "avatar-removebg-preview.png", 
    "avatar-sentaado-bravo.jpg", "basura.png", "camara.png", "camara_parada.png",
    "camara_sentaado.jpeg", "cartas.png", "cartas_amigo.png", "celular_parado.png",
    "celular_sentado.png", "cocina.png", "jorge.png", "postre.png",
    "sentado_bravo_turquesa.jpg", "sentado_solo.png", "sombrero.png",
    "sonriente.png", "viuda.png"
]


def _avatar_names():
    return _AVATAR_NAME_CACHE


def _default_avatar_url():
    names = _avatar_names()
    if not names:
        return ''
    preferred = 'sonriente.png' if 'sonriente.png' in names else names[0]
    return AvatarStorage().url(preferred)


def _avatar_variants():
    global _AVATAR_CACHE
    if _AVATAR_CACHE is not None:
        return _AVATAR_CACHE
    storage = AvatarStorage()
    _AVATAR_CACHE = [storage.url(name) for name in _avatar_names()]
    return _AVATAR_CACHE


def _resolve_avatar(profile):
    """Devuelve la URL del avatar."""
    if profile and profile.avatar:
        try:
            return profile.avatar.url
        except Exception:
            pass
    return _default_avatar_url()


def _calculate_completion(user, profile):
    avatar_name = profile.avatar.name if profile and profile.avatar else ''
    steps = [
        bool(user.email),
        bool(profile and profile.bio and profile.bio.strip()),
        bool(avatar_name),
        bool(profile and profile.phone and profile.phone.strip()),
        bool(profile and profile.date_of_birth),
        bool(profile and profile.is_verified),
    ]
    if not steps:
        return 0
    completed = sum(1 for step in steps if step)
    return min(100, round((completed / len(steps)) * 100))


def navbar_profile(request):
    if not request.user.is_authenticated:
        return {
            'navbar_avatar_url': '',
            'navbar_profile_completion': 0,
            'navbar_profile_bio': '',
            'navbar_avatar_variants': _avatar_variants(),
            'sudaplay_logo_url': f"{settings.SUPABASE_URL.rstrip('/')}/storage/v1/object/public/imagenes/Adornos/logo.png",
        }

    cache_key = f'navbar_profile_{request.user.id}'
    cached = cache.get(cache_key)
    if cached is not None:
        return cached

    # Una sola query con select_related para evitar queries adicionales
    profile = UserProfile.objects.filter(user=request.user).first()

    avatar_url = _resolve_avatar(profile)
    profile_bio = profile.bio or '' if profile else ''
    completion = _calculate_completion(request.user, profile) if profile else 0

    result = {
        'navbar_avatar_url': avatar_url,
        'navbar_profile_completion': completion,
        'navbar_profile_bio': profile_bio,
        'navbar_avatar_variants': _avatar_variants(),
        'sudaplay_logo_url': f"{settings.SUPABASE_URL.rstrip('/')}/storage/v1/object/public/imagenes/Adornos/logo.png",
    }
    # Cachear por 30 segundos para evitar queries repetidas en cada request
    cache.set(cache_key, result, timeout=30)
    return result

