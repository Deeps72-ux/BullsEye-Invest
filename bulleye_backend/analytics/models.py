from django.db import models
from market_data.models import Stock


class Indicator(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    date = models.DateTimeField()

    rsi = models.FloatField(null=True, blank=True)
    macd = models.FloatField(null=True, blank=True)
    ema = models.FloatField(null=True, blank=True)

    class Meta:
        unique_together = ("stock", "date")


class Pattern(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    pattern_name = models.CharField(max_length=100)
    success_rate = models.FloatField()  # %

    detected_at = models.DateTimeField(auto_now_add=True)


class BacktestResult(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    strategy_name = models.CharField(max_length=100)

    win_rate = models.FloatField()
    avg_return = models.FloatField()

    created_at = models.DateTimeField(auto_now_add=True)