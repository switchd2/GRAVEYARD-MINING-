#!/usr/bin/env sh
set -e

# If DATABASE_URL starts with postgresql, wait for the database to be reachable
if echo "$DATABASE_URL" | grep -q "^postgresql"; then
  echo "Waiting for PostgreSQL database..."
  python -c "
import sys, time, os, urllib.parse
import psycopg2

db_url = os.getenv('DATABASE_URL')
for i in range(30):
    try:
        conn = psycopg2.connect(db_url)
        conn.close()
        print('PostgreSQL is ready!')
        sys.exit(0)
    except Exception as e:
        print(f'Waiting for DB connection... ({e})')
        time.sleep(2)
sys.exit(1)
"
fi

echo "Running database migrations..."
alembic upgrade head

echo "Starting application server..."
exec gunicorn app:app -k uvicorn.workers.UvicornWorker -w 2 -b 0.0.0.0:${PORT:-8000}
