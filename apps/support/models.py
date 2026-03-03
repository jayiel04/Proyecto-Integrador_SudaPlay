from django.db import models

class FAQ(models.Model):
    question = models.CharField(max_length=255, verbose_name="Pregunta")
    answer = models.TextField(verbose_name="Respuesta")
    order = models.IntegerField(default=0, verbose_name="Orden")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Pregunta Frecuente"
        verbose_name_plural = "Preguntas Frecuentes"
        ordering = ['order', '-created_at']

    def __str__(self):
        return self.question
