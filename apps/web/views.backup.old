"""
Vistas para la aplicación web.

Mejores prácticas:
- Usar Class-Based Views (CBV)
- Decoradores de autenticación
- Templates centralizados
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

from .forms import GameForm
from .models import Game, GameRating
from .services import process_uploaded_web_build_async
from apps.login.models import Notification


class HomeView(TemplateView):
    """
    Vista para la página de inicio.
    Muestra el catálogo de juegos publicado.
    """
    template_name = "web/home.html"

    def get_context_data(self, **kwargs):
        """Pasar contexto adicional al template."""
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        context['username'] = self.request.user.username
        context["games"] = (
            Game.objects
            .filter(is_approved=True)
            .select_related('uploaded_by')
            .only('pk', 'title', 'short_description', 'cover_image',
                  'downloads', 'rating', 'is_featured', 'uploaded_by')
        )
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


class GameCreateView(LoginRequiredMixin, CreateView):
    template_name = "web/game_form.html"
    form_class = GameForm
    success_url = reverse_lazy("web:home")
    login_url = "login:login"

    def form_valid(self, form):
        form.instance.uploaded_by = self.request.user
        
        # Solo aprueba automáticamente si es admin o moderador
        user_role = getattr(self.request.user.profile, 'role', 'user') if hasattr(self.request.user, 'profile') else 'user'
        if user_role in ['admin', 'moderator']:
            form.instance.is_approved = True
            success_msg = "Juego publicado y disponible."
        else:
            form.instance.is_approved = False
            success_msg = "Juego subido para revisión. Será publicado cuando un moderador lo apruebe."
            
            # Notificar a los administradores/moderadores
            admins_mods = User.objects.filter(profile__role__in=['admin', 'moderator'])
            for am in admins_mods:
                Notification.objects.create(
                    user=am,
                    message=f"Nuevo juego '{form.instance.title}' pendiente de revisión.",
                    url=str(reverse_lazy('web:review_games'))
                )
                cache.delete(f'notifications_{am.id}')



        # Si hay un ZIP, intercepción: guardarlo localmente (instantáneo)
        # en vez de subir a Supabase S3 durante el request (10+ seg).
        if form.cleaned_data.get("game_file"):
            from .storage_backends import GameTempFilesStorage
            from django.core.files.storage import default_storage
            uploaded_file = form.cleaned_data["game_file"]
            temp_storage = GameTempFilesStorage()
            temp_name = temp_storage.save(uploaded_file.name, uploaded_file)
            temp_path = temp_storage.path(temp_name)
            # Guardar el juego SIN el game_file por ahora (se asignará en el worker)
            form.instance.game_file = None
            self.object = form.save()
        else:
            temp_path = None
            self.object = form.save()

        # Marcar como en procesamiento si la migración ya fue aplicada
        if temp_path:
            try:
                self.object.__class__.objects.filter(pk=self.object.pk).update(is_processing=True)
            except Exception:
                pass

        if temp_path:
            process_uploaded_web_build_async(self.object.pk, temp_path=temp_path)
            messages.success(
                self.request,
                "¡Juego recibido! Estamos procesando el archivo ZIP, en unos momentos se completará." if form.instance.is_approved else success_msg
            )
        else:
            messages.success(self.request, success_msg)

        return redirect("web:home")


class MyGamesView(LoginRequiredMixin, TemplateView):
    """
    Vista para listar todos los juegos creados por el usuario autenticado.
    """
    template_name = "web/my_games.html"
    login_url = "login:login"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        games = Game.objects.filter(uploaded_by=self.request.user)

        # Una sola query con aggregate en vez de 6 queries separadas
        stats_agg = games.aggregate(
            total=Count('pk'),
            published=Count(Case(When(is_approved=True, is_rejected=False, then=1), output_field=IntegerField())),
            pending=Count(Case(When(is_approved=False, is_rejected=False, is_processing=False, processing_error='', then=1), output_field=IntegerField())),
            rejected=Count(Case(When(is_rejected=True, then=1), output_field=IntegerField())),
            processing=Count(Case(When(is_processing=True, then=1), output_field=IntegerField())),
            errored=Count(Case(When(is_processing=False, processing_error__gt='', then=1), output_field=IntegerField())),
        )

        # Querysets de visualización (evaluados en el template, no en Python)
        processing_games = games.filter(is_processing=True)
        errored_games = games.filter(processing_error__gt="", is_processing=False)
        review_games = games.filter(is_approved=False, is_rejected=False)
        published_games = games.filter(is_approved=True, is_rejected=False)

        context["games"] = games
        context["processing_games"] = processing_games
        context["errored_games"] = errored_games
        context["review_games"] = review_games
        context["published_games"] = published_games
        context["stats"] = stats_agg
        return context


class GameUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "web/game_form.html"
    form_class = GameForm
    login_url = "login:login"

    def get_queryset(self):
        return Game.objects.filter(uploaded_by=self.request.user)

    def get_success_url(self):
        return reverse_lazy("web:my_games")

    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.is_approved = False
        self.object.is_rejected = False
        self.object.processing_error = ""
        success_msg = "Cambios enviados a revisión. Se publicará tras la aprobación."

        admins_mods = User.objects.filter(profile__role__in=['admin', 'moderator'])
        for am in admins_mods:
            Notification.objects.create(
                user=am,
                message=f"Actualización de juego '{self.object.title}' pendiente de revisión.",
                url=str(reverse_lazy('web:review_games'))
            )
            cache.delete(f'notifications_{am.id}')

        temp_path = None
        uploaded_file = form.cleaned_data.get("game_file")
        if uploaded_file:
            from .storage_backends import GameTempFilesStorage
            temp_storage = GameTempFilesStorage()
            temp_name = temp_storage.save(uploaded_file.name, uploaded_file)
            temp_path = temp_storage.path(temp_name)
            # Evitar guardar el archivo final aún
            self.object.game_file = None
            self.object.save()
            try:
                self.object.__class__.objects.filter(pk=self.object.pk).update(is_processing=True)
            except Exception:
                pass
        else:
            self.object.is_processing = False
            self.object.save()

        if temp_path:
            process_uploaded_web_build_async(self.object.pk, temp_path=temp_path)
            messages.success(
                self.request,
                "Actualización recibida. Procesamos el ZIP y pasará a revisión en minutos."
            )
        else:
            messages.success(self.request, success_msg)

        return redirect(self.get_success_url())


from django.contrib.auth.mixins import UserPassesTestMixin
import os

class RoleRequiredMixin(UserPassesTestMixin):
    """Mixin que permite la entrada solo a usuarios con rol admin o moderator."""
    def test_func(self):
        user = self.request.user
        if not user.is_authenticated:
            return False
        role = getattr(user.profile, 'role', 'user') if hasattr(user, 'profile') else 'user'
        return role in ['admin', 'moderator']


class ReviewGamesView(LoginRequiredMixin, RoleRequiredMixin, TemplateView):
    """
    Vista para listar los juegos pendientes de revisión (is_approved=False).
    """
    template_name = "web/review_games.html"
    login_url = "login:login"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Mostrar juegos que no están aprobados Y no están rechazados
        context["games"] = Game.objects.filter(is_approved=False, is_rejected=False).select_related('uploaded_by')
        return context


class ApproveGameView(LoginRequiredMixin, RoleRequiredMixin, View):
    """
    Vista para aprobar un juego (POST).
    """
    login_url = "login:login"

    def post(self, request, pk):
        game = Game.objects.filter(pk=pk, is_approved=False).first()
        if not game:
            messages.error(request, "El juego no existe o ya ha sido aprobado.")
        else:
            game.is_approved = True
            game.save(update_fields=["is_approved"])
            
            # Notificar al autor
            Notification.objects.create(
                user=game.uploaded_by,
                message=f"¡Tu juego '{game.title}' ha sido aprobado y ya está disponible!",
                url=str(reverse_lazy('web:game_play', kwargs={'pk': game.pk}))
            )
            cache.delete(f'notifications_{game.uploaded_by_id}')
            
            messages.success(request, f"¡El juego '{game.title}' ha sido aprobado y publicado!")
            
        return redirect("web:review_games")


class RejectGameView(LoginRequiredMixin, RoleRequiredMixin, View):
    """
    Vista para rechazar (eliminar) un juego (POST).
    """
    login_url = "login:login"

    def post(self, request, pk):
        game = Game.objects.filter(pk=pk, is_approved=False, is_rejected=False).first()
        if not game:
            messages.error(request, "El juego no existe, ya ha sido aprobado o ya fue rechazado.")
        else:
            title = game.title
            uploader = game.uploaded_by
            reason = request.POST.get("rejection_reason", "").strip()
            
            if not reason:
                messages.error(request, "Debes proporcionar un motivo para rechazar el juego.")
                return redirect("web:review_games")

            game.is_rejected = True
            game.rejection_reason = reason
            game.save(update_fields=["is_rejected", "rejection_reason"])
            
            # Notificar al autor
            Notification.objects.create(
                user=uploader,
                message=f"Tu juego '{title}' ha sido rechazado. Motivo: {reason}",
                url=str(reverse_lazy('web:my_games'))
            )
            cache.delete(f'notifications_{uploader.id}')
            
            messages.success(request, f"El juego '{title}' ha sido rechazado.")
            
        return redirect("web:review_games")
class GamePlayView(DetailView):
    model = Game
    template_name = "web/game_play.html"
    context_object_name = "game"

    def get_queryset(self):
        return Game.objects.filter(is_approved=True)

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        Game.objects.filter(pk=self.object.pk).update(views=F("views") + 1)
        self.object.refresh_from_db(fields=["views"])
        return response

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if not request.user.is_authenticated:
            messages.info(request, "Debes iniciar sesión para calificar.")
            return redirect(f"{reverse_lazy('login:login')}?next={request.path}")

        try:
            rating_value = int(request.POST.get("rating", "").strip())
        except (TypeError, ValueError):
            messages.error(request, "Calificación inválida.")
            return redirect("web:game_play", pk=self.object.pk)

        if rating_value < 1 or rating_value > 5:
            messages.error(request, "La calificación debe estar entre 1 y 5.")
            return redirect("web:game_play", pk=self.object.pk)

        if GameRating.objects.filter(game=self.object, user=request.user).exists():
            messages.warning(request, "Ya calificaste este juego. Solo se permite una calificación por usuario.")
            return redirect("web:game_play", pk=self.object.pk)

        GameRating.objects.create(game=self.object, user=request.user, value=rating_value)

        votes_before = self.object.rating_votes
        total_before = self.object.rating * votes_before
        votes_after = votes_before + 1
        avg_after = (total_before + Decimal(rating_value)) / Decimal(votes_after)
        avg_after = avg_after.quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
        self.object.rating = avg_after
        self.object.rating_votes = votes_after
        self.object.save(update_fields=["rating", "rating_votes"])

        return redirect("web:game_play", pk=self.object.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        game = context["game"]
        play_url = ""
        play_mode = "unavailable"

        if game.is_web_playable and game.web_build_path:
            path = game.web_build_path
            if path.startswith("http"):
                # URL de Supabase: usar el proxy Django para corregir Content-Type
                from django.urls import reverse
                play_url = reverse("web:game_asset", kwargs={"pk": game.pk, "asset_path": "index.html"})
            else:
                play_url = f"{settings.MEDIA_URL}{path}"
            play_mode = "embedded"
        elif game.external_url:
            play_url = game.external_url
            play_mode = "external"

        user_rating = None
        if self.request.user.is_authenticated:
            user_rating = GameRating.objects.filter(game=game, user=self.request.user).values_list("value", flat=True).first()

        context["play_url"] = play_url
        context["play_mode"] = play_mode
        context["user_has_rated"] = user_rating is not None
        context["user_rating"] = user_rating
        return context


class GameDownloadView(LoginRequiredMixin, View):
    """
    Descarga del archivo ZIP del juego como archivo.zip.
    """
    login_url = "login:login"

    def get_queryset(self, request):
        return Game.objects.filter(Q(is_approved=True) | Q(uploaded_by=request.user)).distinct()

    def get(self, request, pk):
        game = self.get_queryset(request).filter(pk=pk).first()
        if not game:
            raise Http404("Juego no encontrado.")

        if not game.game_file:
            raise Http404("Este juego no tiene archivo descargable.")

        try:
            file_handle = game.game_file.open("rb")
        except FileNotFoundError:
            raise Http404("El archivo no está disponible en el servidor.")

        Game.objects.filter(pk=game.pk).update(downloads=F("downloads") + 1)
        return FileResponse(file_handle, as_attachment=True, filename="archivo.zip")


class GameAssetProxyView(View):
    """
    Proxy que descarga archivos del build de juego desde Supabase
    y los re-sirve al browser con el Content-Type MIME correcto.

    Supabase (tanto por S3 como por su API REST) siempre devuelve text/plain
    para todos los archivos, rompiendo el renderizado de HTML/JS/CSS en iframes.
    Este proxy corrige ese problema inyectando el header correcto desde Django.

    URL: /juegos/<pk>/asset/<path:asset_path>
    """

    MIME_MAP = {
        ".html": "text/html; charset=utf-8",
        ".htm":  "text/html; charset=utf-8",
        ".js":   "application/javascript",
        ".css":  "text/css",
        ".wasm": "application/wasm",
        ".json": "application/json",
        ".png":  "image/png",
        ".jpg":  "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif":  "image/gif",
        ".svg":  "image/svg+xml",
        ".ico":  "image/x-icon",
        ".mp3":  "audio/mpeg",
        ".ogg":  "audio/ogg",
        ".wav":  "audio/wav",
        ".mp4":  "video/mp4",
    }

    # TTL de caché por tipo de asset (segundos)
    _CACHE_TTL_DEFAULT = 300          # 5 min para HTML/JS/CSS del build
    _CACHE_TTL_IMMUTABLE = 3600       # 1 hora para imágenes, audio, wasm
    _IMMUTABLE_EXTS = {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.ico',
                       '.mp3', '.ogg', '.wav', '.mp4', '.wasm'}

    def get(self, request, pk, asset_path):
        import requests as req
        import mimetypes
        from pathlib import PurePosixPath

        # --- Caché de asset ---
        safe_path = asset_path.replace('/', '_').replace('..', '')
        cache_key = f'game_asset_{pk}_{safe_path}'
        cached = cache.get(cache_key)
        if cached is not None:
            content, content_type = cached
            response = HttpResponse(content, content_type=content_type)
            ext = PurePosixPath(asset_path).suffix.lower()
            if ext in self._IMMUTABLE_EXTS:
                response['Cache-Control'] = f'public, max-age={self._CACHE_TTL_IMMUTABLE}, immutable'
            else:
                response['Cache-Control'] = f'public, max-age={self._CACHE_TTL_DEFAULT}'
            return response

        game = Game.objects.filter(pk=pk).first()
        if not game or not game.web_build_path:
            raise Http404("Juego no encontrado")

        # Construir la URL base del build: quitar el nombre del archivo de web_build_path
        # web_build_path = https://.../object/public/juegos/games/builds/14/snake/index.html
        build_url = game.web_build_path
        base_url = build_url.rsplit("/", 1)[0]  # Quitar 'index.html'
        asset_url = f"{base_url}/{asset_path}"

        try:
            resp = req.get(asset_url, timeout=15)
            resp.raise_for_status()
        except Exception:
            raise Http404(f"Asset no encontrado: {asset_path}")

        # Determinar Content-Type por extensión (ignoramos lo que manda Supabase)
        ext = PurePosixPath(asset_path).suffix.lower()
        content_type = self.MIME_MAP.get(ext)
        if not content_type:
            content_type, _ = mimetypes.guess_type(asset_path)
        if not content_type:
            content_type = "application/octet-stream"

        # Guardar en caché (TTL mayor para assets binarios inmutables)
        ttl = self._CACHE_TTL_IMMUTABLE if ext in self._IMMUTABLE_EXTS else self._CACHE_TTL_DEFAULT
        cache.set(cache_key, (resp.content, content_type), timeout=ttl)

        response = HttpResponse(resp.content, content_type=content_type)
        # Cache-Control HTTP: el navegador guarda el asset localmente entre visitas
        if ext in self._IMMUTABLE_EXTS:
            response['Cache-Control'] = f'public, max-age={self._CACHE_TTL_IMMUTABLE}, immutable'
        else:
            response['Cache-Control'] = f'public, max-age={self._CACHE_TTL_DEFAULT}'
        return response
