"""
Formularios para la aplicación login de SudaPlay.
Incluye validaciones personalizadas y soporte para registro social.
"""
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile
from django.conf import settings
from pathlib import Path
from allauth.socialaccount.forms import SignupForm
from .models import UserProfile

class RegisterForm(UserCreationForm):
    """Formulario para registro manual estándar."""
    email = forms.EmailField(
        label='Correo electrónico',
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'})
    )
    username = forms.CharField(
        label='Apodo',
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apodo'})
    )
    password1 = forms.CharField(
        label='Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contraseña'})
    )
    password2 = forms.CharField(
        label='Confirmar contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmar contraseña'})
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Este correo electrónico ya está registrado.')
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError('Este nombre de usuario ya existe.')
        return username

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password1')
        p2 = cleaned_data.get('password2')
        if p1 and p2:
            if p1 != p2:
                self.add_error('password2', 'Las contraseñas no coinciden.')
            elif len(p1) < 8:
                self.add_error('password1', 'La contraseña debe tener al menos 8 caracteres.')
        return cleaned_data

class CustomSocialSignupForm(SignupForm):
    """Formulario para finalizar el registro social (Google)."""
    password1 = forms.CharField(
        label='Nueva Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Mínimo 8 caracteres', 'id': 'id_password1'}),
        required=True
    )
    password2 = forms.CharField(
        label='Confirmar Contraseña',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Repite tu contraseña', 'id': 'id_password2'}),
        required=True
    )

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password1')
        p2 = cleaned_data.get('password2')
        if p1 and p2:
            if p1 != p2:
                self.add_error('password2', 'Las contraseñas no coinciden.')
            elif len(p1) < 8:
                self.add_error('password1', 'La contraseña debe tener al menos 8 caracteres.')
        return cleaned_data

    def save(self, request):
        user = super().save(request)
        password = self.cleaned_data.get('password1')
        user.set_password(password)
        user.save()
        return user


class ProfileUpdateForm(forms.ModelForm):
    """Formulario para editar apodo/correo e imagen de perfil."""
    avatar = forms.ImageField(
        label='Imagen de perfil',
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control', 'accept': 'image/*'})
    )
    avatar_choice = forms.CharField(
        required=False,
        widget=forms.HiddenInput()
    )

    class Meta:
        model = User
        fields = ('username', 'email')
        labels = {
            'username': 'Apodo',
            'email': 'Correo electrónico',
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apodo'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electrónico'}),
        }

    def __init__(self, *args, **kwargs):
        self.available_avatars = kwargs.pop('available_avatars', [])
        super().__init__(*args, **kwargs)
        self.order_fields(['username', 'email', 'avatar', 'avatar_choice'])
        self.fields['avatar_choice'].initial = ''

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if User.objects.filter(username__iexact=username).exclude(pk=self.instance.pk).exists():
            raise ValidationError('Este nombre de usuario ya existe.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError('Este correo electrónico ya está registrado.')
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            profile, _ = UserProfile.objects.get_or_create(user=user)
            avatar = self.cleaned_data.get('avatar')
            avatar_choice = self.cleaned_data.get('avatar_choice')
            if avatar_choice and avatar_choice in self.available_avatars:
                avatars_root = Path(settings.BASE_DIR) / 'static' / 'avatars'
                avatar_path = avatars_root / avatar_choice
                if avatar_path.exists():
                    with avatar_path.open('rb') as avatar_file:
                        profile.avatar.save(avatar_choice, ContentFile(avatar_file.read()), save=False)
            if avatar:
                profile.avatar = avatar
            profile.save()
        return user
