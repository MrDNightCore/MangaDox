# Security Implementation Setup Guide

## Quick Start - Deploy Security Updates

### Step 1: Install Required Packages

```bash
# Activate your virtual environment first
cd c:\Users\DoxJr\OneDrive\Desktop\Manga\MangaDox

# Install dependencies with security packages
pip install -r requirements.txt
```

### Step 2: Create Environment Configuration

```bash
# Copy the example environment file
copy .env.example .env

# Edit .env with your settings:
# - Generate a new SECRET_KEY
# - Set DEBUG=False for production
# - Configure ALLOWED_HOSTS
# - Set email settings if needed
```

#### Generate Secure SECRET_KEY:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output and paste it in `.env`:

```
SECRET_KEY=your-generated-key-here
```

### Step 3: Apply Database Migrations

```bash
# Run migrations to add new security fields to UserProfile
python manage.py migrate users

# Check migration status
python manage.py migrate --check
```

### Step 4: Run Security Checks

```bash
# Django's built-in deployment security checks
python manage.py check --deploy
```

Expected output should show deployment checks passed.

### Step 5: Test the Application

```bash
# Run development server
python manage.py runserver

# In another terminal, test the login/register with rate limiting
```

---

## Environment Configuration

### Development (`.env`)

```
# Django Settings
DEBUG=True
SECRET_KEY=your-development-key
ALLOWED_HOSTS=127.0.0.1

# Security - Less strict in development
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False

# Rate Limiting
RATE_LIMIT_LOGIN=10
RATE_LIMIT_REGISTER=5
```

### Production (`.env`)

```
# Django Settings
DEBUG=False
SECRET_KEY=your-production-key-change-this
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Security - Strict in production
SECURE_SSL_REDIRECT=True
SESSION_COOKIE_SECURE=True
CSRF_COOKIE_SECURE=True
SESSION_COOKIE_AGE=3600

# Email Configuration (for password reset)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Admin Email
ADMIN_EMAIL=admin@yourdomain.com

# CSRF Trusted Origins
CSRF_TRUSTED_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

---

## Security Features Overview

### 1. **Rate Limiting**

- Prevents brute force attacks
- Login: 5 attempts per 5 minutes
- Registration: 3 attempts per 5 minutes

Testing:

```bash
# Try logging in with wrong password 6 times - you'll be rate limited
```

### 2. **Strong Password Requirements**

- Minimum 12 characters
- Uppercase, lowercase, number, special character required
- Cannot contain username or email

Testing:

```python
# In Django shell:
python manage.py shell

from users.security import InputValidator

# Test password validation
is_valid, error = InputValidator.validate_password("weak")
print(error)  # Error message shown

is_valid, error = InputValidator.validate_password("Strong@Pass123")
print(is_valid)  # True
```

### 3. **CSRF Protection**

- All forms include CSRF tokens
- Logout is POST-only (prevents CSRF attacks)
- Header validation enabled

### 4. **Input Validation**

- Username: alphanumeric, 3-30 chars
- Email: RFC-validated
- Password: strength checked

### 5. **Security Logging**

Logs are saved to `logs/security.log`:

```bash
# View security logs
tail -f logs/security.log
```

---

## Testing Security Features

### Test 1: Rate Limiting on Login

```bash
# 1. Try logging in with wrong password 6 times
# Expected: "Too many login attempts" on 6th try

# 2. Wait 5 minutes, then try again
# Expected: Should work again
```

### Test 2: Password Strength

Register with weak passwords:

```
- "123456" → Too short
- "Password1" → No special character
- "Pass@" → Too short
- "Pass@123456" → Success!
```

### Test 3: Account Lockout

```bash
# Run in Django shell:
python manage.py shell

from users.models import UserProfile
from django.contrib.auth.hashers import make_password

# Create a test user
user = UserProfile.objects.create(
    username='testuser',
    email='test@example.com',
    password=make_password('Test@12345')
)

# Simulate 5 failed logins
for i in range(5):
    user.record_failed_login()

# Check if locked
print(user.is_account_locked())  # Should be True
```

### Test 4: CSRF Protection

```bash
# Try submitting a form without CSRF token
# Expected: 403 Forbidden error

# Try using POST logout instead of GET
# Expected: Works correctly
```

---

## Monitoring & Maintenance

### Check Security Logs

```bash
# Monitor real-time
tail -f logs/security.log

# Count failed logins today
grep "login_failed" logs/security.log | wc -l

# Find brute force attempts
grep "rate_limit" logs/security.log
```

### Database Backups

```bash
# Backup SQLite database
cp db.sqlite3 db.sqlite3.backup.$(date +%Y%m%d)

# Or automated backup script:
```

Create `backup.sh`:

```bash
#!/bin/bash
BACKUP_DIR="backups"
mkdir -p $BACKUP_DIR
cp db.sqlite3 $BACKUP_DIR/db.sqlite3.$(date +%Y%m%d_%H%M%S)
# Keep only last 30 days
find $BACKUP_DIR -name "*.sqlite3" -mtime +30 -delete
```

### Update Dependencies Regularly

```bash
# Check for outdated packages
pip list --outdated

# Update Django
pip install --upgrade Django

# Update all packages
pip install --upgrade -r requirements.txt

# Review changes in Django release notes
```

---

## Production Deployment

### Before Going Live

1. **Database**: Migrate from SQLite to PostgreSQL

   ```bash
   # Install PostgreSQL driver
   pip install psycopg2-binary

   # Update settings.py DATABASES
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': 'mangadox_db',
           'USER': 'postgres',
           'PASSWORD': 'your-password',
           'HOST': 'localhost',
           'PORT': '5432',
       }
   }
   ```

2. **HTTPS/SSL Certificate**

   ```bash
   # Get free SSL certificate
   # Option 1: Let's Encrypt with Certbot
   sudo apt-get install certbot python3-certbot-nginx
   sudo certbot certonly --nginx -d yourdomain.com

   # Configure in .env
   SECURE_SSL_REDIRECT=True
   SECURE_HSTS_SECONDS=31536000
   ```

3. **Web Server**: Use Gunicorn + Nginx

   ```bash
   # Install
   pip install gunicorn

   # Run
   gunicorn MangaDox.wsgi:application --bind 0.0.0.0:8000
   ```

4. **Static Files**

   ```bash
   # Collect static files
   python manage.py collectstatic --noinput
   ```

5. **Environment Variables**
   - Ensure all secrets are in `.env`
   - Never commit `.env` to git
   - Add to `.gitignore`:
     ```
     .env
     *.log
     db.sqlite3
     ```

6. **Final Security Check**
   ```bash
   python manage.py check --deploy
   ```

---

## Common Issues & Solutions

### Issue: "SECRET_KEY not found"

```
Solution: Create .env file with SECRET_KEY=your-key
```

### Issue: "ALLOWED_HOSTS validation error"

```
Solution: Update ALLOWED_HOSTS in .env with your domain
```

### Issue: Rate limiting not working

```
Solution: Ensure Django cache is configured
# Add to settings.py:
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}
```

### Issue: Login redirects don't work

```
Solution: Ensure request.session is not corrupted
# Clear sessions:
python manage.py flush_sessions
```

---

## Support & Documentation

- **Security Guide**: [SECURITY.md](SECURITY.md)
- **Django Docs**: https://docs.djangoproject.com/en/6.0/
- **OWASP**: https://owasp.org/

---

## Next Steps

1. ✅ Deploy current security updates
2. ⬜ Implement email verification
3. ⬜ Add Two-Factor Authentication (2FA)
4. ⬜ Set up monitoring and alerting
5. ⬜ Regular security audits
6. ⬜ Implement backup strategy

---

**Last Updated**: February 18, 2026  
**Status**: Ready for Deployment ✅
