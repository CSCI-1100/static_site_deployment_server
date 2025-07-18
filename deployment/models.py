from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
import os
import shutil

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    site_name = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s Profile"
    
    def get_site_url(self):
        return reverse('view_site', kwargs={'username': self.user.username})
    
    def get_media_path(self):
        return os.path.join('media', self.user.username)
    
    def delete_user_files(self):
        """Delete all files for this user"""
        media_path = os.path.join('media', self.user.username)
        if os.path.exists(media_path):
            shutil.rmtree(media_path)

class UploadedFile(models.Model):
    FILE_TYPES = [
        ('html', 'HTML'),
        ('css', 'CSS'),
        ('js', 'JavaScript'),
        ('image', 'Image'),
        ('asset', 'Asset'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    file = models.FileField(upload_to='')
    file_type = models.CharField(max_length=10, choices=FILE_TYPES)
    original_name = models.CharField(max_length=255)
    size = models.PositiveIntegerField()
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    def save(self, *args, **kwargs):
        if self.file:
            # Set upload path based on file type and user
            if self.file_type == 'css':
                self.file.name = f"{self.user.username}/css/{self.original_name}"
            elif self.file_type == 'js':
                self.file.name = f"{self.user.username}/js/{self.original_name}"
            elif self.file_type == 'image' or self.file_type == 'asset':
                self.file.name = f"{self.user.username}/img/{self.original_name}"
            else:  # html
                self.file.name = f"{self.user.username}/{self.original_name}"
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.user.username} - {self.original_name}"
