"""
URLs para la aplicación login.
"""
from django.urls import path
from . import views

app_name = 'login'

urlpatterns = [
    path('login/', views.LoginView.as_view(), name='login'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('api/check_availability/', views.CheckUserAPIView.as_view(), name='check_availability'),
]
