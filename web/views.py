"""
Vistas para la aplicación web.

Mejores prácticas:
- Usar Class-Based Views (CBV)
- Decoradores de autenticación
- Templates centralizados
"""
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


class HomeView(TemplateView):
    """
    Vista para la página de inicio.
    Redirige a login si no está autenticado.
    """
    template_name = 'home.html'
    
    @method_decorator(login_required(login_url='login:login'))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        """Pasar contexto adicional al template."""
        context = super().get_context_data(**kwargs)
        context['user'] = self.request.user
        return context

