#!/usr/bin/env bash

cd /code
echo "waiting on postgres"
while ! psql -U postgres -c "SELECT 'DBD::Pg ping test'" 2>/dev/null; do
    sleep 3
    echo "..."
done

python3 manage.py migrate --noinput
python3 manage.py collectstatic --noinput
python3 manage.py runserver_plus 0.0.0.0:8000
