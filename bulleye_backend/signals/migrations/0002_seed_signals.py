from django.db import migrations

SIGNALS = [
    {
        "symbol": "NVDA",
        "type": "bullish",
        "confidence": 92,
        "reason": "Strong breakout above resistance with high volume. RSI momentum confirms uptrend.",
    },
    {
        "symbol": "AAPL",
        "type": "bullish",
        "confidence": 85,
        "reason": "Golden cross formation on daily chart. Institutional buying detected.",
    },
    {
        "symbol": "TSLA",
        "type": "bearish",
        "confidence": 78,
        "reason": "Head and shoulders pattern forming. Volume declining on rallies.",
    },
    {
        "symbol": "AMZN",
        "type": "bullish",
        "confidence": 88,
        "reason": "Earnings beat expectations. Cloud revenue growing 30% YoY.",
    },
    {
        "symbol": "MSFT",
        "type": "bullish",
        "confidence": 90,
        "reason": "AI integration driving revenue. Strong support at current levels.",
    },
]


def seed_signals(apps, schema_editor):
    Signal = apps.get_model("signals", "Signal")
    Stock = apps.get_model("market_data", "Stock")

    for sig in SIGNALS:
        stock = Stock.objects.get(symbol=sig["symbol"])
        Signal.objects.get_or_create(
            stock=stock,
            signal_type=sig["type"],
            confidence=sig["confidence"],
            defaults={"reason": sig["reason"]},
        )


def reverse_signals(apps, schema_editor):
    Signal = apps.get_model("signals", "Signal")
    symbols = [s["symbol"] for s in SIGNALS]
    Signal.objects.filter(stock__symbol__in=symbols).delete()


class Migration(migrations.Migration):

    dependencies = [
        # Stocks must exist first
        ("market_data", "0002_seed_stocks_and_filings"),
        ("signals", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_signals, reverse_signals),
    ]
