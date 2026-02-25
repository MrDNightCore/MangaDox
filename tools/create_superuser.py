import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MangaDox.settings')
import django
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

USERNAME = 'admin'
EMAIL = 'admin@example.com'
PASSWORD = 'adminpass'

if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser(username=USERNAME, email=EMAIL, password=PASSWORD)
    print(f'SUPERUSER_CREATED: username={USERNAME} password={PASSWORD}')
else:
    print('SUPERUSER_EXISTS')
