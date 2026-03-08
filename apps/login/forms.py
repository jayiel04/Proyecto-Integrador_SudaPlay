"""
Formularios para la aplicacion login de SudaPlay.
Incluye validaciones personalizadas y soporte para registro social.
"""
from pathlib import Path

from allauth.socialaccount.forms import SignupForm
from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.files.base import ContentFile

from .models import UserProfile


class RegisterForm(UserCreationForm):
    """Formulario para registro manual estandar."""

    email = forms.EmailField(
        label='Correo electronico',
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electronico'}),
    )
    username = forms.CharField(
        label='Apodo',
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apodo'}),
    )
    password1 = forms.CharField(
        label='Contrasena',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Contrasena'}),
    )
    password2 = forms.CharField(
        label='Confirmar contrasena',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirmar contrasena'}),
    )

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('Este correo electronico ya esta registrado.')
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
                self.add_error('password2', 'Las contrasenas no coinciden.')
            elif len(p1) < 8:
                self.add_error('password1', 'La contrasena debe tener al menos 8 caracteres.')
        return cleaned_data


class CustomSocialSignupForm(SignupForm):
    """Formulario para finalizar el registro social (Google)."""

    password1 = forms.CharField(
        label='Nueva Contrasena',
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Minimo 8 caracteres', 'id': 'id_password1'}
        ),
        required=True,
    )
    password2 = forms.CharField(
        label='Confirmar Contrasena',
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': 'Repite tu contrasena', 'id': 'id_password2'}
        ),
        required=True,
    )

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password1')
        p2 = cleaned_data.get('password2')
        if p1 and p2:
            if p1 != p2:
                self.add_error('password2', 'Las contrasenas no coinciden.')
            elif len(p1) < 8:
                self.add_error('password1', 'La contrasena debe tener al menos 8 caracteres.')
        return cleaned_data

    def save(self, request):
        user = super().save(request)
        password = self.cleaned_data.get('password1')
        user.set_password(password)
        user.save()
        return user


class ProfileUpdateForm(forms.ModelForm):
    """Formulario para editar apodo/correo, avatar predefinido y descripcion."""

    bio = forms.CharField(
        label='Descripcion',
        required=False,
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'placeholder': 'Cuentanos algo sobre ti',
                'rows': 3,
                'style': 'resize: vertical;',
            }
        ),
    )
    avatar_choice = forms.CharField(required=False, widget=forms.HiddenInput())

    class Meta:
        model = User
        fields = ('username', 'email')
        labels = {
            'username': 'Apodo',
            'email': 'Correo electronico',
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Apodo'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Correo electronico'}),
        }

    def __init__(self, *args, **kwargs):
        self.available_avatars = kwargs.pop('available_avatars', [])
        super().__init__(*args, **kwargs)
        self.order_fields(['username', 'email', 'bio', 'avatar_choice'])

        profile = None
        if self.instance:
            profile = getattr(self.instance, 'profile', None)
            if not profile and self.instance.pk:
                profile, _ = UserProfile.objects.get_or_create(user=self.instance)

        if profile:
            self.fields['bio'].initial = profile.bio
            current_avatar_name = Path(getattr(profile.avatar, 'name', '')).name
            self.fields['avatar_choice'].initial = current_avatar_name if current_avatar_name in self.available_avatars else ''
        else:
            self.fields['avatar_choice'].initial = ''

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if User.objects.filter(username__iexact=username).exclude(pk=self.instance.pk).exists():
            raise ValidationError('Este nombre de usuario ya existe.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        if User.objects.filter(email__iexact=email).exclude(pk=self.instance.pk).exists():
            raise ValidationError('Este correo electronico ya esta registrado.')
        return email

    def clean_avatar_choice(self):
        avatar_choice = Path((self.cleaned_data.get('avatar_choice') or '').strip()).name
        if avatar_choice and avatar_choice not in self.available_avatars:
            raise ValidationError('El avatar seleccionado no es valido.')
        return avatar_choice

    def save(self, commit=True):
        user = super().save(commit=False)
        if not commit:
            return user

        user.save()
        profile, _ = UserProfile.objects.get_or_create(user=user)

        avatar_choice = self.cleaned_data.get('avatar_choice')
        if avatar_choice and avatar_choice in self.available_avatars:
            avatars_root = Path(settings.BASE_DIR) / 'static' / 'avatars'
            avatar_path = avatars_root / avatar_choice
            if avatar_path.exists():
                current_avatar_name = Path(getattr(profile.avatar, 'name', '')).name
                if current_avatar_name != avatar_choice:
                    with avatar_path.open('rb') as avatar_file:
                        profile.avatar.save(avatar_choice, ContentFile(avatar_file.read()), save=False)
        else:
            current_avatar_name = Path(getattr(profile.avatar, 'name', '')).name
            if current_avatar_name and current_avatar_name not in self.available_avatars:
                fallback = 'sonriente.png' if 'sonriente.png' in self.available_avatars else (
                    self.available_avatars[0] if self.available_avatars else ''
                )
                if fallback:
                    fallback_path = Path(settings.BASE_DIR) / 'static' / 'avatars' / fallback
                    if fallback_path.exists():
                        with fallback_path.open('rb') as avatar_file:
                            profile.avatar.save(fallback, ContentFile(avatar_file.read()), save=False)
                else:
                    profile.avatar = None

        profile.bio = self.cleaned_data.get('bio', '').strip()
        profile.save()
        return user
