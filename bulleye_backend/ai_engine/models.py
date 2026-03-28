from django.db import models
from accounts.models import User


class ChatQuery(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    query = models.TextField()
    response = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)