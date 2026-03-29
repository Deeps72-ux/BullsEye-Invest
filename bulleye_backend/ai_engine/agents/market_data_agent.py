"""
Market Data Agent — Fetches and summarizes real-time stock data.

Queries:
  - Stock (name, sector)
  - StockPrice (price trend, volume analysis)
  - Filing (recent corporate announcements)
  - InsiderTrade (insider buy/sell activity)

Output keys:
  price           : current close price (float)
  prev_price      : previous close price (float)
  price_change    : absolute change (float)
  price_change_pct: % change (float)
  trend           : "bullish" | "bearish" | "neutral"
  volume_signal   : "above_average" | "below_average" | "normal"
  volume_raw      : latest volume (int)
  sector          : sector name (str)
  insider_sentiment: "buying" | "selling" | "mixed" | "none"
  insider_summary : list of recent insider trades (list[dict])
  recent_filings  : list of recent filings (list[dict])
  data_points     : number of price records available (int)
  confidence_score: 0-100 (int)
"""

import logging
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class MarketDataAgent(BaseAgent):
    agent_name = "MarketDataAgent"

    def analyze(self, symbol: str, user=None) -> dict:
        # Django ORM imports inside method to avoid AppRegistryNotReady issues
        from market_data.models import Stock, StockPrice, Filing, InsiderTrade

        symbol = symbol.upper().strip()

        # ── Stock lookup ────────────────────────────────────────────────────
        try:
            stock = Stock.objects.get(symbol=symbol)
        except Stock.DoesNotExist:
            return self._not_found(symbol)

        # ── Price data ──────────────────────────────────────────────────────
        recent_prices = list(
            StockPrice.objects.filter(stock=stock).order_by("-date")[:30]
        )
        data_points = len(recent_prices)

        if recent_prices:
            latest = recent_prices[0]
            current_price = latest.close_price
            current_volume = latest.volume

            prev = recent_prices[1] if len(recent_prices) > 1 else latest
            prev_price = prev.close_price
            price_change = round(current_price - prev_price, 2)
            price_change_pct = round(
                (price_change / prev_price * 100) if prev_price else 0, 2
            )

            # Trend: based on 5-day vs 20-day average
            prices_5 = [p.close_price for p in recent_prices[:5]]
            prices_20 = [p.close_price for p in recent_prices[:20]]
            avg_5 = sum(prices_5) / len(prices_5)
            avg_20 = sum(prices_20) / len(prices_20) if prices_20 else avg_5

            if avg_5 > avg_20 * 1.01:
                trend = "bullish"
            elif avg_5 < avg_20 * 0.99:
                trend = "bearish"
            else:
                trend = "neutral"

            # Volume signal: compare latest vs 10-day avg
            volumes = [p.volume for p in recent_prices[:10]]
            avg_volume = sum(volumes) / len(volumes) if volumes else 1
            if current_volume > avg_volume * 1.3:
                volume_signal = "above_average"
            elif current_volume < avg_volume * 0.7:
                volume_signal = "below_average"
            else:
                volume_signal = "normal"
        else:
            current_price = 0.0
            prev_price = 0.0
            price_change = 0.0
            price_change_pct = 0.0
            trend = "neutral"
            volume_signal = "normal"
            current_volume = 0

        # ── Insider trades ──────────────────────────────────────────────────
        insider_trades = list(
            InsiderTrade.objects.filter(stock=stock).order_by("-date")[:5]
        )
        buys = sum(1 for t in insider_trades if t.trade_type.upper() == "BUY")
        sells = sum(1 for t in insider_trades if t.trade_type.upper() == "SELL")

        if not insider_trades:
            insider_sentiment = "none"
        elif buys > sells * 1.5:
            insider_sentiment = "buying"
        elif sells > buys * 1.5:
            insider_sentiment = "selling"
        else:
            insider_sentiment = "mixed"

        insider_summary = [
            {
                "name": t.insider_name,
                "action": t.trade_type.upper(),
                "quantity": t.quantity,
                "price": t.price,
                "date": t.date.strftime("%d %b %Y"),
            }
            for t in insider_trades[:3]
        ]

        # ── Recent filings ──────────────────────────────────────────────────
        filings = list(
            Filing.objects.filter(stock=stock).order_by("-created_at")[:3]
        )
        recent_filings = [
            {
                "title": f.title,
                "type": f.filing_type,
                "description": f.description[:150] if f.description else "",
                "date": f.created_at.strftime("%d %b %Y"),
            }
            for f in filings
        ]

        # ── Confidence score ────────────────────────────────────────────────
        # More data → higher confidence; insider + filing data boost confidence
        base = 40 + min(data_points, 30)  # up to 70 from price data
        if insider_trades:
            base += 10
        if filings:
            base += 10
        confidence_score = self.clamp_confidence(base)

        return {
            "symbol": symbol,
            "name": stock.name,
            "sector": stock.sector or "Unknown",
            "price": round(current_price, 2),
            "prev_price": round(prev_price, 2),
            "price_change": price_change,
            "price_change_pct": price_change_pct,
            "trend": trend,
            "volume_signal": volume_signal,
            "volume_raw": current_volume,
            "insider_sentiment": insider_sentiment,
            "insider_summary": insider_summary,
            "recent_filings": recent_filings,
            "data_points": data_points,
            "confidence_score": confidence_score,
        }

    def _not_found(self, symbol: str) -> dict:
        return {
            "symbol": symbol,
            "name": "Unknown",
            "sector": "Unknown",
            "price": 0.0,
            "prev_price": 0.0,
            "price_change": 0.0,
            "price_change_pct": 0.0,
            "trend": "neutral",
            "volume_signal": "normal",
            "volume_raw": 0,
            "insider_sentiment": "none",
            "insider_summary": [],
            "recent_filings": [],
            "data_points": 0,
            "confidence_score": 0,
            "not_found": True,
        }
