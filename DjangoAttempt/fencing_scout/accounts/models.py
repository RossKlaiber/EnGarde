from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    USER_TYPES = [
        ('athlete', 'Athlete'),
        ('recruiter', 'Recruiter'),
    ]
    user_type = models.CharField(max_length=10, choices=USER_TYPES, default='athlete')

    def __str__(self):
        return self.username
