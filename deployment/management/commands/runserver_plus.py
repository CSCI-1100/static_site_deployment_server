# Django management command for HTTPS server
import ssl
from django.core.management.commands.runserver import Command as RunserverCommand
from django.core.management.base import CommandError

class Command(RunserverCommand):
    help = 'Run Django development server with SSL support'
    
    def add_arguments(self, parser):
        super().add_arguments(parser)
        parser.add_argument(
            '--cert-file',
            dest='cert_file',
            help='SSL certificate file path'
        )
        parser.add_argument(
            '--key-file', 
            dest='key_file',
            help='SSL private key file path'
        )
    
    def get_handler(self, *args, **options):
        handler = super().get_handler(*args, **options)
        
        cert_file = options.get('cert_file')
        key_file = options.get('key_file')
        
        if cert_file and key_file:
            # Wrap the handler with SSL
            import socket
            from wsgiref.simple_server import make_server, WSGIServer
            
            class SSLWSGIServer(WSGIServer):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, **kwargs)
                    self.socket = ssl.wrap_socket(
                        self.socket,
                        certfile=cert_file,
                        keyfile=key_file,
                        ssl_version=ssl.PROTOCOL_TLS,
                        server_side=True
                    )
            
            # Monkey patch to use SSL server
            import wsgiref.simple_server
            wsgiref.simple_server.WSGIServer = SSLWSGIServer
        
        return handler
