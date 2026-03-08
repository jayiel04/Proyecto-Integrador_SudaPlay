from django.views.generic import ListView, TemplateView
from .models import FAQ

class FAQListView(ListView):
    model = FAQ
    template_name = 'support/faq.html'
    context_object_name = 'faqs'


class TermsView(TemplateView):
    template_name = 'support/terms.html'
