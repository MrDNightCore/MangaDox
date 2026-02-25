from django.db import models
from django.contrib.auth.hashers import make_password, check_password
import logging

logger = logging.getLogger('django.security')

# Create your models here.
class UserProfile(models.Model):
    """
    Custom user model with security features.
    
    Security features:
    - Password hashing
    - Account lock on multiple failed attempts
    - Last login tracking
    - Account status (active/inactive)
    """
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    last_login = models.DateTimeField(null=True, blank=True)
    failed_login_attempts = models.IntegerField(default=0)
    is_active = models.BooleanField(default=True)
    is_locked = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    locked_until = models.DateTimeField(null=True, blank=True)

    def set_password(self, raw_password):
        """Hash and set password"""
        self.password = make_password(raw_password)

    def check_password(self, raw_password):
        """Verify password"""
        return check_password(raw_password, self.password)
    
    def record_failed_login(self):
        """Record failed login attempt and lock account if necessary."""
        self.failed_login_attempts += 1
        
        # Lock account after 5 failed attempts
        if self.failed_login_attempts >= 5:
            from django.utils import timezone
            from datetime import timedelta
            self.is_locked = True
            self.locked_until = timezone.now() + timedelta(minutes=15)
            logger.warning(f'Account locked: {self.username} (failed attempts: {self.failed_login_attempts})')
        
        self.save()
    
    def reset_failed_login_attempts(self):
        """Reset failed login attempts after successful login."""
        self.failed_login_attempts = 0
        self.is_locked = False
        self.locked_until = None
        
        from django.utils import timezone
        self.last_login = timezone.now()
        self.save()
    
    def is_account_locked(self):
        """Check if account is currently locked."""
        if not self.is_locked:
            return False
        
        from django.utils import timezone
        if self.locked_until and timezone.now() > self.locked_until:
            # Unlock account
            self.is_locked = False
            self.locked_until = None
            self.save()
            return False
        
        return self.is_locked

    def __str__(self):
        return self.username

    class Meta:
        db_table = 'users_userprofile'
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'
        ordering = ['-created_at']
