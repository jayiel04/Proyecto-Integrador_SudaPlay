from django.contrib import admin

from .models import Game, GameRating


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "genre",
        "rating",
        "rating_votes",
        "uploaded_by",
        "is_web_playable",
        "is_approved",
        "is_featured",
        "created_at",
    )
    list_filter = ("genre", "is_web_playable", "is_approved", "is_featured", "created_at")
    search_fields = ("title", "short_description", "uploaded_by__username")
    readonly_fields = ("downloads", "views", "rating_votes", "created_at", "updated_at", "web_build_path", "processing_error")
    list_editable = ("is_approved", "is_featured")


@admin.register(GameRating)
class GameRatingAdmin(admin.ModelAdmin):
    list_display = ("game", "user", "value", "created_at")
    list_filter = ("value", "created_at")
    search_fields = ("game__title", "user__username")
