"""
URLs para la aplicaciÃ³n login.
"""
from django.urls import path
from . import views, api

app_name = 'login'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('perfil/', views.ProfileView.as_view(), name='profile'),
    path('perfil/editar/', views.ProfileUpdateView.as_view(), name='profile_edit'),
    path('api/check_availability/', api.CheckUserAPIView.as_view(), name='check_availability'),
    path('api/validate_password/', api.ValidatePasswordAPIView.as_view(), name='validate_password'),
    # Password Management (Overrides allauth)
    path('password/change/', views.CustomPasswordChangeView.as_view(), name='account_change_password'),
    path('password/set/', views.CustomPasswordSetView.as_view(), name='account_set_password'),
    path('api/auto_messages/', api.AutoMessagesAPIView.as_view(), name='auto_messages_api'),
    path('api/notifications/', api.NotificationsAPIView.as_view(), name='notifications_api'),
    path('api/notifications/read/', api.MarkNotificationReadAPIView.as_view(), name='mark_notification_read'),
    
    # Friend System & Player Search
    path('jugadores/buscar/', views.SearchPlayersView.as_view(), name='search_players'),
    path('jugador/<str:username>/', views.PlayerProfileView.as_view(), name='player_profile'),
    path('amigos/solicitar/', api.SendFriendRequestAPIView.as_view(), name='send_friend_request'),
    path('amigos/aceptar/', api.AcceptFriendRequestAPIView.as_view(), name='accept_friend_request'),
    path('amigos/rechazar/', api.RejectFriendRequestAPIView.as_view(), name='reject_friend_request'),
    path('amigos/eliminar/', api.RemoveFriendAPIView.as_view(), name='remove_friend'),
]
