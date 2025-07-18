from django.apps import AppConfig

class DeploymentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'deployment'
    
    def ready(self):
        # Import signals here to ensure they're registered
        import deployment.signals

class DeploymentConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'deployment'
