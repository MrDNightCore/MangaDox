from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = 'users'
    def ready(self):
        # Import signal handlers to ensure they're registered
        try:
            import users.signals  # noqa: F401
        except Exception:
            pass
