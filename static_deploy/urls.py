from django.contrib import admin
from django.contrib.auth import logout
from django.shortcuts import redirect
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve

def simple_admin_logout(request):
    logout(request)
    return redirect('/admin/')

urlpatterns = [
    path('admin/logout/', simple_admin_logout),  # Add this line FIRST
    path('admin/', admin.site.urls),
    path('', include('deployment.urls')),
]

# Serve media files (user uploads) in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Alternative: Direct media serving for user sites
# This serves files directly from /media/username/ as static content
urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
]
