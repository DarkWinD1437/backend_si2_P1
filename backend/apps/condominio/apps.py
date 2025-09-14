from django.apps import AppConfig


class CondominioConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend.apps.condominio'
    label = 'condominio'  # ← Label para referencias de modelo
    verbose_name = 'Smart Condominium'
