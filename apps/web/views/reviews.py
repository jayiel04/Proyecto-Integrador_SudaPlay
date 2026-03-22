"""
Vistas de moderación y revisión de juegos
"""
from django.conf import settings
from .base import RoleRequiredMixin
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
from apps.web.forms import GameForm
from apps.web.models import Game, GameRating
from apps.web.services import process_uploaded_web_build_async
from apps.login.models import Notification
from django.contrib.auth.mixins import UserPassesTestMixin
import os

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

