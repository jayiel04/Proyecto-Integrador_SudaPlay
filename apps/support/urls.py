from django.urls import path
from . import views

app_name = 'support'

urlpatterns = [
    path('faq/', views.FAQListView.as_view(), name='faq'),
    path('terminos/', views.TermsView.as_view(), name='terms'),
]
