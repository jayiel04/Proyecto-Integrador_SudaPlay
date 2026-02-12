"""
Formularios para la aplicación login.

Incluye formularios personalizados con validaciones adicionales.
"""
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError


class RegisterForm(UserCreationForm):
    """
    Formulario personalizado para registro de usuarios.
    Extiende UserCreationForm con campos adicionales.
    """
    email = forms.EmailField(
        label='Correo electrónico',
        required=True,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Correo electrónico'
        })
    )
    username = forms.CharField(
        label='Apodo',
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Apodo'
        })
    )
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Contraseña'
        })
    )
    password2 = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirmar contraseña'
        })
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        """Validar que el email no esté ya registrado."""
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Este correo electrónico ya está registrado.')
        return email

    def clean_username(self):
        """Validar que el username no esté ya registrado."""
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError('Este nombre de usuario ya existe.')
        return username

    def clean(self):
        """Validación adicional del formulario completo."""
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2:
            if password1 != password2:
                self.add_error('password2', 'Las contraseñas no coinciden.')
            elif len(password1) < 8:
                self.add_error('password1', 'La contraseña debe tener al menos 8 caracteres.')

        return cleaned_data
