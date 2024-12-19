from django.apps import AppConfig

class KilometersappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'KilometersApp'

    def ready(self):
        import KilometersApp.signals
