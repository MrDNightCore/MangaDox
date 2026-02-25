"""
Management command to seed admin and test accounts.

This is safe to run multiple times – it skips accounts that already exist.
"""
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from users.models import UserProfile

User = get_user_model()


# ── Django auth superusers (for /admin access) ──────────────────────────
AUTH_USERS = [
    {
        "username": "doxjr",
        "email": "doxlebumfacil09@gmail.com",
        "password": "pbkdf2_sha256$1200000$BXTi0LImXlpQQyH58zTaoP$FR+RdXmXCyBP9+EyjfxBWjmJTQoDsrlgTMeeu6YFS7w=",
        "first_name": "Dox",
        "last_name": "Lebumfacil",
        "is_superuser": True,
        "is_staff": True,
    },
    {
        "username": "MrDTheGreat",
        "email": "doxlebumfacil09@gmail.com",
        "password": "pbkdf2_sha256$1200000$GP6ybEgJwRWYTAh71DcNIU$GdEVRraVXpoc/OwiiyQXGcczbsAF3IpTEnVDlfYzaP4=",
        "first_name": "",
        "last_name": "",
        "is_superuser": True,
        "is_staff": True,
    },
    {
        "username": "admin_local",
        "email": "admin_local@example.com",
        "password": "pbkdf2_sha256$1200000$jIsMsR4HToDW87IVq7wHZi$JR1fMw1+NFvR7XKffwMya1rAL/CZu0SMpXnqOqZ7Ux8=",
        "first_name": "",
        "last_name": "",
        "is_superuser": True,
        "is_staff": True,
    },
]

# ── Site UserProfile accounts ───────────────────────────────────────────
PROFILE_USERS = [
    {
        "username": "MrDTheGreat",
        "email": "doxlebumfacil09@gmail.com",
        "password": "pbkdf2_sha256$1200000$g9oP3JPTzIJpaDPycrhGCp$u1VUynZqayROwNi/BYGnabxsfPFvOC7b1bZ8u7a9yko=",
        "is_admin": True,
    },
    {
        "username": "admin",
        "email": "admin@mangadox.com",
        "password": "pbkdf2_sha256$1200000$PJEMiEGXkRwvSywLzeaAIr$RAgYNcBCNaMMbFF9DeTT7KOkBpD6H0QSfuufe/9loF8=",
        "is_admin": True,
    },
    {
        "username": "admin_local",
        "email": "admin_local@example.com",
        "password": "pbkdf2_sha256$1200000$jIsMsR4HToDW87IVq7wHZi$JR1fMw1+NFvR7XKffwMya1rAL/CZu0SMpXnqOqZ7Ux8=",
        "is_admin": True,
    },
]

# ── Test user ───────────────────────────────────────────────────────────
TEST_USER = {
    "username": "testuser",
    "email": "testuser@mangadox.com",
    "raw_password": "TestUser@12345",
    "is_admin": False,
}


class Command(BaseCommand):
    help = "Seed admin accounts and a test user into the database (idempotent)."

    def handle(self, *args, **options):
        self._seed_auth_users()
        self._seed_profile_users()
        self._seed_test_user()

    # ── helpers ──────────────────────────────────────────────────────────

    def _seed_auth_users(self):
        """Create Django auth superusers (for /admin panel)."""
        for data in AUTH_USERS:
            username = data["username"]
            if User.objects.filter(username=username).exists():
                self.stdout.write(f"  auth_user '{username}' already exists – skipped")
                continue

            user = User(
                username=username,
                email=data["email"],
                password=data["password"],  # already hashed
                first_name=data["first_name"],
                last_name=data["last_name"],
                is_superuser=data["is_superuser"],
                is_staff=data["is_staff"],
                is_active=True,
            )
            user.save()
            self.stdout.write(self.style.SUCCESS(f"  auth_user '{username}' created"))

    def _seed_profile_users(self):
        """Create site UserProfile admin accounts."""
        for data in PROFILE_USERS:
            username = data["username"]
            if UserProfile.objects.filter(username=username).exists():
                self.stdout.write(f"  UserProfile '{username}' already exists – skipped")
                continue

            profile = UserProfile(
                username=username,
                email=data["email"],
                password=data["password"],  # already hashed
                is_admin=data["is_admin"],
                is_active=True,
            )
            profile.save()
            self.stdout.write(self.style.SUCCESS(f"  UserProfile '{username}' created"))

    def _seed_test_user(self):
        """Create a test user for site login."""
        username = TEST_USER["username"]
        if UserProfile.objects.filter(username=username).exists():
            self.stdout.write(f"  UserProfile '{username}' already exists – skipped")
            return

        profile = UserProfile(
            username=username,
            email=TEST_USER["email"],
            is_admin=TEST_USER["is_admin"],
            is_active=True,
        )
        profile.set_password(TEST_USER["raw_password"])
        profile.save()
        self.stdout.write(self.style.SUCCESS(
            f"  UserProfile '{username}' created (password: {TEST_USER['raw_password']})"
        ))
