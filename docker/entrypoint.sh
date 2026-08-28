#!/bin/sh
set -e

echo "Waiting for PostgreSQL..."
python << 'EOF'
import os
import sys
import time

import psycopg2

host = os.environ.get("DB_HOST", "db")
port = int(os.environ.get("DB_PORT", "5432"))
dbname = os.environ.get("DB_NAME", "doctor_platform")
user = os.environ.get("DB_USER", "postgres")
password = os.environ.get("DB_PASSWORD", "postgres")

for attempt in range(30):
    try:
        conn = psycopg2.connect(
            host=host,
            port=port,
            dbname=dbname,
            user=user,
            password=password,
        )
        conn.close()
        print("PostgreSQL is ready.")
        sys.exit(0)
    except psycopg2.OperationalError:
        print(f"Attempt {attempt + 1}/30 — DB not ready, retrying...")
        time.sleep(2)

print("Could not connect to PostgreSQL.")
sys.exit(1)
EOF

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec gunicorn config.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers "${GUNICORN_WORKERS:-2}" \
    --threads "${GUNICORN_THREADS:-2}" \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
