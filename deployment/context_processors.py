from .utils import get_current_site_url, get_user_site_url
import logging

logger = logging.getLogger(__name__)

def site_context(request):
    """Add site information to all templates with error handling"""
    context = {}
    
    try:
        context['current_site_url'] = get_current_site_url(request)
        
        if request.user.is_authenticated:
            context['user_site_url'] = get_user_site_url(request.user.username, request)
            
    except Exception as e:
        logger.warning(f"Error in site_context: {e}")
        # Provide fallback values
        protocol = 'https' if request.is_secure() else 'http'
        host = request.get_host()
        context['current_site_url'] = f"{protocol}://{host}"
        
        if request.user.is_authenticated:
            context['user_site_url'] = f"{protocol}://{host}/{request.user.username}"
    
    return context