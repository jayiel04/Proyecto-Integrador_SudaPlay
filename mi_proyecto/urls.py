"""
URL configuration para mi_proyecto.

Estructura escalable:
- URLs principales en urls.py
- Cada app tiene su propio urls.py
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # App URLs
    path('', include('apps.web.urls')),
    path('auth/', include('apps.login.urls')),
    path('accounts/', include('allauth.urls')), # Esto crea las rutas de login/social
]

# Servir archivos estáticos en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
