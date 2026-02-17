"""
URLs para la aplicación web.
"""
from django.urls import path
from . import views

app_name = 'web'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('juegos/subir/', views.GameCreateView.as_view(), name='game_create'),
    path('juegos/mis-juegos/', views.MyGamesView.as_view(), name='my_games'),
    path('juegos/<int:pk>/', views.GameDetailView.as_view(), name='game_detail'),
    path('juegos/<int:pk>/descargar/', views.GameDownloadView.as_view(), name='game_download'),
    path('juegos/<int:pk>/jugar/', views.GamePlayView.as_view(), name='game_play'),
]
