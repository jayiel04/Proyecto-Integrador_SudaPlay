from django.contrib import admin
from .models import FAQ

@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('question', 'order', 'created_at')
    list_editable = ('order',)
    search_fields = ('question', 'answer')
