## Seed accounts check

I searched the repository for a `seed_accounts` management command and could not find any implementation (only `build.sh` calls `python manage.py seed_accounts`).

Recommendations:

- Implement a Django management command `seed_accounts` under `yourapp/management/commands/seed_accounts.py` that is idempotent (checks for existing users/accounts before creating).
- Example idempotent pattern:

  from django.core.management.base import BaseCommand
  from django.contrib.auth import get_user_model

  class Command(BaseCommand):
  help = 'Create initial admin user if not present'

      def handle(self, *args, **options):
          User = get_user_model()
          if not User.objects.filter(username='admin').exists():
              User.objects.create_superuser('admin', 'admin@example.com', 'changeme')
          else:
              self.stdout.write('Admin user already exists')

- Make sure `seed_accounts` never exposes secrets in logs and can safely run multiple times.
- Because `build.sh` runs `seed_accounts` during build, keep it idempotent or move seeding to a release hook.
