import os
from django.utils import timezone
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

def personal_photo_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{instance.username}_personal_{timezone.now().strftime('%Y-%m-%d-%H-%M-%S)')}.{ext}"
    return os.path.join('media', 'personal', filename)

def licence_photo_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{instance.username}_licence_{timezone.now().strftime('%Y-%m-%d-%H-%M-%S)')}.{ext}"
    return os.path.join('media', 'licence', filename)

def national_id_photo_upload_path(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{instance.username}_national_id_{timezone.now().strftime('%Y-%m-%d-%H-%M-%S)')}.{ext}"
    return os.path.join('media', 'national_id', filename)

class XrideUser(AbstractUser):
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    phone_number = models.CharField(max_length=15, unique=True, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    national_id = models.CharField(max_length=14, unique=True, blank=True, null=True)  # National ID field

    personal_photo = models.ImageField(upload_to=personal_photo_upload_path, blank=True, null=True)
    licence_photo = models.ImageField(upload_to=licence_photo_upload_path, blank=True, null=True)
    national_id_photo = models.ImageField(upload_to=national_id_photo_upload_path, blank=True, null=True)

    groups = models.ManyToManyField(
        Group,
        related_name='xrideuser_set',  # Custom related name
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.'
    )
    user_permissions = models.ManyToManyField(
        Permission,
        related_name='xrideuser_set',  # Custom related name
        blank=True,
        help_text='Specific permissions for this user.'
    )

    def save(self, *args, **kwargs):
        if self.username:
            self.username = self.username.lower()  # Convert to lowercase
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Name: {self.username} Balance: {self.wallet_balance}"
