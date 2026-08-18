#!/usr/bin/env bash
# Render build script – runs on every deploy
set -o errexit  # exit on error

pip install --upgrade pip
pip install -r requirements.txt

python manage.py collectstatic --no-input
# Retry migrations a few times to tolerate transient DNS/DB readiness during deploys
attempts=0
until python manage.py migrate --no-input || [ $attempts -ge 5 ]; do
	attempts=$((attempts+1))
	echo "migrate failed, retrying in 5s (attempt $attempts)..."
	sleep 5
done
# Seed accounts but don't fail the build if seeding has issues
python manage.py seed_accounts || true
