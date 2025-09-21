#!/bin/bash

# Wait for Postgres
echo "Waiting for Postgres..."
while ! pg_isready -h db -p 5433 >/dev/null 2>&1; do
  sleep 2
done
echo "Postgres is ready!"

# Wait for Elasticsearch
echo "Waiting for Elasticsearch..."
while ! curl -s http://elasticsearch:9200 >/dev/null 2>&1; do
  sleep 2
done
echo "Elasticsearch is ready!"

set -e  # exit on error
echo "Running collectstatic..."
python manage.py collectstatic --noinput

echo "Running migrations..."
python manage.py makemigrations --noinput
python manage.py migrate --noinput


echo "Starting Gunicorn..."
exec gunicorn --bind 0.0.0.0:8000 --workers 3 elasticsearchapi.wsgi:application