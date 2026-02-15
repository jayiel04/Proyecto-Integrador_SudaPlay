"""
URLs para la aplicación web.
"""
from django.urls import path
from . import views

app_name = 'web'

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
]
