"""
Adaptadores para personalizar el comportamiento de Allauth en SudaPlay.
"""
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        """Link automático de cuentas por email y limpieza de flujo."""
        if sociallogin.is_existing:
            return

        user_email = sociallogin.user.email or sociallogin.account.extra_data.get('email')
        
        if user_email:
            User = get_user_model()
            try:
                user = User.objects.get(email=user_email)
                sociallogin.connect(request, user)
            except User.DoesNotExist:
                pass

    def is_auto_signup_allowed(self, request, sociallogin):
        """Forzar paso por 'Finalizar Registro' para nuevos usuarios sociales."""
        return False
