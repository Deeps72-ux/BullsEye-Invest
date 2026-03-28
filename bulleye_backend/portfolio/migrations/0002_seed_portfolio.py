from django.db import migrations

HOLDINGS = [
    {"symbol": "AAPL",  "quantity": 50,  "avg_price": 165.20},
    {"symbol": "MSFT",  "quantity": 25,  "avg_price": 340.00},
    {"symbol": "NVDA",  "quantity": 15,  "avg_price": 420.50},
    {"symbol": "GOOGL", "quantity": 40,  "avg_price": 130.00},
    {"symbol": "AMZN",  "quantity": 30,  "avg_price": 155.00},
]


def seed_portfolio(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    Stock = apps.get_model("market_data", "Stock")
    Portfolio = apps.get_model("portfolio", "Portfolio")
    Holding = apps.get_model("portfolio", "Holding")

    try:
        user = User.objects.get(username="demo")
    except User.DoesNotExist:
        return  # Demo user not seeded, skip

    portfolio, _ = Portfolio.objects.get_or_create(user=user)

    for h in HOLDINGS:
        stock = Stock.objects.get(symbol=h["symbol"])
        Holding.objects.get_or_create(
            portfolio=portfolio,
            stock=stock,
            defaults={"quantity": h["quantity"], "avg_price": h["avg_price"]},
        )


def reverse_portfolio(apps, schema_editor):
    User = apps.get_model("accounts", "User")
    Portfolio = apps.get_model("portfolio", "Portfolio")
    try:
        user = User.objects.get(username="demo")
        Portfolio.objects.filter(user=user).delete()
    except User.DoesNotExist:
        pass


class Migration(migrations.Migration):

    dependencies = [
        # Demo user must exist first
        ("accounts", "0002_seed_demo_user"),
        # Stocks must exist first
        ("market_data", "0002_seed_stocks_and_filings"),
        ("portfolio", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_portfolio, reverse_portfolio),
    ]
