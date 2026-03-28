from django.db import models


class Stock(models.Model):
    symbol = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=255)
    sector = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.symbol


class StockPrice(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    date = models.DateTimeField()

    open_price = models.FloatField()
    high_price = models.FloatField()
    low_price = models.FloatField()
    close_price = models.FloatField()
    volume = models.BigIntegerField()

    class Meta:
        unique_together = ("stock", "date")


class Filing(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    filing_type = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)


class InsiderTrade(models.Model):
    stock = models.ForeignKey(Stock, on_delete=models.CASCADE)
    insider_name = models.CharField(max_length=255)
    trade_type = models.CharField(max_length=10)  # BUY / SELL
    quantity = models.IntegerField()
    price = models.FloatField()
    date = models.DateTimeField()