from django.db import migrations

PATTERNS = [
    {
        "symbol": "AAPL",
        "name": "Bullish Engulfing",
        "success_rate": 87.0,
    },
    {
        "symbol": "AAPL",
        "name": "Cup and Handle",
        "success_rate": 74.0,
    },
]

BACKTESTS = [
    {
        "symbol": "AAPL",
        "strategy": "Mock Strategy v1",
        "win_rate": 68.0,
        "avg_return": 3.2,
    },
]


def seed_analytics(apps, schema_editor):
    Pattern = apps.get_model("analytics", "Pattern")
    BacktestResult = apps.get_model("analytics", "BacktestResult")
    Stock = apps.get_model("market_data", "Stock")

    for p in PATTERNS:
        stock = Stock.objects.get(symbol=p["symbol"])
        Pattern.objects.get_or_create(
            stock=stock,
            pattern_name=p["name"],
            defaults={"success_rate": p["success_rate"]},
        )

    for b in BACKTESTS:
        stock = Stock.objects.get(symbol=b["symbol"])
        BacktestResult.objects.get_or_create(
            stock=stock,
            strategy_name=b["strategy"],
            defaults={"win_rate": b["win_rate"], "avg_return": b["avg_return"]},
        )


def reverse_analytics(apps, schema_editor):
    Pattern = apps.get_model("analytics", "Pattern")
    BacktestResult = apps.get_model("analytics", "BacktestResult")
    Pattern.objects.filter(stock__symbol="AAPL").delete()
    BacktestResult.objects.filter(stock__symbol="AAPL").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("market_data", "0002_seed_stocks_and_filings"),
        ("analytics", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_analytics, reverse_analytics),
    ]
