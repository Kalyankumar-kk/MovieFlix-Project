from django.db import models


class AdminRegister(models.Model):
    admin_first_name = models.CharField(max_length=100)
    admin_last_name = models.CharField(max_length=100)
    admin_email = models.EmailField(unique=True)
    admin_mobileno = models.CharField(max_length=15)
    admin_password = models.CharField(max_length=128) # Use hashing in production
    admin_profile_pic = models.ImageField(upload_to='admin_profiles/', null=True, blank=True)
    admin_username = models.CharField(max_length=100, null=True, blank=True)
    notifications_enabled = models.BooleanField(default=True)


