#!/bin/bash
# setup.sh - Interactive setup script with user input

echo "🚀 Setting up Static Site Deployment Server"
echo "==========================================="

# Check if Python 3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed. Please install Python 3.8 or later."
    exit 1
fi

# Get domain/hostname from user
echo ""
echo "🌐 Network Configuration"
echo "========================"
echo "What domain/hostname will students use to access this server?"
echo ""
echo "Examples:"
echo "  - <your_hostname>.etsu.edu (if hosted on ETSU's domain)"
echo "  - <your_hostname>.local (for local network)"
echo "  - 192.168.1.100 (if using IP address)"
echo "  - localhost (for local development only)"
echo ""
read -p "Enter the domain/hostname: " DOMAIN

# Validate domain input
if [ -z "$DOMAIN" ]; then
    echo "❌ Domain cannot be empty. Please run the script again."
    exit 1
fi

# Get port from user
echo ""
echo "🔌 Port Configuration"
echo "===================="
echo "What port should the server run on?"
echo ""
echo "Common choices:"
echo "  - 5000 (default for development)"
echo "  - 8000 (alternative development port)"
echo "  - 443 (standard HTTPS, requires root/sudo)"
echo "  - 80 (standard HTTP, requires root/sudo)"
echo ""
read -p "Enter the port [default: 5000]: " PORT
PORT=${PORT:-5000}

# Validate port
if ! [[ "$PORT" =~ ^[0-9]+$ ]] || [ "$PORT" -lt 1 ] || [ "$PORT" -gt 65535 ]; then
    echo "❌ Invalid port number. Please enter a number between 1 and 65535."
    exit 1
fi

# Ask about HTTPS
echo ""
echo "🔒 HTTPS Configuration"
echo "====================="
echo "Will you be using HTTPS (SSL certificates)?"
echo ""
echo "Choose HTTPS if:"
echo "  - You want secure connections (recommended)"
echo "  - Students will access from different networks"
echo "  - You're using this in production"
echo ""
echo "Choose HTTP if:"
echo "  - You're only testing locally"
echo "  - You have network restrictions with SSL"
echo ""
read -p "Use HTTPS? [Y/n]: " USE_HTTPS
USE_HTTPS=${USE_HTTPS:-Y}

# Convert to boolean
if [[ "$USE_HTTPS" =~ ^[Yy]$ ]]; then
    USE_TLS=True
    PROTOCOL="https"
else
    USE_TLS=False
    PROTOCOL="http"
fi

# Build full URL
if [ "$PORT" == "443" ] && [ "$PROTOCOL" == "https" ]; then
    FULL_URL="https://$DOMAIN"
    DOMAIN_WITH_PORT="$DOMAIN"
elif [ "$PORT" == "80" ] && [ "$PROTOCOL" == "http" ]; then
    FULL_URL="http://$DOMAIN"
    DOMAIN_WITH_PORT="$DOMAIN"
else
    FULL_URL="$PROTOCOL://$DOMAIN:$PORT"
    DOMAIN_WITH_PORT="$DOMAIN:$PORT"
fi

# Show configuration summary
echo ""
echo "📋 Configuration Summary"
echo "======================="
echo "Domain/Hostname: $DOMAIN"
echo "Port: $PORT"
echo "Protocol: $PROTOCOL"
echo "Full URL: $FULL_URL"
echo "Students will access: $FULL_URL"
echo "Admin panel: $FULL_URL/admin/"
echo ""
read -p "Is this correct? [Y/n]: " CONFIRM
CONFIRM=${CONFIRM:-Y}

if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
    echo "❌ Setup cancelled. Please run the script again with correct settings."
    exit 1
fi

echo ""
echo "✅ Configuration confirmed. Starting setup..."
echo ""

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file with proper CSRF origins
echo "🔑 Creating .env file..."
cat > .env << EOL
SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1,$DOMAIN
USE_TLS=$USE_TLS
PORT=$PORT
ADDITIONAL_CSRF_ORIGINS=$FULL_URL
EOL

echo "📝 Created .env file with your configuration"

# Run Django migrations
echo "🗄️  Setting up database..."
python manage.py makemigrations
python manage.py makemigrations deployment
python manage.py migrate

# Setup site configuration
echo "🌐 Configuring Django site settings..."
python manage.py setup_site --domain "$DOMAIN_WITH_PORT" --name "Static Site Deployment Server"

# Generate SSL certificates if using HTTPS
if [ "$USE_TLS" == "True" ]; then
    echo "🔒 Generating SSL certificates..."
    if [ -f "./generate_ssl.sh" ]; then
        ./generate_ssl.sh "$DOMAIN"
    else
        echo "⚠️  SSL certificate generation script not found."
        echo "    You may need to generate certificates manually."
    fi
else
    echo "ℹ️  Skipping SSL certificate generation (HTTP mode)"
fi

# Create superuser
echo ""
echo "👤 Creating admin user..."
echo "You'll need to create an admin account to manage users:"
python manage.py createsuperuser

# Create media directories
echo "📁 Creating media directories..."
mkdir -p media
chmod 755 media

# Show completion summary
echo ""
echo "🎉 Setup Complete!"
echo "=================="
echo ""
echo "✅ Server configured for: $FULL_URL"
echo "✅ Database created and migrated"
echo "✅ Admin user created"
echo "✅ Media directories created"
if [ "$USE_TLS" == "True" ]; then
    echo "✅ SSL certificates generated"
fi
echo ""
echo "🚀 To start the server:"
echo "   source venv/bin/activate"
if [ "$USE_TLS" == "True" ]; then
    echo "   ./run_server.sh"
else
    echo "   python manage.py runserver 0.0.0.0:$PORT"
fi
echo ""
echo "🌐 Access URLs:"
echo "   Dashboard: $FULL_URL"
echo "   Admin Panel: $FULL_URL/admin/"
echo "   Student Sites: $FULL_URL/username/"
echo ""
echo "📚 Next Steps:"
echo "   1. Start the server using the command above"
echo "   2. Open the admin panel and bulk upload your student list"
echo "   3. Share the dashboard URL with students"
echo ""
if [ "$USE_TLS" == "True" ]; then
    echo "⚠️  Note: Browsers will show a security warning for self-signed certificates."
    echo "   Students should click 'Advanced' and 'Proceed anyway' to continue."
fi
echo ""

---

# generate_ssl.sh - Updated to accept domain parameter

#!/bin/bash
# generate_ssl.sh - Generate self-signed SSL certificate with custom domain

DOMAIN=${1:-localhost}

echo "🔒 Generating self-signed SSL certificate for domain: $DOMAIN"

# Create ssl directory
mkdir -p ssl

# Generate private key
openssl genrsa -out ssl/server.key 2048

# Generate certificate signing request with provided domain
openssl req -new -key ssl/server.key -out ssl/server.csr -subj "/C=US/ST=Tennessee/L=Johnson City/O=ETSU/OU=Computer Science/CN=$DOMAIN"

# Generate self-signed certificate
openssl x509 -req -days 365 -in ssl/server.csr -signkey ssl/server.key -out ssl/server.crt

# Set appropriate permissions
chmod 600 ssl/server.key
chmod 644 ssl/server.crt

echo "✅ SSL certificate generated for $DOMAIN in ssl/ directory"
echo ""
echo "Certificate details:"
echo "  Domain: $DOMAIN"
echo "  Valid for: 365 days"
echo "  Files created:"
echo "    - ssl/server.crt (certificate)"
echo "    - ssl/server.key (private key)"
echo "    - ssl/server.csr (certificate request)"
echo ""
echo "⚠️  Note: This is a self-signed certificate."
echo "   Browsers will show a security warning."
echo "   For production, consider getting a proper SSL certificate."

---

# run_server.sh - Updated to use environment variables

#!/bin/bash
# run_server.sh - Start server with configuration from .env

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "❌ .env file not found. Please run ./setup.sh first."
    exit 1
fi

echo "🚀 Starting Static Site Deployment Server"
echo "Domain: ${ALLOWED_HOSTS##*,}"
echo "Port: ${PORT:-5000}"
echo "HTTPS: ${USE_TLS:-True}"

# Activate virtual environment
source venv/bin/activate

# Collect static files
echo "📦 Collecting static files..."
python manage.py collectstatic --noinput

# Check SSL certificates if using HTTPS
if [ "${USE_TLS:-True}" == "True" ]; then
    if [ ! -f "ssl/server.crt" ] || [ ! -f "ssl/server.key" ]; then
        echo "❌ SSL certificates not found!"
        echo "🔧 Please run ./setup.sh to generate certificates."
        exit 1
    fi
    
    echo "🌐 Starting HTTPS server on 0.0.0.0:${PORT:-5000}..."
    if python -c "import django_extensions" 2>/dev/null; then
        python manage.py runserver_plus 0.0.0.0:${PORT:-5000} \
            --cert-file ssl/server.crt \
            --key-file ssl/server.key
    else
        python run_https_server.py
    fi
else
    echo "🌐 Starting HTTP server on 0.0.0.0:${PORT:-5000}..."
    python manage.py runserver 0.0.0.0:${PORT:-5000}
fi