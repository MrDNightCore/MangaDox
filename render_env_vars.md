Render environment variables (paste these into your Web Service → Environment on Render)

- `DATABASE_URL`: postgresql://<username>:<password>@<host>.oregion-postgres.render.com:5432/<dbname>
- `SECRET_KEY`: (strong secret key)
- `DEBUG`: False
- `ALLOWED_HOSTS`: mangadox.onrender.com
- `CSRF_TRUSTED_ORIGINS`: https://mangadox.onrender.com
- `DB_SSL`: True
- `USE_S3`: True (if using S3 for media)
- `AWS_STORAGE_BUCKET_NAME`: your-bucket-name (if `USE_S3=True`)
- `AWS_ACCESS_KEY_ID`: YOUR_AWS_ACCESS_KEY_ID
- `AWS_SECRET_ACCESS_KEY`: YOUR_AWS_SECRET_ACCESS_KEY
- `EMAIL_HOST_USER`: your-email@example.com
- `EMAIL_HOST_PASSWORD`: your-email-password

Notes:

- Use the full External Database URL shown on your Render Postgres dashboard (copy the External Database URL field). Do NOT paste only the hostname fragment.
- Keep secrets out of the repository; paste them into Render's Environment or Secret Files.
- If you want to use Render's Internal DB URL, make sure the web service and DB are in the same region and private networking is enabled.
