import os
import json
import zipfile
import mimetypes
import logging
import re
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.contrib import messages
from django.core.files.base import ContentFile
from django.http import HttpResponse, Http404, JsonResponse
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.views.static import serve
from django.conf import settings
from django.urls import reverse
from .models import UserProfile, UploadedFile
from .forms import UserProfileForm
from django.contrib.sites.models import Site
from .utils import get_current_site_url, get_user_site_url

logger = logging.getLogger(__name__)

def login_view(request):
    """Handle login page"""
    if request.user.is_authenticated:
        return redirect('dashboard')
    return render(request, 'registration/login.html')

@login_required
def dashboard(request):
    """Main dashboard view for file uploads and management"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    uploaded_files = UploadedFile.objects.filter(user=request.user).order_by('-uploaded_at')
    
    # Group files by type
    files_by_type = {
        'html': uploaded_files.filter(file_type='html'),
        'css': uploaded_files.filter(file_type='css'),
        'js': uploaded_files.filter(file_type='js'),
        'image': uploaded_files.filter(file_type='image'),
        'asset': uploaded_files.filter(file_type='asset'),
    }
    
    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Settings updated successfully!')
            return redirect('dashboard')
    else:
        form = UserProfileForm(instance=profile)
    
    context = {
        'profile': profile,
        'files_by_type': files_by_type,
        'form': form,
        'site_url': get_user_site_url(request.user.username, request),
        'base_site_url': get_current_site_url(request),
    }
    return render(request, 'dashboard.html', context)

def fix_html_paths(file_content, username):
    """
    Fix relative paths in HTML content to use absolute paths with username prefix
    
    Args:
        file_content (str): The HTML content as a string
        username (str): Username to prepend to paths
    
    Returns:
        str: Modified HTML content with fixed absolute paths
    """
    
    # Patterns to match and fix - now using absolute paths with leading slash
    patterns = [
        # src attributes: src="js/main.js" -> src="/username/js/main.js"
        (r'src\s*=\s*["\'](?!https?://|/|#)([^"\']+)["\']', f'src="/{username}/\\1"'),
        
        # href attributes for stylesheets and internal links: href="css/style.css" -> href="/username/css/style.css"
        (r'href\s*=\s*["\'](?!https?://|/|#|mailto:)([^"\']+\.(?:css|html|htm))["\']', f'href="/{username}/\\1"'),
        
        # CSS url() references: url('img/bg.jpg') -> url('/username/img/bg.jpg')
        (r'url\s*\(\s*["\']?(?!https?://|/|#)([^"\')\s]+)["\']?\s*\)', f'url("/{username}/\\1")'),
        
        # @import in CSS: @import "fonts.css" -> @import "/username/fonts.css"
        (r'@import\s+["\'](?!https?://|/)([^"\']+)["\']', f'@import "/{username}/\\1"'),
        
        # Handle navigation links without file extensions: href="about" -> href="/username/about.html"
        # This is for cases where students use href="about" instead of href="about.html"
        (r'href\s*=\s*["\'](?!https?://|/|#|mailto:)([a-zA-Z0-9_-]+)(?!\.)["\']', f'href="/{username}/\\1.html"'),
    ]
    
    modified_content = file_content
    changes_made = []
    
    for pattern, replacement in patterns:
        matches = re.findall(pattern, modified_content, re.IGNORECASE)
        if matches:
            for match in matches:
                changes_made.append(f"Fixed path: {match} -> /{username}/{match}")
            modified_content = re.sub(pattern, replacement, modified_content, flags=re.IGNORECASE)
    
    if changes_made:
        print(f"Fixed paths in HTML for user {username}:")
        for change in changes_made:
            print(f"  - {change}")
    
    return modified_content

def process_uploaded_file(uploaded_file, user, file_type):
    """
    Process uploaded files and fix paths if it's an HTML file
    
    Args:
        uploaded_file: Django UploadedFile object
        user: User object
        file_type: Type of file being uploaded
    
    Returns:
        UploadedFile: The processed file
    """
    
    # Only process HTML files
    if file_type == 'html' and uploaded_file.name.lower().endswith(('.html', '.htm')):
        try:
            # Read the file content
            uploaded_file.seek(0)  # Reset file pointer to beginning
            content = uploaded_file.read().decode('utf-8')
            
            # Fix the paths
            fixed_content = fix_html_paths(content, user.username)
            
            # Create a new file with the fixed content
            fixed_file = ContentFile(fixed_content.encode('utf-8'))
            fixed_file.name = uploaded_file.name
            
            print(f"Processed HTML file: {uploaded_file.name} for user {user.username}")
            return fixed_file
            
        except UnicodeDecodeError:
            print(f"Warning: Could not decode {uploaded_file.name} as UTF-8, serving as-is")
            return uploaded_file
        except Exception as e:
            print(f"Error processing {uploaded_file.name}: {str(e)}, serving as-is")
            return uploaded_file
    
    return uploaded_file

@method_decorator(csrf_exempt, name='dispatch')
class FileUploadView(View):
    """Handle AJAX file uploads with automatic path fixing"""
    
    def post(self, request):
        logger.info(f"FileUploadView: POST request from user {request.user}")
        
        if not request.user.is_authenticated:
            logger.warning("FileUploadView: Unauthenticated request")
            return JsonResponse({'error': 'Authentication required'}, status=401)
        
        files = request.FILES.getlist('files')
        file_type = request.POST.get('file_type', 'asset')
        
        logger.info(f"Processing {len(files)} files of type '{file_type}'")
        
        if not files:
            logger.warning("No files received in upload request")
            return JsonResponse({'error': 'No files provided'}, status=400)
        
        uploaded_files = []
        
        try:
            for file in files:
                logger.info(f"Processing file: {file.name} ({file.size} bytes)")
                
                # Validate file type
                if not self.is_valid_file_type(file, file_type):
                    logger.warning(f"Invalid file type for {file.name}")
                    continue
                
                # Create user directories if they don't exist
                user_dir = os.path.join(settings.MEDIA_ROOT, request.user.username)
                self.ensure_directories_exist(user_dir, file_type)
                
                # Process the file (fix HTML paths if needed)
                processed_file = process_uploaded_file(file, request.user, file_type)
                
                # Create uploaded file record
                uploaded_file = UploadedFile.objects.create(
                    user=request.user,
                    file=processed_file,
                    file_type=file_type,
                    original_name=file.name,
                    size=processed_file.size if hasattr(processed_file, 'size') else file.size
                )
                
                uploaded_files.append({
                    'id': uploaded_file.id,
                    'name': uploaded_file.original_name,
                    'size': uploaded_file.size,
                    'type': uploaded_file.file_type
                })
                
                logger.info(f"Successfully uploaded: {uploaded_file.original_name}")
        
        except Exception as e:
            logger.error(f"Error during file upload: {str(e)}", exc_info=True)
            return JsonResponse({'error': f'Upload failed: {str(e)}'}, status=500)
        
        logger.info(f"Upload complete: {len(uploaded_files)} files processed")
        return JsonResponse({'files': uploaded_files})
    
    def ensure_directories_exist(self, user_dir, file_type):
        """Create necessary directories for file organization"""
        os.makedirs(user_dir, exist_ok=True)
        
        if file_type == 'css':
            os.makedirs(os.path.join(user_dir, 'css'), exist_ok=True)
        elif file_type == 'js':
            os.makedirs(os.path.join(user_dir, 'js'), exist_ok=True)
        elif file_type in ['image', 'asset']:
            os.makedirs(os.path.join(user_dir, 'img'), exist_ok=True)
    
    def is_valid_file_type(self, file, expected_type):
        """Validate that the file matches the expected type"""
        name, ext = os.path.splitext(file.name.lower())
        
        type_extensions = {
            'html': ['.html', '.htm'],
            'css': ['.css'],
            'js': ['.js'],
            'image': ['.jpg', '.jpeg', '.png', '.gif', '.svg', '.webp'],
            'asset': ['.woff', '.woff2', '.ttf', '.otf', '.pdf', '.txt', '.ico']
        }
        
        allowed_extensions = type_extensions.get(expected_type, [])
        
        # For image type, also allow asset extensions
        if expected_type == 'image':
            allowed_extensions.extend(type_extensions['asset'])
        
        return ext in allowed_extensions

@login_required
def export_files(request):
    """Export all user files as a ZIP"""
    user_dir = os.path.join(settings.MEDIA_ROOT, request.user.username)
    
    if not os.path.exists(user_dir):
        messages.error(request, 'No files found to export.')
        return redirect('dashboard')
    
    response = HttpResponse(content_type='application/zip')
    response['Content-Disposition'] = f'attachment; filename="{request.user.username}_website.zip"'
    
    with zipfile.ZipFile(response, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(user_dir):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, user_dir)
                zipf.write(file_path, arcname)
    
    return response

def view_site(request, username, path=''):
    """Serve user's static website files directly"""
    # Verify user exists
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        raise Http404("User not found")
    
    # Build the file path
    user_dir = os.path.join(settings.MEDIA_ROOT, username)
    
    # If no path specified, default to index.html
    if not path:
        path = 'index.html'
    
    # Security check - prevent directory traversal
    if '..' in path or path.startswith('/'):
        raise Http404("Invalid path")
    
    # Full file path
    full_path = os.path.join(user_dir, path)
    
    # Check if the user directory exists
    if not os.path.exists(user_dir):
        return render(request, 'site_not_found.html', {'username': username})
    
    # Check if specific file exists
    if not os.path.exists(full_path):
        # If it's the default index.html, show site not found page
        if path == 'index.html':
            return render(request, 'site_not_found.html', {'username': username})
        else:
            raise Http404(f"File not found: {path}")
    
    # If it's a directory, try to serve index.html from it
    if os.path.isdir(full_path):
        index_file = os.path.join(full_path, 'index.html')
        if os.path.exists(index_file):
            full_path = index_file
            path = os.path.join(path, 'index.html')
        else:
            raise Http404("Directory index not found")
    
    # Use Django's built-in serve function for the actual file serving
    try:
        return serve(request, path, document_root=user_dir)
    except Http404:
        raise Http404(f"File not found: {path}")

@login_required
def delete_file(request, file_id):
    """Delete a specific file"""
    if request.method == 'POST':
        try:
            file = UploadedFile.objects.get(id=file_id, user=request.user)
            file.file.delete()  # Delete the actual file
            file.delete()  # Delete the database record
            messages.success(request, 'File deleted successfully.')
        except UploadedFile.DoesNotExist:
            messages.error(request, 'File not found.')
    
    return redirect('dashboard')
