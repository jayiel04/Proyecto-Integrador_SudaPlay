import json
from django.shortcuts import render, get_object_or_404, redirect
from django.views import View
from django.utils.decorators import method_decorator
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib import messages
from apps.login.models import UserProfile
from .models import ChatMessage
from django.db import models


class ChatInboxView(View):
    """Renderiza la página del Inbox principal o un chat en específico usando el modelo WhatsApp."""
    @method_decorator(login_required(login_url='login:login'))
    def get(self, request, username=None, *args, **kwargs):
        try:
            my_profile = request.user.profile
        except User.profile.RelatedObjectDoesNotExist:
            my_profile = UserProfile.objects.create(user=request.user)
            
        friends = my_profile.friends.all().select_related('user')
        
        target_user = None
        if username:
            target_user = get_object_or_404(User, username=username)
            
            try:
                target_profile = target_user.profile
            except User.profile.RelatedObjectDoesNotExist:
                target_profile = UserProfile.objects.create(user=target_user)

            # Check if they are friends
            if not my_profile.friends.filter(id=target_profile.id).exists():
                messages.warning(request, "Solo puedes chatear con tus amigos.")
                return redirect('chat:inbox')

        context = {
            'friends': friends,
            'target_user': target_user,
        }
        return render(request, 'chat/inbox.html', context)


class GetMessagesAPIView(View):
    """API para obtener mensajes recientes con un usuario específico (para el polling HTTP)."""
    @method_decorator(login_required(login_url='login:login'))
    def get(self, request, username, *args, **kwargs):
        target_user = get_object_or_404(User, username=username)
        
        # Opcionalmente, podemos recibir un "last_timestamp" u offset,
        # pero para simplicidad, mandaremos los ultimos 50 mensajes y dejaremos
        # que el frontend decida qué es nuevo comparando IDs, o todo de golpe.
        messages_qs = ChatMessage.objects.filter(
            models.Q(sender=request.user, receiver=target_user) |
            models.Q(sender=target_user, receiver=request.user)
        ).order_by('timestamp')[:100] # Limitar a 100 por ahora

        data = []
        for msg in messages_qs:
            data.append({
                'id': msg.id,
                'sender': msg.sender.username,
                'content': msg.content,
                'timestamp': msg.timestamp.isoformat(),
                'is_read': msg.is_read
            })

        # Marcar los mensajes entrantes como leídos
        ChatMessage.objects.filter(
            sender=target_user, 
            receiver=request.user, 
            is_read=False
        ).update(is_read=True)

        return JsonResponse({'success': True, 'messages': data})


class SendMessageAPIView(View):
    """API para enviar un mensaje a otro usuario."""
    @method_decorator(login_required(login_url='login:login'))
    def post(self, request, username, *args, **kwargs):
        try:
            target_user = get_object_or_404(User, username=username)
            try:
                my_profile = request.user.profile
            except User.profile.RelatedObjectDoesNotExist:
                my_profile = UserProfile.objects.create(user=request.user)
                
            try:
                target_profile = target_user.profile
            except User.profile.RelatedObjectDoesNotExist:
                target_profile = UserProfile.objects.create(user=target_user)

            if not my_profile.friends.filter(id=target_profile.id).exists():
                return JsonResponse({'success': False, 'error': 'No puedes enviar mensajes a alguien que no es tu amigo.'})

            data = json.loads(request.body)
            content = data.get('content', '').strip()

            if not content:
                return JsonResponse({'success': False, 'error': 'El mensaje no puede estar vacío.'})

            msg = ChatMessage.objects.create(
                sender=request.user,
                receiver=target_user,
                content=content
            )

            return JsonResponse({
                'success': True, 
                'message': {
                    'id': msg.id,
                    'sender': msg.sender.username,
                    'content': msg.content,
                    'timestamp': msg.timestamp.isoformat()
                }
            })
        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)})
