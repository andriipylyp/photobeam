from django.contrib import admin
from .models import UserProfile, ApplicationSettings

admin.site.register(UserProfile)
admin.site.register(ApplicationSettings)
