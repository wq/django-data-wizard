from django.apps import AppConfig


class CustomURLConfig(AppConfig):
    name = "tests.source_app"

    def ready(self):
        import tests.urls
