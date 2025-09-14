from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend.apps.api'
    label = 'api'  # ← Label para referencias de modelo
    verbose_name = 'API Endpoints'
