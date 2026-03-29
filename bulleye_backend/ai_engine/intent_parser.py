"""
Intent Parser — Extracts stock symbols and query intent from free-form text.

Handles queries like:
  "Should I buy TCS?"              → symbol=TCS, intent=buy_query
  "Is Infosys a good investment?"  → symbol=INFY, intent=buy_query
  "Show me my portfolio summary"   → symbol=None, intent=portfolio_review
  "What's happening in the market?"→ symbol=None, intent=market_overview
  "Explain Reliance for me"        → symbol=RELIANCE, intent=explain_stock
"""

import re
import logging

logger = logging.getLogger(__name__)

# ── Top 100 NSE symbols → company name aliases ───────────────────────────────
# Used for fuzzy name-to-symbol matching (e.g. "Infosys" → "INFY")
_NSE_ALIASES: dict[str, str] = {
    # IT
    "TCS": "TCS",
    "TATA CONSULTANCY": "TCS",
    "INFOSYS": "INFY",
    "INFY": "INFY",
    "WIPRO": "WIPRO",
    "HCL": "HCLTECH",
    "HCLTECH": "HCLTECH",
    "TECH MAHINDRA": "TECHM",
    "TECHM": "TECHM",
    "MPHASIS": "MPHASIS",
    "LTIMINDTREE": "LTIM",
    "LTIM": "LTIM",
    "PERSISTENT": "PERSISTENT",
    # Banking & Finance
    "HDFC BANK": "HDFCBANK",
    "HDFCBANK": "HDFCBANK",
    "ICICI BANK": "ICICIBANK",
    "ICICIBANK": "ICICIBANK",
    "SBI": "SBIN",
    "SBIN": "SBIN",
    "STATE BANK": "SBIN",
    "AXIS BANK": "AXISBANK",
    "AXISBANK": "AXISBANK",
    "KOTAK": "KOTAKBANK",
    "KOTAKBANK": "KOTAKBANK",
    "BAJAJ FINANCE": "BAJFINANCE",
    "BAJFINANCE": "BAJFINANCE",
    "BAJAJ FINSERV": "BAJAJFINSV",
    "BAJAJFINSV": "BAJAJFINSV",
    # Energy & Oil
    "RELIANCE": "RELIANCE",
    "RIL": "RELIANCE",
    "ONGC": "ONGC",
    "OIL AND NATURAL GAS": "ONGC",
    "BPCL": "BPCL",
    "IOC": "IOC",
    "INDIAN OIL": "IOC",
    "NTPC": "NTPC",
    "POWER GRID": "POWERGRID",
    "POWERGRID": "POWERGRID",
    # FMCG
    "HINDUSTAN UNILEVER": "HINDUNILVR",
    "HUL": "HINDUNILVR",
    "HINDUNILVR": "HINDUNILVR",
    "ITC": "ITC",
    "NESTLE": "NESTLE",
    "DABUR": "DABUR",
    "MARICO": "MARICO",
    "BRITANNIA": "BRITANNIA",
    # Auto
    "MARUTI": "MARUTI",
    "MARUTI SUZUKI": "MARUTI",
    "TATA MOTORS": "TATAMOTORS",
    "TATAMOTORS": "TATAMOTORS",
    "M&M": "M&M",
    "MAHINDRA": "M&M",
    "BAJAJ AUTO": "BAJAJ-AUTO",
    "HERO MOTOCORP": "HEROMOTOCO",
    "HEROMOTOCO": "HEROMOTOCO",
    "EICHER": "EICHERMOT",
    "EICHERMOT": "EICHERMOT",
    # Pharma
    "SUN PHARMA": "SUNPHARMA",
    "SUNPHARMA": "SUNPHARMA",
    "DR REDDY": "DRREDDY",
    "DRREDDY": "DRREDDY",
    "CIPLA": "CIPLA",
    "DIVI": "DIVISLAB",
    "DIVISLAB": "DIVISLAB",
    "BIOCON": "BIOCON",
    # Metals
    "TATA STEEL": "TATASTEEL",
    "TATASTEEL": "TATASTEEL",
    "JSW STEEL": "JSWSTEEL",
    "JSWSTEEL": "JSWSTEEL",
    "HINDALCO": "HINDALCO",
    "VEDANTA": "VEDL",
    "VEDL": "VEDL",
    # Infra & Conglomerate
    "LARSEN": "LT",
    "L&T": "LT",
    "LT": "LT",
    "ADANI ENTERPRISES": "ADANIENT",
    "ADANIENT": "ADANIENT",
    "ADANI PORTS": "ADANIPORTS",
    "ADANIPORTS": "ADANIPORTS",
    "ULTRATECH": "ULTRACEMCO",
    "ULTRACEMCO": "ULTRACEMCO",
    "GRASIM": "GRASIM",
    "TITAN": "TITAN",
    "ASIAN PAINTS": "ASIANPAINT",
    "ASIANPAINT": "ASIANPAINT",
    # Telecom
    "AIRTEL": "BHARTIARTL",
    "BHARTI AIRTEL": "BHARTIARTL",
    "BHARTIARTL": "BHARTIARTL",
    "JIOFINANCIAL": "JIOFIN",
    # Exchange / AMC
    "BSE": "BSE",
    "NSE": "NSEI",
    "MCAP": "MCAP",
    "MAPMYINDIA": "MAPMYINDIA",
    # Others frequently mentioned
    "ZOMATO": "ZOMATO",
    "PAYTM": "PAYTM",
    "NYKAA": "NYKAA",
    "POLICYBAZAAR": "POLICYBZR",
    "DMART": "DMART",
    "MEDIASSIST": "MEDIASSIST",
    "IRCTC": "IRCTC",
    "HAL": "HAL",
    "BEL": "BEL",
    "BHEL": "BHEL",
    "COAL INDIA": "COALINDIA",
    "COALINDIA": "COALINDIA",
    "MOTHERSON": "MOTHERSON",
    "DIXON": "DIXON",
    "CAMS": "CAMS",
}

# ── Intent patterns ───────────────────────────────────────────────────────────
_BUY_INTENT_PATTERNS = [
    r"\b(should i buy|is it a good time to buy|buy)\b",
    r"\b(worth buying|good investment|invest in|add to portfolio)\b",
    r"\b(entry point|can i entry|should i enter)\b",
]
_SELL_INTENT_PATTERNS = [
    r"\b(should i sell|when to sell|exit|book profit|take profit)\b",
    r"\b(trim|reduce position|exit position)\b",
]
_PORTFOLIO_INTENT_PATTERNS = [
    r"\b(my portfolio|portfolio review|portfolio analysis|holdings|my holdings)\b",
    r"\b(how is my investment|portfolio health|asset allocation)\b",
]
_MARKET_OVERVIEW_PATTERNS = [
    r"\b(market overview|stock market|nifty|sensex|market today|indices)\b",
    r"\b(what.s happening|market update|market summary)\b",
]
_EXPLAIN_PATTERNS = [
    r"\b(explain|tell me about|what is|who is|overview of|analyse|analyze)\b",
]


class IntentParser:
    """Parses free-form user queries into structured intent + symbol."""

    def parse(self, query: str) -> dict:
        """
        Returns:
            {
                "symbol": str | None,
                "intent": str,
                "intent_display": str,
                "cleaned_query": str,
            }
        """
        q = query.strip()
        cleaned = q

        symbol = self._extract_symbol(q)
        intent = self._classify_intent(q)

        intent_display_map = {
            "buy_query": "Buy/Invest Query",
            "sell_query": "Sell/Exit Query",
            "portfolio_review": "Portfolio Review",
            "market_overview": "Market Overview",
            "explain_stock": "Stock Explanation",
            "general": "General Query",
        }

        logger.debug(f"[IntentParser] query={q!r} → symbol={symbol}, intent={intent}")

        return {
            "symbol": symbol,
            "intent": intent,
            "intent_display": intent_display_map.get(intent, "General Query"),
            "cleaned_query": cleaned,
        }

    def _extract_symbol(self, query: str) -> str | None:
        """
        Priority:
          1. Exact NSE ticker in UPPERCASE (e.g. TCS, INFY)
          2. Company name aliases (e.g. "Infosys" → INFY)
          3. Database lookup (if alias not matched)
        """
        upper_q = query.upper()

        # 1. Check alias map (longest match first to avoid partial matches)
        best_match = None
        best_len = 0
        for alias, ticker in _NSE_ALIASES.items():
            if alias in upper_q and len(alias) > best_len:
                best_match = ticker
                best_len = len(alias)
        if best_match:
            return best_match

        # 2. Regex: look for 2-10 uppercase letter sequences that could be a ticker
        candidates = re.findall(r'\b([A-Z]{2,10})\b', upper_q)
        skip_words = {
            "IN", "IT", "IS", "TO", "BUY", "THE", "FOR", "AND",
            "NSE", "BSE", "SEBI", "IPO", "PE", "FII", "DII",
            "CMP", "LTP", "ATH", "EPS", "ME", "MY", "AI",
        }
        for c in candidates:
            if c not in skip_words:
                # Try DB lookup
                symbol = self._db_lookup(c)
                if symbol:
                    return symbol

        return None

    def _db_lookup(self, symbol: str) -> str | None:
        """Check if symbol exists in the Stock table."""
        try:
            from market_data.models import Stock
            if Stock.objects.filter(symbol=symbol).exists():
                return symbol
        except Exception:
            pass
        return None

    def _classify_intent(self, query: str) -> str:
        q_lower = query.lower()

        for pattern in _BUY_INTENT_PATTERNS:
            if re.search(pattern, q_lower):
                return "buy_query"

        for pattern in _SELL_INTENT_PATTERNS:
            if re.search(pattern, q_lower):
                return "sell_query"

        for pattern in _PORTFOLIO_INTENT_PATTERNS:
            if re.search(pattern, q_lower):
                return "portfolio_review"

        for pattern in _MARKET_OVERVIEW_PATTERNS:
            if re.search(pattern, q_lower):
                return "market_overview"

        for pattern in _EXPLAIN_PATTERNS:
            if re.search(pattern, q_lower):
                return "explain_stock"

        return "general"
