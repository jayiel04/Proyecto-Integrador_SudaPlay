"""
Vistas para la aplicación login.

Mejores prácticas:
- Usar Class-Based Views (CBV)
- Validación con formularios Django
- Manejo de mensajes
- Decoradores de autenticación
"""
import logging
import smtplib
import uuid
from pathlib import Path

import requests
from django.conf import settings
from django.core.cache import cache
from django.shortcuts import redirect
from django.views import View
from django.views.generic import FormView
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from django.contrib import messages
from django.core.exceptions import ValidationError as DjangoValidationError
from django.http import JsonResponse
from django.templatetags.static import static
from django.urls import reverse_lazy
from datetime import timedelta

from django.utils import timezone
from django.utils.decorators import method_decorator
from django.db.models import Count, Case, When, IntegerField, Q

from django.contrib.sites.models import Site

from allauth.account.views import PasswordChangeView, PasswordSetView, PasswordResetView
from allauth.core.exceptions import ImmediateHttpResponse

from .forms import RegisterForm, ProfileUpdateForm
from .models import UserProfile, FriendRequest, Notification
from apps.chat.models import ChatMessage


from apps.login.context_processors import _AVATAR_NAME_CACHE
from apps.web.storage_backends import AvatarStorage

logger = logging.getLogger(__name__)

def _available_avatar_names():
    return _AVATAR_NAME_CACHE


def _default_avatar_name(available_avatars):
    if 'sonriente.png' in available_avatars:
        return 'sonriente.png'
    return available_avatars[0] if available_avatars else ''


def _resolve_avatar_url(profile, available_avatars):
    if profile and getattr(profile, 'avatar', None):
        try:
            return profile.avatar.url
        except Exception:
            pass
    default_avatar = _default_avatar_name(available_avatars)
    return AvatarStorage().url(default_avatar) if default_avatar else ''


def _user_is_online(user, window_minutes=5):
    if not user or not getattr(user, 'is_active', False):
        return False
    last_login = getattr(user, 'last_login', None)
    if not last_login:
        return False
    return timezone.now() - last_login <= timedelta(minutes=window_minutes)


class LoginView(FormView):
    """
    Vista para login de usuarios.
    Usa el formulario de autenticación de Django.
    """

    template_name = 'login/login.html'
    form_class = AuthenticationForm
    success_url = reverse_lazy('web:home')

    def form_valid(self, form):
        """Autenticar usuario si el formulario es válido."""
        user = form.get_user()
        auth_login(self.request, user)
        # Mostrar bienvenida una sola vez al entrar después del login.
        self.request.session["show_post_login_welcome"] = True
        return super().form_valid(form)

    def form_invalid(self, form):
        """Mostrar error si el formulario no es válido."""
        return super().form_invalid(form)

    def get(self, request, *args, **kwargs):
        """Redirigir a home si ya está autenticado."""
        if request.user.is_authenticated:
            return redirect('web:home')
        return super().get(request, *args, **kwargs)


class RegisterView(FormView):
    """
    Vista para registro de nuevos usuarios.
    Usa un formulario personalizado con validaciones.
    """

    template_name = 'login/register.html'
    form_class = RegisterForm
    success_url = reverse_lazy('login:login')

    def form_valid(self, form):
        """Guardar nuevo usuario si el formulario es válido."""
        form.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        """Mostrar errores si el formulario no es válido."""
        return super().form_invalid(form)

    def get(self, request, *args, **kwargs):
        """Redirigir a home si ya está autenticado."""
        if request.user.is_authenticated:
            return redirect('web:home')
        return super().get(request, *args, **kwargs)


class LogoutView(View):
    """
    Vista para logout de usuarios.
    Cierra la sesión del usuario y redirige al login.
    """

    def get(self, request):
        """Cerrar sesión del usuario."""
        auth_logout(request)
        return redirect('login:login')


class ProfileUpdateView(FormView):
    """
    Vista para editar el perfil del usuario autenticado.
    """

    template_name = 'login/profile_edit.html'
    form_class = ProfileUpdateForm
    success_url = reverse_lazy('web:home')

    @method_decorator(login_required(login_url='login:login'))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    @staticmethod
    def _available_avatars():
        return _available_avatar_names()

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.request.user
        kwargs['available_avatars'] = self._available_avatars()
        return kwargs

    def form_valid(self, form):
        form.save()
        # Refrescar avatar del navbar inmediatamente
        cache.delete(f'navbar_profile_{self.request.user.id}')
        messages.success(self.request, 'Perfil actualizado correctamente.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = UserProfile.objects.filter(user=self.request.user).first()
        available_avatars = self._available_avatars()
        current_avatar_name_raw = Path(getattr(getattr(profile, 'avatar', None), 'name', '')).name
        current_avatar_name = current_avatar_name_raw if current_avatar_name_raw in available_avatars else ''
        default_avatar_name = _default_avatar_name(available_avatars)

        context['current_avatar_name'] = current_avatar_name
        context['current_avatar_url'] = _resolve_avatar_url(profile, available_avatars)
        context['default_avatar_url'] = AvatarStorage().url(default_avatar_name) if default_avatar_name else ''
        context['available_avatars'] = available_avatars
        context['available_avatar_data'] = [{'name': name, 'url': AvatarStorage().url(name)} for name in available_avatars]
        return context


class CustomPasswordChangeView(PasswordChangeView):
    """Override allauth PasswordChangeView to set a custom success URL."""
    success_url = reverse_lazy('web:home')

    def form_valid(self, form):
        msg = 'La contraseña fue cambiada exitosamente.'
        messages.success(self.request, msg, extra_tags='popup')
        
        sys_notifs = self.request.session.get('system_notifs', [])
        sys_notifs.append(msg)
        self.request.session['system_notifs'] = sys_notifs
        cache.delete(f'notifications_{self.request.user.id}')
        
        return super().form_valid(form)


class CustomPasswordSetView(PasswordSetView):
    """Override allauth PasswordSetView to set a custom success URL."""
    success_url = reverse_lazy('web:home')

    def form_valid(self, form):
        msg = 'La contraseña fue establecida exitosamente.'
        messages.success(self.request, msg, extra_tags='popup')
        
        sys_notifs = self.request.session.get('system_notifs', [])
        sys_notifs.append(msg)
        self.request.session['system_notifs'] = sys_notifs
        cache.delete(f'notifications_{self.request.user.id}')
        
        return super().form_valid(form)


class CustomPasswordResetView(PasswordResetView):
    """
    Evita 500 si falla el envío de correo o la configuración (Sites, SMTP, etc.).
    allauth solo captura un subconjunto de errores de red; otros backends o
    Site.DoesNotExist propagaban hasta Django.
    """

    def form_valid(self, form):
        email = form.cleaned_data.get('email')
        try:
            return super().form_valid(form)
        except ImmediateHttpResponse:
            raise
        except Site.DoesNotExist:
            logger.exception(
                'Site faltante para SITE_ID=%s (revisa django.contrib.sites en admin)',
                getattr(settings, 'SITE_ID', None),
            )
            form.add_error(
                None,
                (
                    'La recuperación de contraseña no está configurada correctamente en el servidor. '
                    'Contacta al administrador.'
                ),
            )
            return self.form_invalid(form)
        except Exception:
            logger.exception(
                'Fallo en recuperacion de contrasena para %s',
                email,
            )
            form.add_error(
                None,
                (
                    'No pudimos enviar el correo de restablecimiento en este momento. '
                    'Intenta de nuevo en unos minutos.'
                ),
            )
            return self.form_invalid(form)


class ProfileView(View):
    """
    Vista para mostrar el perfil del usuario autenticado.
    """

    template_name = 'login/profile.html'

    @method_decorator(login_required(login_url='login:login'))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        from django.shortcuts import render
        from apps.web.models import Game

        profile = UserProfile.objects.filter(user=request.user).first()
        user_games = Game.objects.filter(uploaded_by=request.user).order_by('-created_at')
        # Una sola query con aggregate en vez de 3 queries separadas
        counts = user_games.aggregate(
            approved=Count(Case(When(is_approved=True, then=1), output_field=IntegerField())),
            pending=Count(Case(When(is_approved=False, then=1), output_field=IntegerField())),
        )
        approved = counts['approved']
        pending = counts['pending']

        available_avatars = _available_avatar_names()
        avatar_url = _resolve_avatar_url(profile, available_avatars)
            
        # Obtener solicitudes de amistad entrantes y amigos
        friend_requests = FriendRequest.objects.filter(to_user=request.user).select_related('from_user__profile')
        friends = profile.friends.all().select_related('user') if profile else UserProfile.objects.none()

        for req in friend_requests:
            req.avatar_url = _resolve_avatar_url(getattr(req.from_user, 'profile', None), available_avatars)
        for friend in friends:
            friend.avatar_url = _resolve_avatar_url(friend, available_avatars)
            friend.is_online = _user_is_online(getattr(friend, 'user', None))

        context = {
            'profile': profile,
            'user_games': user_games,
            'avatar_url': avatar_url,
            'user_games_count': approved + pending,
            'user_games_approved': approved,
            'user_games_pending': pending,
            'friend_requests': friend_requests,
            'friends': friends,
        }
        return render(request, self.template_name, context)




class SearchPlayersView(View):
    """
    Vista para buscar jugadores por nombre de usuario.
    """
    template_name = 'login/search_players.html'

    @method_decorator(login_required(login_url='login:login'))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        from django.shortcuts import render
        query = request.GET.get('q', '').strip()
        tab = request.GET.get('tab', 'players')
        results = []

        if tab == 'friends':
            profile = getattr(request.user, 'profile', None)
            if profile:
                friends_qs = profile.friends.filter(user__is_active=True).select_related('user')
                if query:
                    friends_qs = friends_qs.filter(user__username__icontains=query)
                results = [f.user for f in friends_qs]
                for f in friends_qs:
                    f.user.profile = f
        else:
            if query:
                # Buscar usuarios cuyo username contenga el término, excluyendo al usuario actual
                results = User.objects.filter(
                    username__icontains=query,
                    is_active=True
                ).exclude(id=request.user.id).select_related('profile')

        available_avatars = _available_avatar_names()
        for u in results:
            u.avatar_url = _resolve_avatar_url(getattr(u, 'profile', None), available_avatars)

        context = {
            'query': query,
            'tab': tab,
            'results': results,
        }
        return render(request, self.template_name, context)


class PlayerProfileView(View):
    """
    Vista para el perfil público de otro jugador.
    """
    template_name = 'login/player_profile.html'

    @method_decorator(login_required(login_url='login:login'))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, username, *args, **kwargs):
        from django.shortcuts import render, get_object_or_404
        from apps.web.models import Game
        
        target_user = get_object_or_404(User, username=username, is_active=True)
        
        # Si intenta ver su propio perfil desde aquí, redirigir al perfil privado
        if target_user == request.user:
            return redirect('login:profile')

        # Manejador seguro para perfiles faltantes (evita RelatedObjectDoesNotExist)
        try:
            profile = target_user.profile
        except User.profile.RelatedObjectDoesNotExist:
            from .models import UserProfile
            profile = UserProfile.objects.create(user=target_user)
            
        try:
            my_profile = request.user.profile
        except User.profile.RelatedObjectDoesNotExist:
            from .models import UserProfile
            my_profile = UserProfile.objects.create(user=request.user)
        user_games = Game.objects.filter(
            uploaded_by=target_user, is_approved=True
        ).select_related('uploaded_by').order_by('-created_at')

        # Determinar el estado de amistad
        friendship_status = 'none' # none, pending_sent, pending_received, friends
        
        if my_profile.friends.filter(id=profile.id).exists():
            friendship_status = 'friends'
        elif FriendRequest.objects.filter(from_user=request.user, to_user=target_user).exists():
            friendship_status = 'pending_sent'
        elif FriendRequest.objects.filter(from_user=target_user, to_user=request.user).exists():
            friendship_status = 'pending_received'

        available_avatars = _available_avatar_names()
        target_is_online = _user_is_online(target_user)

        context = {
            'target_user': target_user,
            'profile': profile,
            'profile_avatar_url': _resolve_avatar_url(profile, available_avatars),
            'user_games': user_games,
            'friendship_status': friendship_status,
            'target_is_online': target_is_online,
        }
        return render(request, self.template_name, context)


