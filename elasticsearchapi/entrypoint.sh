#!/bin/bash
set -e

echo "Waiting for Postgres..."
timeout=180
elapsed=0
until pg_isready -h db -p 5432 >/dev/null 2>&1 || [ $elapsed -ge $timeout ]; do
  echo "Waiting for Postgres... ($elapsed/$timeout)"
  sleep 2
  elapsed=$((elapsed + 2))
done

if [ $elapsed -ge $timeout ]; then
  echo "Postgres did not start within $timeout seconds."
  exit 1
fi
echo "Postgres is ready!"

echo "Waiting for Elasticsearch..."
elapsed=0
while ! curl -s http://esearch:9200 >/dev/null 2>&1 && [ $elapsed -lt $timeout ]; do
  echo "Waiting for Elasticsearch... ($elapsed/$timeout)"
  sleep 2
  elapsed=$((elapsed + 2))
done

if [ $elapsed -ge $timeout ]; then
  echo "Elasticsearch did not start within $timeout seconds."
  exit 1
fi
echo "Elasticsearch is ready!"

echo "Running collectstatic..."
python manage.py collectstatic --noinput

echo "Running migrations..."
#python manage.py makemigrations --noinput
python manage.py migrate --noinput

echo "Starting Gunicorn..."
#exec gunicorn --bind 0.0.0.0:8000 --workers 3 elasticsearchapi.wsgi:application

echo "Starting Supervisor..."
exec /usr/bin/supervisord -c /etc/supervisor/conf.d/supervisord.conf
