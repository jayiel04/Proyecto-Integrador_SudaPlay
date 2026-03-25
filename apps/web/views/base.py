"""
Vistas base (Inicio, Reglas, Acerca de)
"""
from django.conf import settings
from django.contrib import messages
from django.shortcuts import redirect
from django.http import FileResponse, Http404, HttpResponse
from django.views import View
from django.views.generic import TemplateView
from django.views.generic import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import F, Q, Count, Case, When, IntegerField
from django.contrib.auth.models import User
from decimal import Decimal, ROUND_HALF_UP
from django.core.cache import cache
from django.core.paginator import Paginator
from apps.web.forms import GameForm
from apps.web.models import Game, GameRating
from apps.web.services import process_uploaded_web_build_async
from apps.login.models import Notification
from django.contrib.auth.mixins import UserPassesTestMixin
import os

class HomeView(TemplateView):
    """
    Vista para la página de inicio.
    Muestra el catálogo de juegos publicado.
    """
    template_name = "web/home.html"

    def get_context_data(self, **kwargs):
        """Pasar contexto adicional al template."""
        context = super().get_context_data(**kwargs)
        query = (self.request.GET.get("q") or "").strip()
        page_number = self.request.GET.get("page")

        games_qs = (
            Game.objects
            .filter(is_approved=True)
            .select_related('uploaded_by')
            .only(
                'pk', 'title', 'description', 'short_description', 'cover_image',
                'views', 'downloads', 'rating', 'is_featured',
                'is_processing', 'is_web_playable', 'game_file',
                'uploaded_by__username'
            )
        )

        if query:
            games_qs = games_qs.filter(
                Q(title__icontains=query)
                | Q(short_description__icontains=query)
                | Q(description__icontains=query)
                | Q(uploaded_by__username__icontains=query)
            )

        paginator = Paginator(games_qs, 12)
        page_obj = paginator.get_page(page_number)

        context['user'] = self.request.user
        context['username'] = self.request.user.username
        context["games"] = page_obj.object_list
        context["page_obj"] = page_obj
        context["catalog_query"] = query
        context["is_paginated"] = page_obj.has_other_pages()
        context["show_post_login_welcome"] = self.request.session.pop("show_post_login_welcome", False)
        return context

class AboutView(TemplateView):
    """
    Vista para la pagina Acerca de.
    """
    template_name = "web/about.html"

class NormasView(TemplateView):
    """
    Vista para las Normas de Convivencia.
    """
    template_name = "web/normas.html"

class AdvancedAudioSettingsView(TemplateView):
    """
    Vista para configuraciones avanzadas de sonido.
    """
    template_name = "web/advanced_audio_settings.html"
    _AUDIO_CACHE_KEY = 'supabase_audio_list'
    _AUDIO_CACHE_TTL = 600  # 10 minutos — el listado cambia rara vez

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        import urllib.parse
        from decouple import config
        from supabase import create_client

        # Intentar devolver desde caché primero
        cached_audio = cache.get(self._AUDIO_CACHE_KEY)
        if cached_audio is not None:
            context['audio_files'] = cached_audio
            return context

        try:
            service_role_key = config('SUPABASE_SERVICE_ROLE_KEY', default=settings.SUPABASE_KEY)
            admin_supabase = create_client(settings.SUPABASE_URL, service_role_key)
            response = admin_supabase.storage.from_("musica").list("audio")
            
            audio_files = []
            for item in response:
                name = item.get('name', '')
                if name and name != '.emptyFolderPlaceholder':
                    # Ensure we don't duplicate the folder prefix if Supabase returns absolute paths
                    if name.startswith('audio/'):
                        name = name[len('audio/'):]
                    
                    if not name:
                        continue

                    # Beautify display name
                    display_name = name.rsplit('.', 1)[0].replace('-', ' ').replace('_', ' ').title()
                    
                    audio_files.append({
                        'name': name,
                        'display_name': display_name,
                        'url': f"{settings.SUPABASE_URL}/storage/v1/object/public/musica/audio/{urllib.parse.quote(name)}"
                    })
            cache.set(self._AUDIO_CACHE_KEY, audio_files, timeout=self._AUDIO_CACHE_TTL)
            context['audio_files'] = audio_files
        except Exception as e:
            print(f"Error fetching audio files from supabase: {e}")
            context['audio_files'] = []
        return context

class RoleRequiredMixin(UserPassesTestMixin):
    """Mixin que permite la entrada solo a usuarios con rol admin o moderator."""
    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            return False
        role = getattr(user.profile, 'role', 'user') if hasattr(user, 'profile') else 'user'
        return role in ['admin', 'moderator']

