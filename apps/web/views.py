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
from django.http import FileResponse, Http404
from django.views import View
from django.views.generic import TemplateView
from django.views.generic import DetailView
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.db.models import F, Q
from decimal import Decimal, ROUND_HALF_UP

from .forms import GameForm
from .models import Game, GameRating
from .services import process_uploaded_web_build


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
        context["games"] = Game.objects.filter(is_approved=True)
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


class GameCreateView(LoginRequiredMixin, CreateView):
    template_name = "web/game_form.html"
    form_class = GameForm
    success_url = reverse_lazy("web:home")
    login_url = "login:login"

    def form_valid(self, form):
        form.instance.uploaded_by = self.request.user
        # Publicacion inmediata para que otros usuarios puedan jugar al instante.
        form.instance.is_approved = True
        response = super().form_valid(form)

        if self.object.game_file:
            ok, error_message = process_uploaded_web_build(self.object)
            if not ok:
                self.object.delete()
                messages.error(self.request, f"No se pudo publicar el juego: {error_message}")
                return redirect("web:game_create")

        messages.success(self.request, "Juego publicado y disponible para jugar.")

        return response


class MyGamesView(LoginRequiredMixin, TemplateView):
    """
    Vista para listar todos los juegos creados por el usuario autenticado.
    """
    template_name = "web/my_games.html"
    login_url = "login:login"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["games"] = Game.objects.filter(uploaded_by=self.request.user)
        return context


class GameDetailView(DetailView):
    model = Game
    template_name = "web/game_detail.html"
    context_object_name = "game"

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Game.objects.filter(Q(is_approved=True) | Q(uploaded_by=self.request.user)).distinct()
        return Game.objects.filter(is_approved=True)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        game = context["game"]
        play_url = ""
        play_mode = "unavailable"

        if game.is_approved:
            if game.is_web_playable and game.web_build_path:
                play_url = f"{settings.MEDIA_URL}{game.web_build_path}"
                play_mode = "embedded"
            elif game.external_url:
                play_url = game.external_url
                play_mode = "external"

        context["play_url"] = play_url
        context["play_mode"] = play_mode
        context["can_play"] = play_mode in ("embedded", "external")
        context["is_owner"] = self.request.user.is_authenticated and game.uploaded_by_id == self.request.user.id
        return context


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

        messages.success(request, "Gracias por calificar este juego.")
        return redirect("web:game_play", pk=self.object.pk)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        game = context["game"]
        play_url = ""
        play_mode = "unavailable"

        if game.is_web_playable and game.web_build_path:
            play_url = f"{settings.MEDIA_URL}{game.web_build_path}"
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

