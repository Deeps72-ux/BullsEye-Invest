from django.db import models
from market_data.models import Stock


class Signal(models.Model):
    SIGNAL_TYPES = [
        ("bullish", "Bullish"),
        ("bearish", "Bearish"),
        ("neutral", "Neutral"),
    ]

    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    signal_type = models.CharField(max_length=10, choices=SIGNAL_TYPES)
    confidence = models.IntegerField()  # 0-100
    reason = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.stock.symbol} - {self.signal_type}"