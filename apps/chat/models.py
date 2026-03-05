from django.db import models
from django.contrib.auth.models import User

class ChatMessage(models.Model):
    """
    Modelo para los mensajes de chat entre dos usuarios.
    Migrado desde la app login.
    """
    sender = models.ForeignKey(User, related_name='sent_messages', on_delete=models.CASCADE)
    receiver = models.ForeignKey(User, related_name='received_messages', on_delete=models.CASCADE)
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        verbose_name = "Mensaje de Chat"
        verbose_name_plural = "Mensajes de Chat"
        ordering = ['timestamp']
        indexes = [
            models.Index(fields=['receiver', 'is_read'], name='idx_receiver_unread'),
            models.Index(fields=['sender', 'receiver'], name='idx_chat_conversation'),
        ]

    def __str__(self):
        return f"De {self.sender.username} para {self.receiver.username} ({self.timestamp})"

class Perfil(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    avatar_base64 = models.TextField(blank=True, null=True)  # Guardaremos la imagen en Base64

    def __str__(self):
        return f"Perfil de {self.user.username}"

    def get_avatar_url(self):
        if self.avatar_base64:
            return f"data:image/png;base64,{self.avatar_base64}"
        return ""


# Señal para crear automáticamente un perfil cuando se crea un usuario
from django.db.models.signals import post_save
from django.dispatch import receiver

@receiver(post_save, sender=User)
def crear_perfil(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.create(user=instance)