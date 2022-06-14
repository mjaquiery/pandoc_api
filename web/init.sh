#!/bin/sh
# init.sh

# adapted from https://docs.docker.com/compose/startup-order/

set -e
PGUP=1

while [ $PGUP -ne 0 ]; do
  pg_isready -d "$DATABASE_URL"
  PGUP=$?
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres ready - initalising"
python manage.py makemigrations
python manage.py migrate

>&2 echo "Launching celery workers"
celery --app=pandoc_api worker --hostname=worker@%h --loglevel=INFO --detach

>&2 echo "Initalisation complete - starting server"
#exec "$@"
python manage.py runserver 0.0.0.0:$PORT