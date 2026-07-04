from django.contrib.auth.models import AbstractUser
from django.db import models


class UserRole(models.TextChoices):
    CLIENT = "CLIENT", "Client"
    MANAGEMENT = "MANAGEMENT", "Management"
    MP = "MP", "Member of Parliament"
    ADMIN = "ADMIN", "Admin"


class User(AbstractUser):
    firebase_uid = models.CharField(
        max_length=128,
        unique=True,
        null=True,
        blank=True
    )

    role = models.CharField(
        max_length=20,
        choices=UserRole.choices,
        default=UserRole.CLIENT
    )

    phone_number = models.CharField(max_length=15,blank=True)
    preferred_language = models.CharField(max_length=10,default="en")
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.username} ({self.role})"