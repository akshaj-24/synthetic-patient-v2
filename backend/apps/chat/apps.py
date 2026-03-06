from django.apps import AppConfig
from dotenv import load_dotenv

class LangfuseInit(AppConfig):
    name = 'apps.chat'
    default_auto_field = 'django.db.models.BigAutoField'

    def ready(self):
        from langfuse import Langfuse
        load_dotenv()  # Load environment variables for Langfuse
        Langfuse()
