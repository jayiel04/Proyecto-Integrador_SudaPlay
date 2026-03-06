from django.apps import AppConfig


class LoginConfig(AppConfig):
    name = 'apps.login'

    def ready(self):
        from . import signals  # noqa: F401 to register handlers
