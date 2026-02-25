"""
Security utilities for authentication and protection against common attacks.
"""
import hashlib
import time
from functools import wraps
from django.core.cache import cache
from django.http import HttpResponseForbidden
from django.contrib import messages
from decouple import config
import re
import logging

logger = logging.getLogger('django.security')

# ============================================================================
# RATE LIMITING
# ============================================================================

class RateLimiter:
    """Rate limiting to prevent brute force attacks."""
    
    @staticmethod
    def is_limited(identifier, action, limit=5, window=300):
        """
        Check if an action is rate limited.
        
        Args:
            identifier: IP address or user identifier
            action: Type of action (login, register, forgot_password)
            limit: Number of attempts allowed
            window: Time window in seconds
            
        Returns:
            True if rate limited, False otherwise
        """
        cache_key = f'rate_limit:{action}:{identifier}'
        attempts = cache.get(cache_key, 0)
        
        if attempts >= limit:
            logger.warning(f'Rate limit exceeded: {action} from {identifier}')
            return True
        
        cache.set(cache_key, attempts + 1, window)
        return False
    
    @staticmethod
    def get_client_ip(request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


def rate_limit(action, limit=5, window=300):
    """
    Decorator to rate limit view functions.
    
    Usage:
        @rate_limit('login', limit=5, window=300)
        def login_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            client_ip = RateLimiter.get_client_ip(request)
            
            if RateLimiter.is_limited(client_ip, action, limit, window):
                messages.error(request, f'Too many {action} attempts. Please try again later.')
                logger.warning(f'Rate limit triggered for {action} from {client_ip}')
                return HttpResponseForbidden('Too many requests. Please try again later.')
            
            return view_func(request, *args, **kwargs)
        return wrapped_view
    return decorator


# ============================================================================
# INPUT VALIDATION & SANITIZATION
# ============================================================================

class InputValidator:
    """Validate and sanitize user input."""
    
    # Username pattern: alphanumeric, underscore, dash (3-30 chars)
    USERNAME_PATTERN = re.compile(r'^[a-zA-Z0-9_-]{3,30}$')
    
    # Email pattern validation
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')
    
    @staticmethod
    def validate_username(username):
        """
        Validate username.
        
        Returns:
            (is_valid: bool, error_message: str or None)
        """
        if not username or len(username) == 0:
            return False, "Username is required."
        
        if len(username) < 3:
            return False, "Username must be at least 3 characters long."
        
        if len(username) > 30:
            return False, "Username must not exceed 30 characters."
        
        if not InputValidator.USERNAME_PATTERN.match(username):
            return False, "Username can only contain letters, numbers, underscores, and dashes."
        
        return True, None
    
    @staticmethod
    def validate_email(email):
        """
        Validate email address.
        
        Returns:
            (is_valid: bool, error_message: str or None)
        """
        if not email or len(email) == 0:
            return False, "Email is required."
        
        if len(email) > 254:
            return False, "Email address is too long."
        
        if not InputValidator.EMAIL_PATTERN.match(email):
            return False, "Please enter a valid email address."
        
        return True, None
    
    @staticmethod
    def validate_password(password, username=None, email=None):
        """
        Validate password strength.
        
        Requirements:
        - Minimum 12 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character
        - Not similar to username or email
        
        Returns:
            (is_valid: bool, error_message: str or None)
        """
        if not password or len(password) == 0:
            return False, "Password is required."
        
        if len(password) < 12:
            return False, "Password must be at least 12 characters long."
        
        if len(password) > 128:
            return False, "Password must not exceed 128 characters."
        
        if not re.search(r'[A-Z]', password):
            return False, "Password must contain at least one uppercase letter."
        
        if not re.search(r'[a-z]', password):
            return False, "Password must contain at least one lowercase letter."
        
        if not re.search(r'\d', password):
            return False, "Password must contain at least one digit."
        
        if not re.search(r'[!@#$%^&*()_+=\-\[\]{};:\'",.<>?/\\|`~]', password):
            return False, "Password must contain at least one special character (!@#$%^&*...)."
        
        # Check similarity to username
        if username and username.lower() in password.lower():
            return False, "Password is too similar to your username."
        
        # Check similarity to email
        if email:
            email_local = email.split('@')[0].lower()
            if email_local in password.lower():
                return False, "Password is too similar to your email address."
        
        return True, None
    
    @staticmethod
    def sanitize_input(user_input):
        """
        Simple sanitization of user input to prevent XSS.
        
        This is a basic sanitizer. For production, use django-bleach or similar.
        """
        if not isinstance(user_input, str):
            return user_input
        
        # Remove potentially dangerous HTML/JS
        dangerous_chars = {
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#39;',
        }
        
        for char, replacement in dangerous_chars.items():
            user_input = user_input.replace(char, replacement)
        
        return user_input


# ============================================================================
# SECURITY LOGGING
# ============================================================================

def log_security_event(event_type, user_id=None, ip_address=None, details=None):
    """
    Log security events for monitoring and auditing.
    
    Args:
        event_type: Type of event (login_attempt, registration, failed_login, etc.)
        user_id: User ID if applicable
        ip_address: Client IP address
        details: Additional details dictionary
    """
    log_message = f'[{event_type}] User ID: {user_id}, IP: {ip_address}'
    if details:
        log_message += f', Details: {details}'
    
    if event_type.startswith('failed_') or event_type == 'suspicious_activity':
        logger.warning(log_message)
    else:
        logger.info(log_message)


# ============================================================================
# SESSION SECURITY
# ============================================================================

def is_session_valid(request):
    """Check if user session is still valid."""
    if 'user_id' not in request.session:
        return False
    
    # Additional security checks can be added here
    return True
