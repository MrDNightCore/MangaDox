# Local installation & data migration (Step-by-step)

This file explains how to set up a local development environment, export existing data from SQLite, and prepare for migration to PostgreSQL.

1. Prerequisites

- Python 3.11+ (this repo used Python 3.14 in CI logs, but 3.11–3.14 should work). Use the same interpreter on server if possible.
- `git`, `pip`, virtualenv or `python -m venv`.
- AWS CLI (optional) if planning to use S3.

2. Create and activate a virtualenv (Windows PowerShell):

```powershell
python -m venv env
.\env\Scripts\Activate.ps1
pip install --upgrade pip
```

3. Install requirements

```bash
pip install -r requirements.txt
```

4. Local settings

- Copy `.env.example` to `.env` and edit values for local development (keep `DATABASE_URL=sqlite:///db.sqlite3` by default).

```powershell
copy .env.example .env
# then edit .env in an editor
```

5. Run migrations and start locally

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py collectstatic --noinput
python manage.py runserver
```

6. Export existing data (SQLite -> fixtures)

- Export to `data.json` using the helper script:

```bash
./scripts/export_data.sh data.json
```

7. Preparing to import into Postgres (on Render or other host)

- Ensure `DATABASE_URL` on the target points to a PostgreSQL database.
- Upload `data.json` to the server (via git, Render file upload, or SFTP).
- On the server, after `migrate`, run:

```bash
python manage.py loaddata data.json
```

8. Media files

- For uploaded images (`media/chapter_images/`), move files to S3:
  - Create an S3 bucket and IAM user with write permissions.
  - Set `USE_S3=True` and `AWS_*` env vars on the server.
  - Copy the `media/` directory to the S3 bucket (aws cli `aws s3 sync media/ s3://your-bucket/`)

9. Tests and verification

- Run tests locally:

```bash
pytest
```

- Manually test key pages: homepage, manga list, manga detail, chapter reader, login/register, admin.

10. Common errors & fixes

- `OperationalError: could not translate host name` — full `DATABASE_URL` host is missing or truncated. Use the full External DB URL from Render.
- `Permission denied` when writing static/media — ensure file permissions or use S3 for media in production.

If you'd like, I can produce a runnable `docker-compose.yml` for local Postgres + web to reproduce production behavior before deploying.
