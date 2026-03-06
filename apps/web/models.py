from django.conf import settings
from django.core.validators import FileExtensionValidator
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from .storage_backends import GameCoversStorage, GameFilesStorage


class Game(models.Model):
    GENRE_CHOICES = [
        ("accion", "Acción"),
        ("aventura", "Aventura"),
        ("estrategia", "Estrategia"),
        ("rpg", "RPG"),
        ("deportes", "Deportes"),
        ("carreras", "Carreras"),
        ("puzzle", "Puzzle"),
        ("simulacion", "Simulación"),
        ("terror", "Terror"),
        ("multijugador", "Multijugador"),
        ("otro", "Otro"),
    ]

    title = models.CharField(max_length=200, verbose_name="Título")
    description = models.TextField(verbose_name="Descripción")
    short_description = models.CharField(
        max_length=300,
        verbose_name="Descripción corta",
        help_text="Breve resumen del juego",
    )
    cover_image = models.ImageField(
        storage=GameCoversStorage(),
        verbose_name="Imagen de portada"
    )
    genre = models.CharField(max_length=100, choices=GENRE_CHOICES, verbose_name="Género")
    game_file = models.FileField(
        storage=GameFilesStorage(),
        null=True,
        blank=True,
        verbose_name="Archivo del juego",
        validators=[FileExtensionValidator(allowed_extensions=["zip"])],
        help_text="Archivo ZIP web con index.html (max 500MB)",
    )
    external_url = models.URLField(
        blank=True,
        verbose_name="URL externa",
        help_text="Link para jugar online (opcional)",
    )
    downloads = models.IntegerField(default=0, verbose_name="Descargas")
    views = models.IntegerField(default=0, verbose_name="Vistas")
    rating = models.DecimalField(max_digits=2, decimal_places=1, default=0, verbose_name="Calificación")
    rating_votes = models.PositiveIntegerField(default=0, verbose_name="Total de votos")
    is_web_playable = models.BooleanField(default=False, verbose_name="Jugable en web")
    web_build_path = models.CharField(max_length=500, blank=True, default="", verbose_name="Ruta web del build")
    processing_error = models.CharField(
        max_length=255,
        blank=True,
        default="",
        verbose_name="Error de procesamiento",
    )

    is_approved = models.BooleanField(
        default=False,
        verbose_name="Aprobado",
        help_text="Solo juegos aprobados son visibles públicamente",
    )
    is_featured = models.BooleanField(default=False, verbose_name="Destacado")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de creación")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última actualización")
    uploaded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="games",
        verbose_name="Subido por",
    )

    class Meta:
        verbose_name = "Juego"
        verbose_name_plural = "Juegos"
        ordering = ["-created_at"]

    def __str__(self):
        return self.title


class GameRating(models.Model):
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="ratings", verbose_name="Juego")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="game_ratings", verbose_name="Usuario")
    value = models.PositiveSmallIntegerField(
        verbose_name="Calificación",
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Calificación de juego"
        verbose_name_plural = "Calificaciones de juegos"
        constraints = [
            models.UniqueConstraint(fields=["game", "user"], name="unique_game_user_rating"),
        ]

    def __str__(self):
        return f"{self.user_id}:{self.game_id}={self.value}"


# ---------------------------------------------------------------------------
# Signal: post_save en Game
# ---------------------------------------------------------------------------
@receiver(post_save, sender=Game)
def process_game_zip(sender, instance, created, **kwargs):
    """
    Se dispara después de guardar un Game.
    Si es nuevo y tiene game_file, actualiza is_web_playable y web_build_path.

    Para lógica avanzada de descompresión (extraer index.html del ZIP en
    Supabase y servir los archivos), agrega una tarea Celery aquí.
    """
    if created and instance.game_file:
        # Usamos update() para evitar recursión infinita con el signal
        Game.objects.filter(pk=instance.pk).update(
            is_web_playable=True,
            web_build_path=instance.game_file.url,
        )
