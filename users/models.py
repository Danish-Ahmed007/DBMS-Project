from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    """Custom user model that extends Django's AbstractUser to include location."""
    location = models.CharField(max_length=100)
    
    def __str__(self):
        return self.username
