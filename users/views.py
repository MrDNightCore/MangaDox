# views.py
"""
Secure authentication views with rate limiting, input validation, and protection against common attacks.
"""
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.messages import get_messages
from django.contrib.auth import authenticate, login as auth_login
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_protect
from django.http import HttpResponseForbidden
from .models import UserProfile
from .security import (
    RateLimiter, 
    rate_limit, 
    InputValidator, 
    log_security_event,
    is_session_valid
)


@csrf_protect
@require_http_methods(["GET", "POST"])
def login_page(request):
    """
    Secure login page with rate limiting and input validation.
    
    Security features:
    - Rate limiting: 5 attempts per 5 minutes
    - Input validation
    - Safe error messages (doesn't reveal user existence)
    - CSRF protection
    - Session security
    """
    client_ip = RateLimiter.get_client_ip(request)
    if request.method == "POST":
        # Check rate limiting only on form submission to avoid counting simple page views
        if RateLimiter.is_limited(client_ip, 'login', limit=5, window=300):
            messages.error(request, 'Too many login attempts. Please try again later.')
            log_security_event('rate_limit_exceeded', ip_address=client_ip)
            return render(request, "login.html")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        
        # Input validation
        if not username or not password:
            messages.error(request, "Username and password are required.")
            log_security_event('login_attempt_missing_fields', ip_address=client_ip)
            return render(request, "login.html")
        
        # Validate username format for safety
        if not InputValidator.validate_username(username)[0]:
            messages.error(request, "Invalid username format.")
            log_security_event('login_attempt_invalid_format', ip_address=client_ip)
            return render(request, "login.html")

        # First try Django's authentication backend (so admin/superusers authenticate)
        try:
            auth_user = authenticate(request, username=username, password=password)
            if auth_user is not None:
                # Successful Django auth: log them in and rely on the user_logged_in signal
                # (we register a signal to create/sync a UserProfile and set session keys)
                try:
                    request.session.flush()
                except Exception:
                    pass
                auth_login(request, auth_user)
                messages.success(request, f"Welcome back, {username}!")
                log_security_event('login_successful_django', user_id=getattr(auth_user, 'id', None), ip_address=client_ip)
                return redirect("home")
        except Exception:
            # If Django auth errors, continue to site-specific UserProfile flow
            pass
        
        # Check if user exists
        try:
            user = UserProfile.objects.get(username=username)
            
            # Check if account is locked
            if user.is_account_locked():
                messages.error(request, "Account is temporarily locked due to multiple failed login attempts. Please try again later.")
                log_security_event('login_attempt_locked_account', ip_address=client_ip,
                                 details=f'Username: {username}')
                return render(request, "login.html")
            
            # Check if password is correct
            if user.check_password(password):
                # Reset failed attempts on successful login
                user.reset_failed_login_attempts()
                
                # Successful login
                # Prevent session fixation: clear existing session and start fresh
                request.session.flush()
                request.session['user_id'] = user.id
                request.session['username'] = user.username
                
                messages.success(request, f"Welcome back, {username}!")
                log_security_event('login_successful', user_id=user.id, ip_address=client_ip)
                return redirect("home")
            else:
                # Invalid password - record failed attempt
                user.record_failed_login()
                if user.is_locked:
                    messages.error(request, "Account locked due to multiple failed login attempts. Please try again later.")
                else:
                    messages.error(request, "Invalid username or password.")
                
                log_security_event('login_failed_invalid_password', ip_address=client_ip, 
                                 details=f'Username: {username}')
                
        except UserProfile.DoesNotExist:
            # User doesn't exist - use generic error message (don't reveal)
            messages.error(request, "Invalid username or password.")
            log_security_event('login_failed_user_not_found', ip_address=client_ip,
                             details=f'Username: {username}')
    
    return render(request, "login.html")


@csrf_protect
@require_http_methods(["GET", "POST"])
def register_page(request):
    """
    Secure registration page with comprehensive input validation.
    
    Security features:
    - Rate limiting: 3 attempts per 5 minutes
    - Password strength requirements
    - Email validation
    - Username validation
    - Duplicate checking
    - CSRF protection
    """
    client_ip = RateLimiter.get_client_ip(request)
    if request.method == "POST":
        # Check rate limiting only on form submission to avoid counting page views
        if RateLimiter.is_limited(client_ip, 'register', limit=3, window=300):
            messages.error(request, 'Too many registration attempts. Please try again later.')
            log_security_event('rate_limit_exceeded', ip_address=client_ip, 
                             details='Registration')
            return render(request, "registers.html")

    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        email = request.POST.get("email", "").strip().lower()
        password = request.POST.get("password", "")
        confirm_password = request.POST.get("confirm_password", "")
        
        # Validate username
        username_valid, username_error = InputValidator.validate_username(username)
        if not username_valid:
            messages.error(request, username_error)
            log_security_event('registration_attempt_invalid_username', ip_address=client_ip)
            return render(request, "registers.html")
        
        # Validate email
        email_valid, email_error = InputValidator.validate_email(email)
        if not email_valid:
            messages.error(request, email_error)
            log_security_event('registration_attempt_invalid_email', ip_address=client_ip)
            return render(request, "registers.html")
        
        # Validate password
        password_valid, password_error = InputValidator.validate_password(password, username, email)
        if not password_valid:
            messages.error(request, password_error)
            log_security_event('registration_attempt_weak_password', ip_address=client_ip)
            return render(request, "registers.html")
        
        # Check password confirmation
        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            log_security_event('registration_attempt_password_mismatch', ip_address=client_ip)
            return render(request, "registers.html")
        
        # Check if username already exists
        if UserProfile.objects.filter(username=username).exists():
            messages.error(request, "Username already exists! Please choose another.")
            log_security_event('registration_attempt_duplicate_username', ip_address=client_ip,
                             details=f'Username: {username}')
            return render(request, "registers.html")
        
        # Check if email already exists
        if UserProfile.objects.filter(email=email).exists():
            messages.error(request, "Email already registered! Please use another or login.")
            log_security_event('registration_attempt_duplicate_email', ip_address=client_ip,
                             details=f'Email: {email}')
            return render(request, "registers.html")
        
        # Create user with hashed password
        try:
            user = UserProfile(username=username, email=email)
            user.set_password(password)
            user.save()
            
            messages.success(request, "Registration successful! Please login with your credentials.")
            log_security_event('registration_successful', user_id=user.id, ip_address=client_ip)
            return redirect("login_page")
            
        except Exception as e:
            messages.error(request, "An error occurred during registration. Please try again.")
            log_security_event('registration_error', ip_address=client_ip,
                             details=str(e))
    
    # Don't expose all users - just render the form
    return render(request, "registers.html")


@require_http_methods(["POST"])
def logout_page(request):
    """
    Secure logout page.
    
    Security features:
    - POST-only (prevents CSRF via GET)
    - Clears all session data
    - Clears messages
    """
    user_id = request.session.get('user_id')
    client_ip = RateLimiter.get_client_ip(request)
    
    # Clear session data
    if 'user_id' in request.session:
        del request.session['user_id']
    if 'username' in request.session:
        del request.session['username']
    
    # Clear all session data
    request.session.flush()
    
    # Consume/clear any existing messages
    list(get_messages(request))
    
    messages.success(request, "Logged out successfully!")
    log_security_event('logout_successful', user_id=user_id, ip_address=client_ip)
    
    return redirect("login_page")


def csrf_failure(request, reason=""):
    """
    Custom CSRF failure view.
    """
    messages.error(request, "Security check failed. Please try again.")
    log_security_event('csrf_failure', ip_address=RateLimiter.get_client_ip(request),
                     details=reason)
    return render(request, "login.html", status=403)


def require_login(view_func):
    """
    Decorator to require login for a view.
    """
    def wrapper(request, *args, **kwargs):
        if not is_session_valid(request):
            messages.warning(request, "Please login first.")
            return redirect("login_page")
        return view_func(request, *args, **kwargs)
    return wrapper
