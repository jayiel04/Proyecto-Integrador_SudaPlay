from django.urls import path
from . import views

app_name = 'chat'

urlpatterns = [
    # Nueva vista para el Inbox estilo WhatsApp
    path('', views.ChatInboxView.as_view(), name='inbox'),
    path('conversacion/<str:username>/', views.ChatInboxView.as_view(), name='chat'),
    
    # APIs
    path('api/messages/<str:username>/', views.GetMessagesAPIView.as_view(), name='api_get_messages'),
    path('api/send/<str:username>/', views.SendMessageAPIView.as_view(), name='api_send_message'),
]
