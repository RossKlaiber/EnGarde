# profiles/models.py
from django.db import models
from django.conf import settings
from django.db import models
from django.conf import settings

class AthleteProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    FIE_page = models.URLField(blank=True, null=True)
    FIE_id = models.CharField(max_length=100, blank=True, null=True)
    name = models.CharField(max_length=200, default='Unknown Athlete')
    flag = models.CharField(max_length=10, blank=True, null=True)
    handedness = models.CharField(max_length=50, blank=True, null=True)
    age = models.PositiveIntegerField(blank=True, null=True)
    image = models.ImageField(upload_to='profile_images/', blank=True, null=True)
    weapon = models.CharField(max_length=50, blank=True, null=True)
    rank = models.CharField(max_length=50, blank=True, null=True)
    residence = models.CharField(max_length=200, blank=True, null=True)
    points = models.IntegerField(default=0)
    bio = models.TextField(blank=True, null=True)

    # New fields to store competition data
    competitions_data = models.JSONField(blank=True, null=True)
    yearly_summary_data = models.JSONField(blank=True, null=True)


    def __str__(self):
        return f"{self.user.username}'s Athlete Profile" 
 
class RecruiterProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    school_affiliation = models.CharField(max_length=255)
    # Recruiters can add athletes to their list:
    athletes = models.ManyToManyField(AthleteProfile, blank=True, related_name='recruiters')

    def __str__(self):
        return f"{self.user.username}'s Recruiter Profile"
