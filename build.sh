#!/usr/bin/env bash
# Render build script – runs on every deploy
set -o errexit  # exit on error

pip install --upgrade pip
pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate --no-input
python manage.py seed_accounts
