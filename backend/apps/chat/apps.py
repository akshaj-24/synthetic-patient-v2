from django.apps import AppConfig

class LangfuseInit(AppConfig):
    name = 'chat'
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        from langfuse import Langfuse
        Langfuse()
