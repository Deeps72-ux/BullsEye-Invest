from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    RISK_CHOICES = [
        ("low", "Low"),
        ("moderate", "Moderate"),
        ("high", "High"),
    ]

    risk_profile = models.CharField(max_length=10, choices=RISK_CHOICES, default="moderate")
    preferred_sectors = models.JSONField(default=list, blank=True)

    def __str__(self):
        return self.username