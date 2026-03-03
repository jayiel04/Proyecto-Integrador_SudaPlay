from django.views.generic import ListView
from .models import FAQ

class FAQListView(ListView):
    model = FAQ
    template_name = 'support/faq.html'
    context_object_name = 'faqs'
