#!/usr/bin/env bash
cd /app
echo "waiting on postgres"
while ! psql -U postgres -h db -c "SELECT 'DBD::Pg ping test'" 2>/dev/null; do
    sleep 3
    echo "..."
done
python manage.py migrate --noinput
python manage.py collectstatic --noinput
python manage.py runserver 0.0.0.0:8000
