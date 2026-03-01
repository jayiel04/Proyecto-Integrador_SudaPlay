"""
URLs para la aplicaciÃ³n login.
"""
from django.urls import path
from . import views

app_name = 'login'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('perfil/', views.ProfileView.as_view(), name='profile'),
    path('perfil/editar/', views.ProfileUpdateView.as_view(), name='profile_edit'),
    path('api/check_availability/', views.CheckUserAPIView.as_view(), name='check_availability'),
    path('api/validate_password/', views.ValidatePasswordAPIView.as_view(), name='validate_password'),
    path('api/auto_messages/', views.AutoMessagesAPIView.as_view(), name='auto_messages_api'),
    
    # Friend System & Player Search
    path('jugadores/buscar/', views.SearchPlayersView.as_view(), name='search_players'),
    path('jugador/<str:username>/', views.PlayerProfileView.as_view(), name='player_profile'),
    path('amigos/solicitar/', views.SendFriendRequestAPIView.as_view(), name='send_friend_request'),
    path('amigos/aceptar/', views.AcceptFriendRequestAPIView.as_view(), name='accept_friend_request'),
    path('amigos/rechazar/', views.RejectFriendRequestAPIView.as_view(), name='reject_friend_request'),
    path('amigos/eliminar/', views.RemoveFriendAPIView.as_view(), name='remove_friend'),
]
