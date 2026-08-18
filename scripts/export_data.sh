#!/usr/bin/env bash
# Export Django data fixtures for migrating from SQLite to Postgres.
set -euo pipefail

# Usage: ./scripts/export_data.sh data.json
OUT=${1:-data.json}
echo "Exporting data to $OUT"
pip install -r requirements.txt --quiet || true
python manage.py dumpdata --natural-foreign --natural-primary --exclude auth.permission --exclude contenttypes > "$OUT"
echo "Done: $OUT"
