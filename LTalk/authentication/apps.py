from django.apps import AppConfig


from django.apps import AppConfig

class AuthenticationConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'authentication'
    
    def ready(self):
        # Import signals to register them when the app is ready
        import authentication.signals
