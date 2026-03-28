from django.db import migrations

ALERTS = [
    {"symbol": "AAPL",  "message": "AAPL crossed above $185.00",              "is_read": False},
    {"symbol": "NVDA",  "message": "New bullish signal detected for NVDA",     "is_read": False},
    {"symbol": "TSLA",  "message": "Unusual volume spike in TSLA",             "is_read": True},
    {"symbol": "MSFT",  "message": "MSFT earnings report in 3 days",           "is_read": True},
]


def seed_alerts(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    Stock = apps.get_model("market_data", "Stock")
    Alert = apps.get_model("alerts", "Alert")

    try:
        user = User.objects.get(username="demo")
    except User.DoesNotExist:
        return  # demo user not seeded, skip

    for a in ALERTS:
        stock = Stock.objects.get(symbol=a["symbol"])
        Alert.objects.get_or_create(
            user=user,
            stock=stock,
            message=a["message"],
            defaults={"is_read": a["is_read"]},
        )


def reverse_alerts(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    Alert = apps.get_model("alerts", "Alert")
    try:
        user = User.objects.get(username="demo")
        Alert.objects.filter(user=user).delete()
    except User.DoesNotExist:
        pass


class Migration(migrations.Migration):

    dependencies = [
        ("accounts", "0002_seed_demo_user"),
        ("market_data", "0002_seed_stocks_and_filings"),
        ("alerts", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_alerts, reverse_alerts),
    ]
