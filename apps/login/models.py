"""
Modelos para la aplicación login.

Se extiende el modelo User de Django para agregar campos personalizados.
"""
from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    """
    Perfil de usuario extendido.
    Relacionado 1:1 con el modelo User de Django.
    """
    ROLE_CHOICES = [
        ('user', 'Usuario Regular'),
        ('admin', 'Administrador'),
        ('moderator', 'Moderador'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, help_text="Biografía del usuario")
    avatar = models.ImageField(upload_to='avatars/', default='avatars/default.png', help_text="Foto de perfil")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='user')
    is_verified = models.BooleanField(default=False, help_text="¿Email verificado?")
    phone = models.CharField(max_length=20, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    friends = models.ManyToManyField('self', blank=True, symmetrical=True, help_text="Amigos del usuario")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuarios"
        ordering = ['-created_at']

    def __str__(self):
        return f"Perfil de {self.user.username}"
    
    def is_admin(self):
        """Verificar si el usuario es administrador."""
        return self.role == 'admin'


class FriendRequest(models.Model):
    """
    Modelo para gestionar las solicitudes de amistad entre usuarios.
    """
    from_user = models.ForeignKey(User, related_name='sent_friend_requests', on_delete=models.CASCADE)
    to_user = models.ForeignKey(User, related_name='received_friend_requests', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Solicitud de Amistad"
        verbose_name_plural = "Solicitudes de Amistad"
        unique_together = ('from_user', 'to_user')

    def __str__(self):
        return f"{self.from_user.username} -> {self.to_user.username}"
