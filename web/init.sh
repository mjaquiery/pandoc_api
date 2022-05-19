#!/bin/sh
# init.sh

# adapted from https://docs.docker.com/compose/startup-order/

set -e

host="$1"
shift
shift

until PGPASSWORD=$POSTGRES_PASSWORD psql -h "$host" -U "$POSTGRES_USER" -c '\q'; do
  >&2 echo "Postgres is unavailable - sleeping"
  sleep 1
done

>&2 echo "Postgres ready - initalising"
python manage.py makemigrations
python manage.py migrate

>&2 echo "Initalisation complete - running command $*"
exec "$@"
