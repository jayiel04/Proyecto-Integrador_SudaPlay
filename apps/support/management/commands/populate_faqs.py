from django.core.management.base import BaseCommand
from apps.support.models import FAQ

class Command(BaseCommand):
    help = 'Popula la base de datos con las preguntas frecuentes iniciales'

    def handle(self, *args, **kwargs):
        faqs = [
            {
                'question': '¿Cómo puedo subir un juego?',
                'answer': 'Para subir un juego, haz clic en el botón "Subir juego" en la barra de navegación superior (debes haber iniciado sesión). Luego, completa el formulario con el título, descripción, y sube los archivos de tu juego (HTML o ZIP dependiendo del tipo).',
                'order': 1
            },
            {
                'question': '¿Cómo puedo reportar infracciones por derecho de autor?',
                'answer': 'Si crees que un juego infringe tus derechos de autor, por favor envíanos un correo a copyright@sudaplay.com con la URL del juego y una prueba de autoría y propiedad del material. Revisaremos tu caso lo antes posible.',
                'order': 2
            },
            {
                'question': 'Mi juego fue retirado por derechos de autor, ¿qué hago?',
                'answer': 'Los juegos pueden ser retirados si recibimos un reclamo de DMCA válido. Si crees que esto fue un error o tienes los derechos para publicar el juego, puedes presentar una contranotificación respondiendo al correo electrónico que te enviamos notificando el retiro.',
                'order': 3
            }
        ]

        for faq_data in faqs:
            FAQ.objects.get_or_create(question=faq_data['question'], defaults=faq_data)
        
        self.stdout.write(self.style.SUCCESS(f'Exitosamente se añadieron {len(faqs)} preguntas frecuentes.'))
