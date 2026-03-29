"""
seed_stocks — Populate the Stock table with 50+ Indian & global companies.

Usage:
    python manage.py seed_stocks
    python manage.py seed_stocks --clear   # wipe existing stocks first
"""

from django.core.management.base import BaseCommand
from market_data.models import Stock


STOCKS = [
    # ─── Indian NSE / BSE blue-chips ──────────────────────────────────────
    ("RELIANCE.NS", "Reliance Industries", "Energy"),
    ("TCS.NS", "Tata Consultancy Services", "IT"),
    ("HDFCBANK.NS", "HDFC Bank", "Banking"),
    ("INFY.NS", "Infosys", "IT"),
    ("ICICIBANK.NS", "ICICI Bank", "Banking"),
    ("HINDUNILVR.NS", "Hindustan Unilever", "FMCG"),
    ("SBIN.NS", "State Bank of India", "Banking"),
    ("BHARTIARTL.NS", "Bharti Airtel", "Telecom"),
    ("ITC.NS", "ITC Limited", "FMCG"),
    ("KOTAKBANK.NS", "Kotak Mahindra Bank", "Banking"),
    ("LT.NS", "Larsen & Toubro", "Infrastructure"),
    ("AXISBANK.NS", "Axis Bank", "Banking"),
    ("BAJFINANCE.NS", "Bajaj Finance", "Finance"),
    ("ASIANPAINT.NS", "Asian Paints", "Paints"),
    ("MARUTI.NS", "Maruti Suzuki", "Automobile"),
    ("SUNPHARMA.NS", "Sun Pharmaceutical", "Pharma"),
    ("TITAN.NS", "Titan Company", "Consumer Goods"),
    ("ULTRACEMCO.NS", "UltraTech Cement", "Cement"),
    ("NESTLEIND.NS", "Nestle India", "FMCG"),
    ("WIPRO.NS", "Wipro", "IT"),
    ("HCLTECH.NS", "HCL Technologies", "IT"),
    ("POWERGRID.NS", "Power Grid Corp", "Utilities"),
    ("NTPC.NS", "NTPC Limited", "Utilities"),
    ("TATAMOTORS.NS", "Tata Motors", "Automobile"),
    ("TATASTEEL.NS", "Tata Steel", "Metals"),
    ("ONGC.NS", "ONGC", "Energy"),
    ("ADANIENT.NS", "Adani Enterprises", "Conglomerate"),
    ("ADANIPORTS.NS", "Adani Ports", "Infrastructure"),
    ("TECHM.NS", "Tech Mahindra", "IT"),
    ("JSWSTEEL.NS", "JSW Steel", "Metals"),
    ("DRREDDY.NS", "Dr Reddy's Labs", "Pharma"),
    ("CIPLA.NS", "Cipla", "Pharma"),
    ("BPCL.NS", "Bharat Petroleum", "Energy"),
    ("COALINDIA.NS", "Coal India", "Mining"),
    ("EICHERMOT.NS", "Eicher Motors", "Automobile"),
    ("DIVISLAB.NS", "Divi's Laboratories", "Pharma"),
    ("BAJAJFINSV.NS", "Bajaj Finserv", "Finance"),
    ("APOLLOHOSP.NS", "Apollo Hospitals", "Healthcare"),
    ("BRITANNIA.NS", "Britannia Industries", "FMCG"),
    ("INDUSINDBK.NS", "IndusInd Bank", "Banking"),

    # ─── Global stocks ────────────────────────────────────────────────────
    ("AAPL", "Apple Inc.", "Technology"),
    ("GOOGL", "Alphabet Inc.", "Technology"),
    ("MSFT", "Microsoft Corp.", "Technology"),
    ("AMZN", "Amazon.com Inc.", "E-Commerce"),
    ("TSLA", "Tesla Inc.", "Automobile"),
    ("NVDA", "NVIDIA Corp.", "Semiconductors"),
    ("META", "Meta Platforms", "Technology"),
    ("JPM", "JPMorgan Chase", "Banking"),
    ("V", "Visa Inc.", "Financial Services"),
    ("JNJ", "Johnson & Johnson", "Healthcare"),
    ("WMT", "Walmart Inc.", "Retail"),
    ("NFLX", "Netflix Inc.", "Entertainment"),
    ("DIS", "Walt Disney Co.", "Entertainment"),
    ("AMD", "AMD Inc.", "Semiconductors"),
    ("INTC", "Intel Corp.", "Semiconductors"),
]


class Command(BaseCommand):
    help = "Seed the database with 50+ Indian & global stocks"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete all existing stocks before seeding",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            deleted, _ = Stock.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"Deleted {deleted} existing stock records."))

        created = 0
        skipped = 0
        for symbol, name, sector in STOCKS:
            _, was_created = Stock.objects.update_or_create(
                symbol=symbol,
                defaults={"name": name, "sector": sector},
            )
            if was_created:
                created += 1
            else:
                skipped += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Done! Created {created} stocks, updated {skipped} existing."
            )
        )
