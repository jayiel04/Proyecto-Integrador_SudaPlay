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
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from apps.login.views import CustomPasswordResetView

urlpatterns = [
    path('admin/', admin.site.urls),
    # App URLs
    path('', include('apps.web.urls')),
    path('auth/', include('apps.login.urls')),
    path('chat/', include('apps.chat.urls')),
    path('soporte/', include('apps.support.urls', namespace='support')),
    path('accounts/password/reset/', CustomPasswordResetView.as_view(), name='account_reset_password'),
    path('accounts/', include('allauth.urls')), # Esto crea las rutas de login/social
]

# Servir archivos estáticos en desarrollo
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += staticfiles_urlpatterns()
