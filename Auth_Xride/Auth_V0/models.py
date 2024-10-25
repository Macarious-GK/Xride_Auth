from django.contrib.auth.models import AbstractUser, Group, Permission
from django.db import models

class XrideUser(AbstractUser):
    wallet_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    phone_number = models.CharField(max_length=15, unique=True, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    national_id = models.CharField(max_length=14, unique=True, blank=True, null=True)  # National ID field

    # Override related names to avoid clashes
    groups = models.ManyToManyField(
        Group,
        related_name='xrideuser_set',  # Custom related name
        blank=True,
        help_text='The groups this user belongs to. A user will get all permissions '
                  'granted to each of their groups.'
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
