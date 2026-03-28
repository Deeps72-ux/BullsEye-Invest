from django.db import models
from accounts.models import User
from market_data.models import Stock


class AlertSubscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)

    alert_type = models.CharField(max_length=50)  # breakout, volume spike, etc.
    created_at = models.DateTimeField(auto_now_add=True)


class Alert(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)

    message = models.TextField()
    is_read = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)