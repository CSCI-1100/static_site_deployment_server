from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile
import os
import shutil
from django.conf import settings

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create UserProfile when User is created"""
    if created:
        UserProfile.objects.create(user=instance)
        
        # Create user directory structure
        user_dir = os.path.join(settings.MEDIA_ROOT, instance.username)
        os.makedirs(user_dir, exist_ok=True)
        os.makedirs(os.path.join(user_dir, 'css'), exist_ok=True)
        os.makedirs(os.path.join(user_dir, 'js'), exist_ok=True)
        os.makedirs(os.path.join(user_dir, 'img'), exist_ok=True)

@receiver(post_delete, sender=User)
def delete_user_files(sender, instance, **kwargs):
    """Delete user files when User is deleted"""
    user_dir = os.path.join(settings.MEDIA_ROOT, instance.username)
    if os.path.exists(user_dir):
        shutil.rmtree(user_dir)
