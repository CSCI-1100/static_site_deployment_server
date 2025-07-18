"""
Alternative HTTPS server runner using built-in Python SSL
Run with: python run_https_server.py
"""
import os
import sys
import ssl
import django
from django.core.wsgi import get_wsgi_application
from wsgiref.simple_server import make_server, WSGIServer
import socket

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'static_deploy.settings')
django.setup()

class SSLWSGIServer(WSGIServer):
    """WSGI Server with SSL support"""
    def __init__(self, server_address, RequestHandlerClass, cert_file, key_file):
        super().__init__(server_address, RequestHandlerClass)
        
        # Wrap socket with SSL
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        context.load_cert_chain(cert_file, key_file)
        self.socket = context.wrap_socket(self.socket, server_side=True)

def run_server():
    """Run the HTTPS development server"""
    cert_file = 'ssl/server.crt'
    key_file = 'ssl/server.key'
    
    if not os.path.exists(cert_file) or not os.path.exists(key_file):
        print("❌ SSL certificates not found!")
        print("Run ./generate_ssl.sh to create certificates")
        sys.exit(1)
    
    # Get WSGI application
    application = get_wsgi_application()
    
    # Create SSL server
    server = make_server(
        '0.0.0.0', 5000, application,
        server_class=lambda addr, handler: SSLWSGIServer(addr, handler, cert_file, key_file)
    )
    
    print("🚀 Starting HTTPS server...")
    print("📍 Server running at: https://csciauto1.etsu.edu:5000/")
    print("🛑 Press Ctrl+C to stop")
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n🛑 Server stopped")

if __name__ == '__main__':
    run_server()
