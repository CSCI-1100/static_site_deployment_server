# Dockerfile (Alternative deployment option)
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create media directory
RUN mkdir -p media && chmod 755 media

# Collect static files
RUN python manage.py collectstatic --noinput

# Expose port
EXPOSE 5000

# Run server
CMD ["gunicorn", "static_deploy.wsgi:application", "--bind", "0.0.0.0:5000", "--workers", "3"]

---

# nginx.conf (For production deployment behind nginx)
server {
    listen 5000 ssl;
    server_name csciauto1.etsu.edu;
    
    ssl_certificate /path/to/ssl/server.crt;
    ssl_certificate_key /path/to/ssl/server.key;
    
    client_max_body_size 50M;
    
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
    
    location /media/ {
        alias /path/to/your/project/media/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }
    
    location /static/ {
        alias /path/to/your/project/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, no-transform";
    }
}