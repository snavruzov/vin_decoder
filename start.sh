#!/usr/bin/env bash
# Start Gunicorn processes
echo "Starting Gunicorn."
cd /vin_decoder

# Waiting for the database connection access
# to avoid django db connection issues
while ! exec 6<>/dev/tcp/vin-postgres/5432; do
    echo "Trying to connect to PostgreSQL at 5432..."
    sleep 10
done

# Synchronizing django models with database
python manage.py migrate
# Creating a default superuser to access django admin panel
echo "from django.contrib.auth.models import User; User.objects.filter(email='admin@example.com').delete(); User.objects.create_superuser('admin', 'admin@example.com', 'rhjrjlbk84637857')" | python manage.py shell

# Running gunicorn server with three workers
exec gunicorn VINService.wsgi:application \
    --bind 0.0.0.0:8000 \
    --workers 3