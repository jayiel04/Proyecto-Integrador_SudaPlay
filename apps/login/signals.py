"""Senales especificas de la app login."""
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver


@receiver(user_logged_in)
def ensure_post_login_welcome_flag(sender, request, user, **kwargs):
    """Asegura que cualquier login deje la bandera para la bienvenida."""
    request.session["show_post_login_welcome"] = True
