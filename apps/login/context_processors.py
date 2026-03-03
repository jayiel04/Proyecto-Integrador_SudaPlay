from pathlib import Path

from django.conf import settings
from django.templatetags.static import static

from .models import UserProfile

_AVATAR_CACHE = None

def _avatar_variants():
    global _AVATAR_CACHE
    if _AVATAR_CACHE is not None:
        return _AVATAR_CACHE

    avatars_dir = Path(settings.BASE_DIR) / 'static' / 'avatars'
    if not avatars_dir.exists():
        return []

    _AVATAR_CACHE = [
        static(f'avatars/{avatar.name}') for avatar in sorted(avatars_dir.iterdir()) if avatar.is_file()
    ]
    return _AVATAR_CACHE


def _resolve_avatar(profile):
    """Devuelve la URL del avatar del usuario o cadena vacía si no tiene uno propio."""
    if profile and profile.avatar and hasattr(profile.avatar, 'path'):
        try:
            avatar_path = Path(profile.avatar.path)
            if avatar_path.exists():
                return profile.avatar.url
        except (ValueError, NotImplementedError):
            pass
    return ''


def _calculate_completion(user, profile):
    steps = [
        bool(user.email),
        bool(profile and profile.bio and profile.bio.strip()),
        bool(profile and profile.avatar and getattr(profile.avatar, 'name', '').strip() and not profile.avatar.name.endswith('avatars/default.png')),
        bool(profile and profile.phone and profile.phone.strip()),
        bool(profile and profile.date_of_birth),
        bool(profile and profile.is_verified),
    ]
    if not steps:
        return 0
    completed = sum(1 for step in steps if step)
    return min(100, round((completed / len(steps)) * 100))


def navbar_profile(request):
    avatar_url = ''
    completion = 0
    profile_bio = ''

    if request.user.is_authenticated:
        try:
            profile = request.user.profile
        except UserProfile.DoesNotExist:
            profile = None

        if profile:
            avatar_url = _resolve_avatar(profile)
            profile_bio = profile.bio or ''
            completion = _calculate_completion(request.user, profile)

    return {
        'navbar_avatar_url': avatar_url,
        'navbar_profile_completion': completion,
        'navbar_profile_bio': profile_bio,
        'navbar_avatar_variants': _avatar_variants(),
        'sudaplay_logo_url': static('img/SudaPlay.png'),
    }
