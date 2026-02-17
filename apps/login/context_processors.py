from .models import UserProfile


def navbar_profile(request):
    avatar_url = ''

    if request.user.is_authenticated:
        try:
            profile = request.user.profile
        except UserProfile.DoesNotExist:
            profile = None

        if profile and profile.avatar:
            avatar_url = profile.avatar.url

    return {'navbar_avatar_url': avatar_url}
