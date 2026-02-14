from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from django.contrib.auth import get_user_model

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    def pre_social_login(self, request, sociallogin):
        # Si la cuenta social ya existe (está vinculada), no hacemos nada
        if sociallogin.is_existing:
            return

        # Intentamos obtener el usuario por su email
        user_email = sociallogin.user.email
        if not user_email:
            # Si no hay email en los datos del proveedor, intentamos obtenerlo de extra_data
            user_email = sociallogin.account.extra_data.get('email')
        
        if user_email:
            User = get_user_model()
            try:
                # Buscamos si existe un usuario con ese email
                user = User.objects.get(email=user_email)
                
                # Si existe, conectamos la cuenta social a este usuario
                sociallogin.connect(request, user)
                
            except User.DoesNotExist:
                # Si no existe, dejamos que allauth continúe con el flujo de registro normal
                pass
