from django.contrib import admin
from .models import Stock, StockPrice, Filing, InsiderTrade


@admin.register(Stock)
class StockAdmin(admin.ModelAdmin):
    list_display = ("symbol", "name", "sector")
    search_fields = ("symbol", "name")
    list_filter = ("sector",)


@admin.register(StockPrice)
class StockPriceAdmin(admin.ModelAdmin):
    list_display = ("stock", "date", "close_price", "volume")
    list_filter = ("stock",)
    ordering = ("-date",)


@admin.register(Filing)
class FilingAdmin(admin.ModelAdmin):
    list_display = ("stock", "title", "filing_type", "created_at")
    search_fields = ("title",)
    list_filter = ("filing_type",)


@admin.register(InsiderTrade)
class InsiderTradeAdmin(admin.ModelAdmin):
    list_display = ("stock", "insider_name", "trade_type", "quantity", "price", "date")
    list_filter = ("trade_type",)
