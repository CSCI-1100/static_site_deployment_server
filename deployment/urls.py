from django.urls import path, re_path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('upload/', views.FileUploadView.as_view(), name='upload_files'),
    path('export/', views.export_files, name='export_files'),
    path('delete-file/<int:file_id>/', views.delete_file, name='delete_file'),
    # User static sites - these should be at the end
    # Pattern: /username/path/to/file.html
    re_path(r'^(?P<username>[a-zA-Z0-9_-]+)/(?P<path>.+)$', views.view_site, name='view_site_with_path'),
    # Pattern: /username/ or /username (serves index.html)
    re_path(r'^(?P<username>[a-zA-Z0-9_-]+)/?$', views.view_site, name='view_site'),
]