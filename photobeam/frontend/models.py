from datetime import datetime, timedelta
import os
import uuid
from django.db import models
from django.contrib.auth.models import User

from django.db.models.signals import post_delete
from django.dispatch import receiver

def default_event_date_end():
    return datetime.now() + timedelta(days=7)

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    def __str__(self):
        return self.user.username

class Album(models.Model):
    name = models.TextField(default="Missing name")
    user_profile = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="albums")
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    event_date_start = models.DateTimeField(default=datetime.now)
    event_date_end = models.DateTimeField(default=default_event_date_end)

    def __str__(self):
        return f"Album for {self.user_profile.user.username} - {self.unique_id}"

class UploadedImage(models.Model):
    album = models.ForeignKey(Album, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="uploaded_images/")
    uploaded_at = models.DateTimeField(auto_now_add=True)
    processing_speed = models.IntegerField(default=0)

    def __str__(self):
        return f"Image in album {self.album.unique_id} uploaded at {self.uploaded_at}"

class ApplicationSettings(models.Model):
    app_name = models.CharField(max_length=255, default="My Application")
    mobile = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    facebook_url = models.CharField(max_length=255, blank=True, null=True)
    twitter_url = models.CharField(max_length=255, blank=True, null=True)
    linkedin_url = models.CharField(max_length=255, blank=True, null=True)
    instagram_url = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return "Application Settings"

    class Meta:
        verbose_name = "Application Setting"
        verbose_name_plural = "Application Settings"

@receiver(post_delete, sender=UploadedImage)
def delete_image_file(sender, instance, **kwargs):
    """
    Delete the image file from the file system when the UploadedImage object is deleted.
    """
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)