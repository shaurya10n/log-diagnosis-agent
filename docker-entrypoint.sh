#!/bin/bash
set -e

echo "Waiting for PostgreSQL..."
python - <<'PY'
import os
import sys
import time

import psycopg2

database_url = os.environ.get("DATABASE_URL")
if not database_url:
    sys.exit("DATABASE_URL is not set")

for attempt in range(30):
    try:
        psycopg2.connect(database_url).close()
        print("PostgreSQL is ready.")
        break
    except psycopg2.OperationalError:
        time.sleep(1)
else:
    sys.exit("PostgreSQL did not become ready in time.")
PY

exec uvicorn app.main:app --host 0.0.0.0 --port 8000
