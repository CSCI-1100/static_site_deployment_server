#! /bin/bash -
# run_server.sh - HTTP development server startup script

echo "🚀 Starting Static Site Deployment Server"

# Activate virtual environment
source venv/bin/activate

# Collect static files
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

# Start the server without SSL
echo "🌐 Starting HTTP server on 0.0.0.0:5000..."
python manage.py runserver 0.0.0.0:5000