"""
sync_stock_prices — Fetch live OHLCV data for all stocks in the database.

Usage:
    python manage.py sync_stock_prices              # live data, last 30 days
    python manage.py sync_stock_prices --days 7      # last 7 days
    python manage.py sync_stock_prices --symbol AAPL # single stock
    python manage.py sync_stock_prices --mock        # generate realistic sample data
"""

import logging
import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from market_data.models import Stock, StockPrice

logger = logging.getLogger(__name__)

# Realistic base prices for mock data generation
MOCK_BASE_PRICES = {
    # Indian stocks (INR)
    "RELIANCE.NS": 2950, "TCS.NS": 3800, "HDFCBANK.NS": 1650,
    "INFY.NS": 1550, "ICICIBANK.NS": 1200, "HINDUNILVR.NS": 2400,
    "SBIN.NS": 820, "BHARTIARTL.NS": 1650, "ITC.NS": 450,
    "KOTAKBANK.NS": 1780, "LT.NS": 3500, "AXISBANK.NS": 1150,
    "BAJFINANCE.NS": 6800, "ASIANPAINT.NS": 2900, "MARUTI.NS": 12500,
    "SUNPHARMA.NS": 1800, "TITAN.NS": 3500, "ULTRACEMCO.NS": 11200,
    "NESTLEIND.NS": 2500, "WIPRO.NS": 480, "HCLTECH.NS": 1700,
    "POWERGRID.NS": 330, "NTPC.NS": 380, "TATAMOTORS.NS": 780,
    "TATASTEEL.NS": 165, "ONGC.NS": 280, "ADANIENT.NS": 3100,
    "ADANIPORTS.NS": 1400, "TECHM.NS": 1650, "JSWSTEEL.NS": 920,
    "DRREDDY.NS": 6400, "CIPLA.NS": 1500, "BPCL.NS": 630,
    "COALINDIA.NS": 480, "EICHERMOT.NS": 4800, "DIVISLAB.NS": 5900,
    "BAJAJFINSV.NS": 1800, "APOLLOHOSP.NS": 6900, "BRITANNIA.NS": 5400,
    "INDUSINDBK.NS": 1050,
    # Global stocks (USD)
    "AAPL": 189, "GOOGL": 175, "MSFT": 425, "AMZN": 185,
    "TSLA": 175, "NVDA": 880, "META": 500, "JPM": 195,
    "V": 280, "JNJ": 155, "WMT": 170, "NFLX": 620,
    "DIS": 115, "AMD": 165, "INTC": 42,
}


def _generate_mock_prices(stock, days):
    """Generate realistic OHLCV data with random walk."""
    base = MOCK_BASE_PRICES.get(stock.symbol, 100)
    now = timezone.now()
    records = []
    price = base

    for d in range(days, 0, -1):
        date = now - timedelta(days=d)

        # Skip weekends
        if date.weekday() >= 5:
            continue

        # Random daily change ±3%
        change_pct = random.uniform(-0.03, 0.03)
        price = round(price * (1 + change_pct), 2)

        day_high = round(price * random.uniform(1.005, 1.025), 2)
        day_low = round(price * random.uniform(0.975, 0.995), 2)
        open_price = round(random.uniform(day_low, day_high), 2)
        volume = random.randint(500_000, 50_000_000)

        records.append(StockPrice(
            stock=stock,
            date=date,
            open_price=open_price,
            high_price=day_high,
            low_price=day_low,
            close_price=price,
            volume=volume,
        ))

    return records


class Command(BaseCommand):
    help = "Fetch latest OHLCV prices from Yahoo Finance (or generate mock data) for all stocks"

    def add_arguments(self, parser):
        parser.add_argument(
            "--days", type=int, default=30,
            help="Number of days of history to fetch (default: 30)",
        )
        parser.add_argument(
            "--symbol", type=str, default="",
            help="Sync only this symbol (default: all)",
        )
        parser.add_argument(
            "--mock", action="store_true",
            help="Generate realistic sample data instead of fetching from Yahoo Finance",
        )

    def handle(self, *args, **options):
        days = options["days"]
        symbol_filter = options["symbol"].upper().strip()
        use_mock = options["mock"]

        stocks = Stock.objects.all()
        if symbol_filter:
            stocks = stocks.filter(symbol=symbol_filter)

        if not stocks.exists():
            self.stdout.write(self.style.WARNING("No stocks found. Run seed_stocks first."))
            return

        if use_mock:
            self._handle_mock(stocks, days)
        else:
            self._handle_live(stocks, days)

    def _handle_mock(self, stocks, days):
        """Generate realistic sample OHLCV data."""
        self.stdout.write(self.style.HTTP_INFO(f"Generating mock prices for {stocks.count()} stocks ({days} days)..."))

        total = 0
        for stock in stocks:
            records = _generate_mock_prices(stock, days)

            # Bulk upsert: delete old entries in the date range and recreate
            if records:
                StockPrice.objects.filter(
                    stock=stock,
                    date__gte=records[0].date,
                ).delete()
                StockPrice.objects.bulk_create(records, ignore_conflicts=True)
                total += len(records)
                self.stdout.write(f"  ✓ {stock.symbol}: {len(records)} days")

        self.stdout.write(self.style.SUCCESS(f"\nDone! Created {total} price records (mock data)."))

    def _handle_live(self, stocks, days):
        """Fetch real data from Yahoo Finance using batch download."""
        try:
            import yfinance as yf
        except ImportError:
            self.stderr.write(self.style.ERROR(
                "yfinance is not installed. Run: pip install yfinance\n"
                "Or use --mock to generate sample data."
            ))
            return

        end_date = timezone.now()
        start_date = end_date - timedelta(days=days)

        symbols = [s.symbol for s in stocks]
        symbol_map = {s.symbol: s for s in stocks}

        self.stdout.write(f"Downloading prices for {len(symbols)} stocks via yf.download()...")

        try:
            df = yf.download(
                tickers=symbols,
                start=start_date.strftime("%Y-%m-%d"),
                end=end_date.strftime("%Y-%m-%d"),
                group_by="ticker",
                threads=True,
                progress=True,
            )
        except Exception as exc:
            self.stderr.write(self.style.ERROR(
                f"yfinance batch download failed: {exc}\n"
                "Try: python manage.py sync_stock_prices --mock"
            ))
            return

        if df.empty:
            self.stderr.write(self.style.ERROR(
                "No data returned from Yahoo Finance.\n"
                "This may be a network issue inside Docker.\n"
                "Try: python manage.py sync_stock_prices --mock"
            ))
            return

        total_created = 0
        total_updated = 0
        errors = []

        for sym in symbols:
            stock = symbol_map[sym]
            try:
                if len(symbols) == 1:
                    stock_df = df
                else:
                    stock_df = df[sym].dropna(how="all")

                if stock_df.empty:
                    self.stdout.write(self.style.WARNING(f"  No data for {sym}"))
                    continue

                for date_idx, row in stock_df.iterrows():
                    if any(v != v for v in [row["Open"], row["Close"]]):  # NaN check
                        continue
                    _, created = StockPrice.objects.update_or_create(
                        stock=stock,
                        date=date_idx.to_pydatetime(),
                        defaults={
                            "open_price": round(float(row["Open"]), 2),
                            "high_price": round(float(row["High"]), 2),
                            "low_price": round(float(row["Low"]), 2),
                            "close_price": round(float(row["Close"]), 2),
                            "volume": int(row["Volume"]),
                        },
                    )
                    if created:
                        total_created += 1
                    else:
                        total_updated += 1

                self.stdout.write(self.style.SUCCESS(f"  ✓ {sym}"))
            except Exception as exc:
                msg = f"  ✗ {sym}: {exc}"
                self.stdout.write(self.style.ERROR(msg))
                errors.append(msg)

        self.stdout.write(self.style.SUCCESS(
            f"\nSync complete — {total_created} new, {total_updated} updated, {len(errors)} errors."
        ))
