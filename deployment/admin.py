from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.urls import path, reverse
from django.http import HttpResponse
from django.contrib import messages
from django.utils.html import format_html
from .models import UserProfile, UploadedFile
from .forms import BulkUserUploadForm
import csv
import io

class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'

class CustomUserAdmin(UserAdmin):
    inlines = (UserProfileInline,)
    
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('bulk-upload/', self.admin_site.admin_view(self.bulk_upload_view), name='auth_user_bulk_upload'),
        ]
        return custom_urls + urls
    
    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        # Add bulk upload button to the changelist
        extra_context['bulk_upload_url'] = reverse('admin:auth_user_bulk_upload')
        return super().changelist_view(request, extra_context)
    
    def bulk_upload_view(self, request):
        if request.method == 'POST':
            form = BulkUserUploadForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = request.FILES['csv_file']
                
                try:
                    # Read CSV file
                    decoded_file = csv_file.read().decode('utf-8')
                    csv_reader = csv.DictReader(io.StringIO(decoded_file))
                    
                    created_count = 0
                    errors = []
                    
                    for row_num, row in enumerate(csv_reader, start=2):  # Start at 2 for header
                        try:
                            # Validate required fields
                            required_fields = ['First Name', 'Last Name', 'Email', 'Password']
                            for field in required_fields:
                                if not row.get(field, '').strip():
                                    errors.append(f"Row {row_num}: Missing {field}")
                                    continue
                            
                            if errors:
                                continue
                            
                            email = row['Email'].strip()
                            username = email.split('@')[0]  # Use email prefix as username
                            
                            # Check if user already exists
                            if User.objects.filter(username=username).exists():
                                errors.append(f"Row {row_num}: Username '{username}' already exists")
                                continue
                            
                            if User.objects.filter(email=email).exists():
                                errors.append(f"Row {row_num}: Email '{email}' already exists")
                                continue
                            
                            # Create user
                            user = User.objects.create_user(
                                username=username,
                                email=email,
                                password=row['Password'].strip(),
                                first_name=row['First Name'].strip(),
                                last_name=row['Last Name'].strip()
                            )
                            
                            # Create profile (should be automatic via signals, but ensure it exists)
                            UserProfile.objects.get_or_create(user=user)
                            created_count += 1
                            
                        except Exception as e:
                            errors.append(f"Row {row_num}: Error creating user - {str(e)}")
                    
                    # Show results
                    if created_count > 0:
                        messages.success(request, f'Successfully created {created_count} users.')
                    
                    if errors:
                        error_message = f"Encountered {len(errors)} errors:\n" + "\n".join(errors[:10])
                        if len(errors) > 10:
                            error_message += f"\n... and {len(errors) - 10} more errors."
                        messages.error(request, error_message)
                    
                    if created_count > 0:
                        return redirect('admin:auth_user_changelist')
                        
                except Exception as e:
                    messages.error(request, f'Error processing CSV: {str(e)}')
        else:
            form = BulkUserUploadForm()
        
        return render(request, 'admin/bulk_upload.html', {
            'form': form,
            'title': 'Bulk Upload Users',
            'site_title': 'Static Site Deployment Admin',
            'has_permission': True,
        })

# Unregister the default UserAdmin and register our custom one
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)

@admin.register(UploadedFile)
class UploadedFileAdmin(admin.ModelAdmin):
    list_display = ['user', 'original_name', 'file_type', 'size', 'uploaded_at']
    list_filter = ['file_type', 'uploaded_at']
    search_fields = ['user__username', 'original_name']
    readonly_fields = ['uploaded_at']

# Custom admin site configuration
admin.site.site_header = 'Static Site Deployment Admin'
admin.site.site_title = 'Static Site Admin'
admin.site.index_title = 'Welcome to Static Site Deployment Administration'
