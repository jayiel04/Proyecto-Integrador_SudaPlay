"""
Vistas para la aplicación login.

Mejores prácticas:
- Usar Class-Based Views (CBV)
- Validación con formularios Django
- Manejo de mensajes
- Decoradores de autenticación
"""
import uuid
from pathlib import Path

import requests
from django.conf import settings
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
from django.urls import reverse_lazy
from django.utils.decorators import method_decorator
from django.db.models import Q

from .forms import RegisterForm, ProfileUpdateForm
from .models import UserProfile, FriendRequest


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
        avatars_dir = Path(settings.BASE_DIR) / 'static' / 'avatars'
        if not avatars_dir.exists():
            return []
        return sorted([
            avatar.name for avatar in avatars_dir.iterdir() if avatar.is_file()
        ])

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.request.user
        kwargs['available_avatars'] = self._available_avatars()
        return kwargs

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Perfil actualizado correctamente.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = UserProfile.objects.filter(user=self.request.user).first()
        context['current_avatar_url'] = profile.avatar.url if profile and profile.avatar else ''
        context['available_avatars'] = self._available_avatars()
        return context


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
        from django.templatetags.static import static
        from apps.web.models import Game
        from pathlib import Path

        profile = UserProfile.objects.filter(user=request.user).first()
        user_games = Game.objects.filter(uploaded_by=request.user).order_by('-created_at')
        approved = user_games.filter(is_approved=True).count()
        pending = user_games.filter(is_approved=False).count()

        # Resolver URL del avatar: si el usuario tiene uno subido y existe en disco, usarlo.
        # De lo contrario, usar el avatar por defecto del sistema.
        avatar_url = ''
        if profile and profile.avatar:
            avatar_path = Path(profile.avatar.path)
            if avatar_path.exists():
                avatar_url = profile.avatar.url

        if not avatar_url:
            avatar_url = static('avatars/sonriente.png')
            
        # Obtener solicitudes de amistad entrantes y amigos
        friend_requests = FriendRequest.objects.filter(to_user=request.user).select_related('from_user__profile')
        friends = profile.friends.all().select_related('user')

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



class CheckUserAPIView(View):
    """
    API endpoint para verificar disponibilidad de usuario/email en tiempo real.
    """

    def get(self, request, *args, **kwargs):
        username = request.GET.get('username', None)
        email = request.GET.get('email', None)
        response = {'is_taken': False}

        if username:
            if User.objects.filter(username__iexact=username).exists():
                response['is_taken'] = True
                response['error_message'] = 'Este nombre de usuario ya esta en uso.'
        elif email:
            if User.objects.filter(email__iexact=email).exists():
                response['is_taken'] = True
                response['error_message'] = 'Este correo electronico ya esta registrado.'

        return JsonResponse(response)


class ValidatePasswordAPIView(View):
    """
    API endpoint para validar contraseña en tiempo real usando validadores Django.
    """

    def get(self, request, *args, **kwargs):
        password = request.GET.get('password', '') or ''
        username = request.GET.get('username', '') or ''
        email = request.GET.get('email', '') or ''

        if not password:
            return JsonResponse({
                'is_valid': False,
                'errors': ['La contraseña no puede estar vacía.'],
            })

        temp_user = User(username=username, email=email)

        try:
            validate_password(password, user=temp_user)
        except DjangoValidationError as exc:
            return JsonResponse({
                'is_valid': False,
                'errors': exc.messages,
            })

        return JsonResponse({
            'is_valid': True,
            'errors': [],
        })


def _normalize_auto_message(record):
    text = record.get('message') or record.get('text') or record.get('content') or ''
    author = record.get('author') or record.get('sender') or record.get('bot_name') or 'Chat SudaPlay'
    created_at = record.get('created_at') or record.get('timestamp') or ''
    return {
        'id': record.get('id') or record.get('uuid') or str(uuid.uuid4()),
        'text': text,
        'author': author,
        'created_at': created_at,
    }


def _fetch_supabase_messages():
    endpoint_url = (settings.SUPABASE_URL or '').rstrip('/')
    api_key = settings.SUPABASE_ANON_KEY
    table_name = settings.SUPABASE_CHAT_TABLE or 'auto_messages'

    if not (endpoint_url and api_key and table_name):
        return []

    url = f"{endpoint_url}/rest/v1/{table_name}"
    headers = {
        'apikey': api_key,
        'Authorization': f"Bearer {api_key}",
        'Accept': 'application/json',
    }
    params = {
        'select': 'id,message,created_at,author,text,content,timestamp,sender',
        'order': 'created_at.desc',
        'limit': 8,
    }

    try:
        response = requests.get(url, headers=headers, params=params, timeout=5)
        if response.ok:
            records = response.json()
            return [_normalize_auto_message(record) for record in records]
    except requests.RequestException:
        pass

    return []


class AutoMessagesAPIView(View):
    """
    API para retornar mensajes automáticos desde Supabase (o plantillas de fallback).
    """

    def get(self, request, *args, **kwargs):
        messages = _fetch_supabase_messages()
        if not messages:
            messages = [
                {'id': 'fallback-1', 'text': 'Bienvenido a SudaPlay, ¿quieres ver los juegos más recientes?', 'author': 'Chat SudaPlay', 'created_at': ''},
                {'id': 'fallback-2', 'text': 'Actualiza tu perfil para aparecer en la lista de creadores.', 'author': 'Chat SudaPlay', 'created_at': ''},
                {'id': 'fallback-3', 'text': 'Publica tu próximo lanzamiento y recibirás notificaciones.', 'author': 'Chat SudaPlay', 'created_at': ''},
            ]
        return JsonResponse({'messages': messages})


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
        results = []

        if query:
            # Buscar usuarios cuyo username contenga el término, excluyendo al usuario actual
            results = User.objects.filter(
                username__icontains=query,
                is_active=True
            ).exclude(id=request.user.id).select_related('profile')

        context = {
            'query': query,
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
        user_games = Game.objects.filter(uploaded_by=target_user, is_approved=True).order_by('-created_at')

        # Determinar el estado de amistad
        friendship_status = 'none' # none, pending_sent, pending_received, friends
        
        if my_profile.friends.filter(id=profile.id).exists():
            friendship_status = 'friends'
        elif FriendRequest.objects.filter(from_user=request.user, to_user=target_user).exists():
            friendship_status = 'pending_sent'
        elif FriendRequest.objects.filter(from_user=target_user, to_user=request.user).exists():
            friendship_status = 'pending_received'

        context = {
            'target_user': target_user,
            'profile': profile,
            'user_games': user_games,
            'friendship_status': friendship_status,
        }
        return render(request, self.template_name, context)


class SendFriendRequestAPIView(View):
    """API para enviar una solicitud de amistad."""
    @method_decorator(login_required(login_url='login:login'))
    def post(self, request, *args, **kwargs):
        import json
        from django.shortcuts import get_object_or_404
        try:
            data = json.loads(request.body)
            to_user_id = data.get('to_user_id')
            to_user = get_object_or_404(User, id=to_user_id)

            if to_user == request.user:
                return JsonResponse({'success': False, 'error': 'No puedes enviarte una solicitud a ti mismo.'})

            # Prevent trying to access non-existent profiles directly
            try:
                my_profile = request.user.profile
            except User.profile.RelatedObjectDoesNotExist:
                from .models import UserProfile
                my_profile = UserProfile.objects.create(user=request.user)
                
            try:
                target_profile = to_user.profile
            except User.profile.RelatedObjectDoesNotExist:
                from .models import UserProfile
                target_profile = UserProfile.objects.create(user=to_user)

            # Check if already friends
            if my_profile.friends.filter(id=target_profile.id).exists():
                return JsonResponse({'success': False, 'error': 'Ya son amigos.'})

            # Check if request already exists in either direction
            if FriendRequest.objects.filter(from_user=request.user, to_user=to_user).exists():
                 return JsonResponse({'success': False, 'error': 'Solicitud ya enviada.'})
            
            if FriendRequest.objects.filter(from_user=to_user, to_user=request.user).exists():
                 return JsonResponse({'success': False, 'error': 'Este usuario ya te ha enviado una solicitud.'})

            FriendRequest.objects.create(from_user=request.user, to_user=to_user)
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


class AcceptFriendRequestAPIView(View):
    """API para aceptar una solicitud de amistad."""
    @method_decorator(login_required(login_url='login:login'))
    def post(self, request, *args, **kwargs):
        import json
        from django.shortcuts import get_object_or_404
        try:
            data = json.loads(request.body)
            request_id = data.get('request_id')
            friend_request = get_object_or_404(FriendRequest, id=request_id, to_user=request.user)

            # Add to each other's friends list
            try:
                my_profile = request.user.profile
            except User.profile.RelatedObjectDoesNotExist:
                from .models import UserProfile
                my_profile = UserProfile.objects.create(user=request.user)
                
            try:
                from_profile = friend_request.from_user.profile
            except User.profile.RelatedObjectDoesNotExist:
                from .models import UserProfile
                from_profile = UserProfile.objects.create(user=friend_request.from_user)

            my_profile.friends.add(from_profile)
            
            # Delete the request
            friend_request.delete()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


class RejectFriendRequestAPIView(View):
    """API para rechazar o cancelar una solicitud de amistad."""
    @method_decorator(login_required(login_url='login:login'))
    def post(self, request, *args, **kwargs):
        import json
        from django.shortcuts import get_object_or_404
        try:
            data = json.loads(request.body)
            request_id = data.get('request_id')
            # User can cancel sent request or reject received request
            friend_request = get_object_or_404(FriendRequest, id=request_id)
            if friend_request.to_user == request.user or friend_request.from_user == request.user:
                friend_request.delete()
                return JsonResponse({'success': True})
            return JsonResponse({'success': False, 'error': 'No autorizado.'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})

class RemoveFriendAPIView(View):
    """API para eliminar a un usuario de la lista de amigos."""
    @method_decorator(login_required(login_url='login:login'))
    def post(self, request, *args, **kwargs):
        import json
        from django.shortcuts import get_object_or_404
        try:
            data = json.loads(request.body)
            friend_id = data.get('friend_id')
            friend_user = get_object_or_404(User, id=friend_id)

            try:
                my_profile = request.user.profile
            except User.profile.RelatedObjectDoesNotExist:
                from .models import UserProfile
                my_profile = UserProfile.objects.create(user=request.user)
                
            try:
                target_profile = friend_user.profile
            except User.profile.RelatedObjectDoesNotExist:
                from .models import UserProfile
                target_profile = UserProfile.objects.create(user=friend_user)

            if my_profile.friends.filter(id=target_profile.id).exists():
                my_profile.friends.remove(target_profile)
                return JsonResponse({'success': True})
            
            return JsonResponse({'success': False, 'error': 'No son amigos.'})
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})


