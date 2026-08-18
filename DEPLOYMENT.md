# Deployment to Render (Step-by-step)

This guide shows the recommended steps to deploy MangaDox to Render using a managed PostgreSQL database and optional S3 media storage.

1. Preparations

- Ensure your repository has: `requirements.txt`, `build.sh`, `Procfile` and `MangaDox/settings.py` (this repo includes them).
- Ensure your code is committed and pushed to the Git remote used by Render.

2. Render resources

- Create a Render Postgres database (Managed Database) in the same region as your Web Service.
- Note the External Database URL and Internal Database URL on the DB page. Copy the External URL for public web services.

3. Required Render environment variables (Web Service → Environment)

- `DATABASE_URL` — full External Database URL from Render (postgresql://user:pass@host:5432/dbname)
- `SECRET_KEY` — strong random secret
- `DEBUG` — `False`
- `ALLOWED_HOSTS` — `mangadox.onrender.com` (or your Render service domain)
- `CSRF_TRUSTED_ORIGINS` — `https://mangadox.onrender.com`
- `DB_SSL` — `True` (if Render requires SSL)
- `USE_S3` — `True` (if using S3 for media), else leave unset/False
- `AWS_STORAGE_BUCKET_NAME`, `AWS_ACCESS_KEY_ID`, `AWS_SECRET_ACCESS_KEY` — if `USE_S3=True`
- `EMAIL_HOST_USER`, `EMAIL_HOST_PASSWORD` — production SMTP credentials (do NOT commit these)

4. Start command / Procfile

- `Procfile` should contain:

  web: gunicorn MangaDox.wsgi:application --bind 0.0.0.0:$PORT

5. Build & Deploy hooks

- `build.sh` in this repo runs during deploy. It installs requirements, runs `collectstatic` and `migrate`. It now includes a retry loop for `migrate` to tolerate transient DNS/DB readiness issues.
- Optional: Move `migrate` to a release hook or run migrations manually from Render Shell for safer control.

6. Recommended deploy steps

- On Render dashboard -> Web Service -> Environment, add the variables above.
- Trigger a Manual Deploy.
- Open Render Shell (Web Service -> Shell) and verify `DATABASE_URL`:

  python -c "import os; from urllib.parse import urlparse; print('DB=', os.environ.get('DATABASE_URL')); print('HOST=', urlparse(os.environ.get('DATABASE_URL') or '').hostname)"

- If the host prints as a full FQDN (like `dpg-xxxxx.oregon-postgres.render.com`) proceed. If it prints a short fragment, replace `DATABASE_URL` with the full External Database URL.

7. Post-deploy actions

- Run (if not already run):

  python manage.py migrate
  python manage.py collectstatic --noinput

- Create admin user:

  python manage.py createsuperuser

8. Data migration from SQLite (if needed)

- Locally export fixtures:

  ./scripts/export_data.sh data.json

- Upload `data.json` to the server (Render file upload or git) and run on server after `migrate`:

  python manage.py loaddata data.json

- Move `media/` files: upload to S3 and enable `USE_S3=True` and AWS env vars, or manually copy files to persistent storage.

9. Troubleshooting

- DNS / hostname resolve errors: ensure `DATABASE_URL` contains the full domain (not a truncated fragment). Use External DB URL for public web service unless using the Internal URL in the same region/private network.
- `psycopg2.OperationalError` while connecting: verify username/password, host, port, and `DB_SSL` setting.
- Build-time migrate failures: the `build.sh` retry loop helps; consider using a release hook.

10. Security checklist

- Never commit secrets (use Render Environment or Secret Files).
- Set `DEBUG=False` in production.
- Use HTTPS and set `SECURE_SSL_REDIRECT=True` and cookie security flags when `DEBUG=False`.

If you want, I can convert `migrate` into a Render Release Command and remove it from `build.sh`.
