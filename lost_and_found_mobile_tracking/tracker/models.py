# tracker/models.py
from django.db import models
from django.contrib.auth.models import User

class MobileReport(models.Model):
    STATUS_CHOICES = [
        ('lost', 'Lost'),
        ('found', 'Found'),
        ('returned', 'Returned'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    brand = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    imei = models.CharField(max_length=15, unique=True)
    color = models.CharField(max_length=30)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='lost')
    location = models.CharField(max_length=100)
    date_reported = models.DateField(auto_now_add=True)
    contact_info = models.TextField()
    photo = models.ImageField(upload_to='mobile_photos/', null=True, blank=True)

    def __str__(self):
        return f"{self.brand} {self.model} - {self.status}"
# models.py
from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.CharField(max_length=255, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"
