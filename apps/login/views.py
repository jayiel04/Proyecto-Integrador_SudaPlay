"""
Vistas para la aplicación login.

Mejores prácticas:
- Usar Class-Based Views (CBV)
- Validación con formularios Django
- Manejo de mensajes
- Decoradores de autenticación
"""
from django.shortcuts import render, redirect
from django.views import View
from django.views.generic import FormView
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib import messages
from django.urls import reverse_lazy
from django.contrib.auth.forms import AuthenticationForm
from .forms import RegisterForm


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
        messages.success(self.request, f'¡Bienvenido {user.first_name or user.username}!')
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """Mostrar error si el formulario no es válido."""
        messages.error(self.request, 'Usuario o contraseña inválidos')
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
        user = form.save()
        messages.success(
            self.request,
            f'¡Bienvenido {user.first_name}! Tu cuenta ha sido creada. Por favor inicia sesión.'
        )
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """Mostrar errores si el formulario no es válido."""
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, f'{field}: {error}')
        return super().form_invalid(form)
    
    def get(self, request, *args, **kwargs):
        """Redirigir a home si ya está autenticado."""
        if request.user.is_authenticated:
            return redirect('web:home')
        return super().get(request, *args, **kwargs)


class LogoutView(View):
    """
    Vista para logout de usuarios.
    Cierra la sesión del usuario y muestra un mensaje de despedida.
    """
    
    def get(self, request):
        """Cerrar sesión del usuario."""
        username = request.user.username if request.user.is_authenticated else 'Usuario'
        auth_logout(request)
        messages.success(request, f'¡Hasta luego {username}! Tu sesión ha sido cerrada.')
        return redirect('web:home')


from django.http import JsonResponse
from django.contrib.auth.models import User

class CheckUserAPIView(View):
    """
    API endpoint para verificar disponibilidad de usuario/email en tiempo real.
    """
    def get(self, request, *args, **kwargs):
        username = request.GET.get('username', None)
        email = request.GET.get('email', None)
        response = {
            'is_taken': False
        }
        
        if username:
            if User.objects.filter(username__iexact=username).exists():
                response['is_taken'] = True
                response['error_message'] = 'Este nombre de usuario ya está en uso.'
        
        elif email:
            if User.objects.filter(email__iexact=email).exists():
                response['is_taken'] = True
                response['error_message'] = 'Este correo electrónico ya está registrado.'
        
        return JsonResponse(response)

