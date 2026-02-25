from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.utils import timezone

from .models import UserProfile


@receiver(user_logged_in)
def sync_userprofile_on_login(sender, user, request, **kwargs):
    """
    When a Django `auth.User` logs in, ensure there's a corresponding
    `UserProfile` and set `request.session['user_id']` so legacy session-based
    admin checks work.

    Behavior:
    - Find existing `UserProfile` by email or username.
    - If missing, create one.
    - Copy the password hash from `auth.User` into `UserProfile.password` so
      site login (which checks the stored hash) accepts the same password.
    - Mark `is_admin=True` for `user.is_superuser`.
    - Update `last_login` and set session keys `user_id` and `username`.
    """
    try:
        profile = None
        if getattr(user, 'email', None):
            profile = UserProfile.objects.filter(email=user.email).first()
        if not profile:
            profile = UserProfile.objects.filter(username=user.username).first()

        if not profile:
            profile = UserProfile(username=user.username, email=(user.email or ''))

        # Copy Django's hashed password so UserProfile.check_password() works
        try:
            if getattr(user, 'password', None):
                profile.password = user.password
        except Exception:
            pass

        # Mark admin status for superusers
        if getattr(user, 'is_superuser', False):
            profile.is_admin = True

        profile.is_active = True
        profile.last_login = timezone.now()
        profile.save()

        # Populate legacy session keys used across the site
        try:
            request.session['user_id'] = profile.id
            request.session['username'] = profile.username
        except Exception:
            # Request/session may not be available in some contexts
            pass
    except Exception:
        # Never raise from a signal handler — log silently if needed
        return
