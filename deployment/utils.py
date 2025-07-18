import os
import mimetypes
from django.conf import settings
from django.contrib.sites.models import Site
from django.core.exceptions import ImproperlyConfigured
import logging

logger = logging.getLogger(__name__)

def get_current_site_url(request=None):
    """Get the current site URL with protocol"""
    try:
        # Try to get from Sites framework
        current_site = Site.objects.get_current(request)
        protocol = 'https' if getattr(settings, 'USE_TLS', True) else 'http'
        
        # Handle port in domain
        if ':' in current_site.domain:
            return f"{protocol}://{current_site.domain}"
        else:
            # Check if we need to add a port
            port = getattr(settings, 'PORT', 5000)
            default_port = 443 if protocol == 'https' else 80
            
            if port not in [default_port, 80, 443]:
                return f"{protocol}://{current_site.domain}:{port}"
            else:
                return f"{protocol}://{current_site.domain}"
                
    except Exception as e:
        logger.warning(f"Could not get site from database: {e}")
        
        # Fallback: try to construct from request
        if request:
            protocol = 'https' if request.is_secure() else 'http'
            host = request.get_host()
            return f"{protocol}://{host}"
        
        # Final fallback: use settings
        protocol = 'https' if getattr(settings, 'USE_TLS', True) else 'http'
        port = getattr(settings, 'PORT', 5000)
        
        # Try to get hostname from ALLOWED_HOSTS
        allowed_hosts = getattr(settings, 'ALLOWED_HOSTS', [])
        for host in allowed_hosts:
            if host and host != '*' and host not in ['localhost', '127.0.0.1']:
                if port in [80, 443]:
                    return f"{protocol}://{host}"
                else:
                    return f"{protocol}://{host}:{port}"
        
        # Ultimate fallback
        if port in [80, 443]:
            return f"{protocol}://localhost"
        else:
            return f"{protocol}://localhost:{port}"

def get_user_site_url(username, request=None):
    """Get the full URL for a user's static site"""
    base_url = get_current_site_url(request)
    return f"{base_url}/{username}"

def update_site_configuration(domain, name="Static Site Deployment Server"):
    """Update site configuration safely"""
    try:
        site, created = Site.objects.get_or_create(id=1)
        site.domain = domain
        site.name = name
        site.save()
        
        action = "Created" if created else "Updated"
        logger.info(f"{action} site configuration: {name} at {domain}")
        return site
        
    except Exception as e:
        logger.error(f"Failed to update site configuration: {e}")
        return None

def get_file_type(filename):
    """Determine file type based on extension"""
    name, ext = os.path.splitext(filename.lower())
    
    if ext in ['.html', '.htm']:
        return 'html'
    elif ext == '.css':
        return 'css'
    elif ext == '.js':
        return 'js'
    elif ext in ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp']:
        return 'image'
    else:
        return 'asset'

def format_file_size(size_bytes):
    """Convert bytes to human readable format"""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f} {size_names[i]}"

def validate_file_upload(file):
    """Validate uploaded file"""
    max_size = getattr(settings, 'FILE_UPLOAD_MAX_MEMORY_SIZE', 10 * 1024 * 1024)
    
    if file.size > max_size:
        return False, f"File too large. Maximum size is {format_file_size(max_size)}"
    
    # Check file type
    file_type = get_file_type(file.name)
    allowed_extensions = [
        '.html', '.htm', '.css', '.js',
        '.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp',
        '.woff', '.woff2', '.ttf', '.otf', '.pdf', '.txt'
    ]
    
    name, ext = os.path.splitext(file.name.lower())
    if ext not in allowed_extensions:
        return False, f"File type {ext} not allowed"
    
    return True, "Valid file"
