"""
Vistas para la aplicacion login.

Mejores practicas:
- Usar Class-Based Views (CBV)
- Validacion con formularios Django
- Manejo de mensajes
- Decoradores de autenticacion
"""
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

from .forms import RegisterForm, ProfileUpdateForm
from .models import UserProfile


class LoginView(FormView):
    """
    Vista para login de usuarios.
    Usa el formulario de autenticacion de Django.
    """

    template_name = 'login/login.html'
    form_class = AuthenticationForm
    success_url = reverse_lazy('web:home')

    def form_valid(self, form):
        """Autenticar usuario si el formulario es valido."""
        user = form.get_user()
        auth_login(self.request, user)
        return super().form_valid(form)

    def form_invalid(self, form):
        """Mostrar error si el formulario no es valido."""
        return super().form_invalid(form)

    def get(self, request, *args, **kwargs):
        """Redirigir a home si ya esta autenticado."""
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
        """Guardar nuevo usuario si el formulario es valido."""
        form.save()
        return super().form_valid(form)

    def form_invalid(self, form):
        """Mostrar errores si el formulario no es valido."""
        return super().form_invalid(form)

    def get(self, request, *args, **kwargs):
        """Redirigir a home si ya esta autenticado."""
        if request.user.is_authenticated:
            return redirect('web:home')
        return super().get(request, *args, **kwargs)


class LogoutView(View):
    """
    Vista para logout de usuarios.
    Cierra la sesion del usuario y redirige al login.
    """

    def get(self, request):
        """Cerrar sesion del usuario."""
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

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['instance'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.save()
        messages.success(self.request, 'Perfil actualizado correctamente.')
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        profile = UserProfile.objects.filter(user=self.request.user).first()
        context['current_avatar_url'] = profile.avatar.url if profile and profile.avatar else ''
        return context


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
    API endpoint para validar contrasena en tiempo real usando validadores Django.
    """

    def get(self, request, *args, **kwargs):
        password = request.GET.get('password', '') or ''
        username = request.GET.get('username', '') or ''
        email = request.GET.get('email', '') or ''

        if not password:
            return JsonResponse({
                'is_valid': False,
                'errors': ['La contrasena no puede estar vacia.'],
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
