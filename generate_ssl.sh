#! /bin/bash -
# generate_ssl.sh - Generate self-signed SSL certificate

echo "🔒 Generating self-signed SSL certificate..."

# Create ssl directory
mkdir -p ssl

# Generate private key
openssl genrsa -out ssl/server.key 2048

# Generate certificate signing request
openssl req -new -key ssl/server.key -out ssl/server.csr -subj "/C=US/ST=Tennessee/L=Johnson City/O=ETSU/OU=Computer Science/CN=csciauto1.etsu.edu"

# Generate self-signed certificate
openssl x509 -req -days 365 -in ssl/server.csr -signkey ssl/server.key -out ssl/server.crt

# Set appropriate permissions
chmod 600 ssl/server.key
chmod 644 ssl/server.crt

echo "✅ SSL certificate generated in ssl/ directory"
echo "Note: Browsers will show a security warning for self-signed certificates."
echo "Students should proceed anyway for local development."