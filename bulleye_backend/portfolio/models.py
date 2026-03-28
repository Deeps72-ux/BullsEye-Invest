from django.db import models
from accounts.models import User
from market_data.models import Stock


class Portfolio(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class Holding(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name="holdings")
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)

    quantity = models.IntegerField()
    avg_price = models.FloatField()

    def __str__(self):
        return f"{self.stock.symbol} ({self.quantity})"