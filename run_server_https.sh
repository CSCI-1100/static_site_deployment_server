#! /bin/bash -
# run_server.sh - HTTPS server startup script

echo "🚀 Starting Static Site Deployment Server"

# Activate virtual environment
source venv/bin/activate

# Collect static files
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

# Start the server without SSL
python run_https_server.py