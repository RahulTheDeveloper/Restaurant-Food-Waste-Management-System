#!/bin/bash

echo "📦 Starting up the container..."

echo "🧩 Applying migrations..."
python manage.py makemigrations
python manage.py migrate

echo "📁 Collecting static files..."
python manage.py collectstatic --noinput

echo "🚀 Starting Gunicorn server..."
exec gunicorn food_waste_management.wsgi:application --bind 0.0.0.0:8080
