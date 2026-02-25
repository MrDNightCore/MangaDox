# MangaDox Security Implementation Guide

## Overview

This document outlines all security measures implemented in the MangaDox Django application to protect against common web attacks and vulnerabilities.

---

## Security Issues Identified & Fixed

### 🚨 CRITICAL Issues (Fixed)

#### 1. **Hardcoded Secret Key**

- **Issue**: SECRET_KEY was exposed in settings.py
- **Fix**:
  - Moved to `.env` file using `python-decouple`
  - Use environment variables in production

#### 2. **DEBUG Mode Enabled**

- **Issue**: DEBUG=True exposes sensitive information in error pages
- **Fix**:
  - Set DEBUG=False in production
  - Configure via environment variable

#### 3. **Empty ALLOWED_HOSTS**

- **Issue**: Allows any host to access the application (Host Header Injection)
- **Fix**:
  - Configure specific allowed hosts in `.env`
  - Example: `ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com`

#### 4. **No HTTPS Enforcement**

- **Issue**: Data transmitted in plain text over HTTP
- **Fix**:
  - Enable `SECURE_SSL_REDIRECT=True` in production
  - Set `SESSION_COOKIE_SECURE=True`
  - Set `CSRF_COOKIE_SECURE=True`

#### 5. **Weak Session Security**

- **Issue**: Sessions vulnerable to hijacking and fixation attacks
- **Fix**:
  - `SESSION_COOKIE_HTTPONLY=True` - prevents JavaScript access
  - `SESSION_COOKIE_SAMESITE='Strict'` - prevents CSRF via cookies
  - `CSRF_COOKIE_HTTPONLY=True` - protects CSRF token
  - Session expiry set to 3600 seconds (1 hour)

---

### 🔴 HIGH Priority Issues (Fixed)

#### 6. **No Rate Limiting**

- **Issue**: Brute force attacks on login and registration
- **Fix**:
  - Implemented custom rate limiter in `users/security.py`
  - Login: 5 attempts per 5 minutes per IP
  - Registration: 3 attempts per 5 minutes per IP
  - Account lockout: 15 minutes after 5 failed login attempts

#### 7. **Weak Input Validation**

- **Issue**: SQL Injection, XSS, and data validation vulnerabilities
- **Fix**:
  - Created `InputValidator` class with comprehensive validation
  - Username validation: alphanumeric, 3-30 characters
  - Email validation: RFC-compliant pattern
  - Password strength requirements:
    - Minimum 12 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    - Cannot contain username or email

#### 8. **Information Disclosure (User Enumeration)**

- **Issue**: Login errors reveal whether user exists
- **Fix**:
  - Generic error message: "Invalid username or password"
  - Doesn't reveal user existence
  - Logs suspicious activity for monitoring

#### 9. **Account Enumeration on Registration**

- **Issue**: Users list exposed on registration page
- **Fix**:
  - Removed `users = UserProfile.objects.all()` from context
  - No more user list in templates

#### 10. **Missing Security Headers**

- **Issue**: Vulnerable to Clickjacking, XSS, MIME type sniffing
- **Fix**:
  - `X-Frame-Options=DENY` - prevent iframe embedding
  - `SECURE_CONTENT_TYPE_NOSNIFF=True` - prevent MIME type sniffing
  - `SECURE_BROWSER_XSS_FILTER=True` - enable browser XSS protection
  - Content Security Policy (CSP) configured

#### 11. **Weak CSRF Protection**

- **Issue**: Logout could be triggered via GET request (CSRF)
- **Fix**:
  - Changed logout to POST-only method
  - Updated templates to use form-based logout button
  - CSRF token validation on all forms

---

### 🟡 MEDIUM Priority Issues (Fixed)

#### 12. **No HSTS (HTTP Strict Transport Security)**

- **Issue**: Browser can be downgraded to HTTP
- **Fix**:
  - `SECURE_HSTS_SECONDS=31536000` (1 year)
  - `SECURE_HSTS_INCLUDE_SUBDOMAINS=True`
  - `SECURE_HSTS_PRELOAD=True`

#### 13. **No Security Logging**

- **Issue**: Cannot detect or audit security events
- **Fix**:
  - Implemented `log_security_event()` function
  - Logs login attempts, failed logins, registration, etc.
  - Security logs separate in `logs/security.log`

#### 14. **Insufficient Password Policy**

- **Issue**: Default Django validators too weak
- **Fix**:
  - Increased minimum length from 8 to 12 characters
  - Added comprehensive strength requirements

#### 15. **Account Already Active After Registration**

- **Issue**: No email verification needed
- **Fix**:
  - Users are active immediately (for now)
  - TODO: Implement email verification in future

---

## Security Configuration Files

### 1. **.env Configuration** (`.env.example`)

```
# Production Security Settings
DEBUG=False
ALLOWED_HOSTS=localhost,127.0.0.1,yourdomain.com
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SESSION_COOKIE_AGE=3600
```

### 2. **Settings.py** (`MangaDox/settings.py`)

- All critical security settings configured
- Environment-based configuration
- Logging for security events
- Password validation
- CSRF and cookie protection

### 3. **Security Module** (`users/security.py`)

- Rate limiting decorator and class
- Input validation with comprehensive rules
- Security event logging
- Session validation utilities

---

## Implementation Details

### Rate Limiting

```python
# Automatic rate limiting with Django cache
# Uses IP address to track attempts
# Configurable per action type

@rate_limit('login', limit=5, window=300)
def login_view(request):
    ...
```

### Password Validation

```python
# Strong password requirements enforced
# Minimum 12 characters
# Must include uppercase, lowercase, digit, special char
# Cannot contain username or email

is_valid, error_msg = InputValidator.validate_password(
    password,
    username=username,
    email=email
)
```

### Security Logging

```python
# All security events logged
# Login attempts, failures, registrations, etc.
log_security_event(
    'login_successful',
    user_id=user.id,
    ip_address=client_ip
)
```

---

## Deployment Checklist

Before deploying to production, ensure:

- [ ] Create `.env` file with production values
- [ ] Set `DEBUG=False`
- [ ] Set `SECRET_KEY` to a strong random value
- [ ] Configure `ALLOWED_HOSTS` with your domain
- [ ] Enable `SECURE_SSL_REDIRECT=True`
- [ ] Enable `SESSION_COOKIE_SECURE=True`
- [ ] Enable `CSRF_COOKIE_SECURE=True`
- [ ] Install SSL certificate (HTTPS)
- [ ] Configure database for production (PostgreSQL recommended)
- [ ] Set up email backend for password reset
- [ ] Enable logging and monitoring
- [ ] Run security checks: `python manage.py check --deploy`
- [ ] Update Django to latest security patch
- [ ] Configure firewall rules
- [ ] Set up WAF (Web Application Firewall) if possible

---

## Running Security Tests

```bash
# Run Django's built-in security checks
python manage.py check --deploy

# Run rate limiting tests
pytest tests/test_rate_limiting.py

# Run authentication tests
pytest tests/test_authentication.py
```

---

## Future Security Improvements

1. **Email Verification**
   - Send verification link on registration
   - Activate account only after email confirmation

2. **Two-Factor Authentication (2FA)**
   - TOTP (Time-based One-Time Password)
   - SMS-based 2FA option

3. **Password Reset**
   - Secure token-based reset links
   - Email verification

4. **API Rate Limiting**
   - Per-user API rate limits
   - DDoS protection

5. **Enhanced Monitoring**
   - Brute force detection
   - Suspicious activity alerts
   - Automated response to attacks

6. **Database Encryption**
   - Encrypt sensitive data at rest
   - Field-level encryption for PII

7. **Audit Trail**
   - Track all user actions
   - Compliance with regulations (GDPR, etc.)

8. **Security Headers**
   - Upgrade to CSP Level 3
   - Add Permissions-Policy header
   - Add X-Permitted-Cross-Domain-Policies

---

## Security Best Practices

### For Developers

1. Always validate input on the server side
2. Use Django ORM to prevent SQL injection
3. Keep dependencies updated
4. Never hardcode secrets
5. Use CSRF tokens on all forms
6. Sanitize error messages to prevent info disclosure

### For Administrators

1. Monitor logs regularly for suspicious activity
2. Back up database regularly
3. Keep Django and dependencies updated
4. Use strong database credentials
5. Restrict admin panel access
6. Enable 2FA for admin accounts
7. Monitor server resources and performance

### For Users

1. Use strong, unique passwords
2. Never share your password
3. Log out when finished
4. Don't use public WiFi for sensitive actions
5. Enable 2FA if available
6. Report suspicious activity

---

## Security Contacts

- **Security Issues**: security@mangadox.com
- **Report Vulnerabilities**: [Create GitHub Issue](https://github.com/your-repo/issues)
- **Django Security**: https://www.django-rest-framework.org/topics/security/

---

## References

1. [Django Security Documentation](https://docs.djangoproject.com/en/6.0/topics/security/)
2. [OWASP Top 10](https://owasp.org/Top10/)
3. [CWE/SANS Top 25](https://cwe.mitre.org/top25/)
4. [Django Deployment Checklist](https://docs.djangoproject.com/en/6.0/howto/deployment/checklist/)

---

## Last Updated

February 18, 2026

**Implemented By**: Security Audit
**Status**: ✅ Active
