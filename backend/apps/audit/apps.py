from django.apps import AppConfig


class AuditConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend.apps.audit'
    verbose_name = 'Auditoría y Bitácora'
    
    def ready(self):
        """Importar las señales cuando la app esté lista"""
        import backend.apps.audit.signals