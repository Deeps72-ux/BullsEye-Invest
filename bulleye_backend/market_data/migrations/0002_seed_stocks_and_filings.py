import math
import random
from django.db import migrations


STOCKS = [
    {"symbol": "AAPL",  "name": "Apple Inc.",        "sector": "Technology"},
    {"symbol": "GOOGL", "name": "Alphabet Inc.",      "sector": "Technology"},
    {"symbol": "MSFT",  "name": "Microsoft Corp.",    "sector": "Technology"},
    {"symbol": "AMZN",  "name": "Amazon.com Inc.",    "sector": "Consumer Discretionary"},
    {"symbol": "TSLA",  "name": "Tesla Inc.",         "sector": "Consumer Discretionary"},
    {"symbol": "NVDA",  "name": "NVIDIA Corp.",       "sector": "Technology"},
    {"symbol": "META",  "name": "Meta Platforms",     "sector": "Technology"},
    {"symbol": "JPM",   "name": "JPMorgan Chase",     "sector": "Financials"},
]

FILINGS = [
    {"symbol": "AAPL",  "type": "10-K",  "date": "2024-11-03", "description": "Annual report filing"},
    {"symbol": "NVDA",  "type": "8-K",   "date": "2024-10-28", "description": "Current report - material event"},
    {"symbol": "MSFT",  "type": "10-Q",  "date": "2024-10-24", "description": "Quarterly report filing"},
    {"symbol": "TSLA",  "type": "8-K",   "date": "2024-10-18", "description": "Earnings announcement"},
]


def seed_stocks_and_filings(apps, schema_editor):
    Stock = apps.get_model("market_data", "Stock")
    StockPrice = apps.get_model("market_data", "StockPrice")
    Filing = apps.get_model("market_data", "Filing")

    from datetime import datetime, timezone

    # Seed stocks (skip if already exist)
    for s in STOCKS:
        Stock.objects.get_or_create(symbol=s["symbol"], defaults={"name": s["name"], "sector": s["sector"]})

    # Seed 30-day chart data for AAPL (matching mockChartData)
    aapl = Stock.objects.get(symbol="AAPL")
    random.seed(42)  # deterministic
    for i in range(30):
        dt = datetime(2024, 1, i + 1, tzinfo=timezone.utc)
        price = 170 + math.sin(i / 3) * 15 + random.random() * 8
        volume_m = int((30 + random.random() * 40) * 1_000_000)
        StockPrice.objects.get_or_create(
            stock=aapl,
            date=dt,
            defaults={
                "open_price": round(price - 0.5, 2),
                "high_price": round(price + 1.2, 2),
                "low_price": round(price - 1.5, 2),
                "close_price": round(price, 2),
                "volume": volume_m,
            },
        )

    # Seed filings
    for f in FILINGS:
        stock = Stock.objects.get(symbol=f["symbol"])
        Filing.objects.get_or_create(
            stock=stock,
            filing_type=f["type"],
            title=f"{f['type']} - {stock.name}",
            defaults={"description": f["description"]},
        )


def reverse_seed(apps, schema_editor):
    Stock = apps.get_model("market_data", "Stock")
    Filing = apps.get_model("market_data", "Filing")
    StockPrice = apps.get_model("market_data", "StockPrice")
    symbols = [s["symbol"] for s in STOCKS]
    StockPrice.objects.filter(stock__symbol__in=symbols).delete()
    Filing.objects.filter(stock__symbol__in=symbols).delete()
    Stock.objects.filter(symbol__in=symbols).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("market_data", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_stocks_and_filings, reverse_seed),
    ]
