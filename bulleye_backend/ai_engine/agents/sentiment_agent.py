"""
Sentiment Agent — Detects sentiment from filings, insider trades, and signal text.

Queries:
  - Filing model (keyword analysis of titles and descriptions)
  - InsiderTrade model (buy vs sell patterns)
  - Signal.reason text (keyword sentiment scan)

Output keys:
  sentiment_score  : 0-100 (50 = neutral, >65 = positive, <35 = negative)
  sentiment_label  : "very_positive" | "positive" | "neutral" | "negative" | "very_negative"
  sentiment_emoji  : visual shorthand 🟢 🟡 🔴
  key_events       : list of notable events driving sentiment (list[dict])
  filing_sentiment : sentiment from corporate filings alone
  insider_sentiment: sentiment from insider trade patterns
  signal_sentiment : sentiment from signal text analysis
  confidence_score : 0-100 (int) — higher when more data sources contribute
"""

import logging
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

# Filing keywords → sentiment weights
_BULLISH_FILING_KEYWORDS = [
    "record profit", "dividend", "buyback", "acquisition", "expansion",
    "strong earnings", "beat", "outperform", "revenue growth", "new order",
    "contract win", "partnership", "upgrade", "bonus share",
]
_BEARISH_FILING_KEYWORDS = [
    "loss", "fraud", "penalty", "downgrade", "recall", "layoff",
    "write-off", "impairment", "default", "investigation", "regulatory action",
    "miss", "disappointing", "withdrawal", "debt",
]


class SentimentAgent(BaseAgent):
    agent_name = "SentimentAgent"

    def analyze(self, symbol: str, user=None) -> dict:
        from market_data.models import Stock, Filing, InsiderTrade
        from signals.models import Signal

        symbol = symbol.upper().strip()

        try:
            stock = Stock.objects.get(symbol=symbol)
        except Stock.DoesNotExist:
            return self._empty(symbol)

        scores = []
        key_events = []

        # ── Filing sentiment ─────────────────────────────────────────────────
        filings = list(
            Filing.objects.filter(stock=stock).order_by("-created_at")[:10]
        )
        filing_score = 50  # neutral baseline
        if filings:
            filing_bull = 0
            filing_bear = 0
            for f in filings:
                text = (f.title + " " + (f.description or "")).lower()
                bull_hits = sum(1 for kw in _BULLISH_FILING_KEYWORDS if kw in text)
                bear_hits = sum(1 for kw in _BEARISH_FILING_KEYWORDS if kw in text)
                filing_bull += bull_hits
                filing_bear += bear_hits
                if bull_hits > 0 or bear_hits > 0:
                    key_events.append({
                        "source": "Filing",
                        "event": f.title,
                        "sentiment": "positive" if bull_hits > bear_hits else "negative",
                        "date": f.created_at.strftime("%d %b %Y"),
                    })
            if filing_bull + filing_bear > 0:
                filing_score = int(50 + 50 * (filing_bull - filing_bear) / (filing_bull + filing_bear))
            scores.append(filing_score)

        # ── Insider sentiment ────────────────────────────────────────────────
        insider_trades = list(
            InsiderTrade.objects.filter(stock=stock).order_by("-date")[:10]
        )
        insider_score = 50
        if insider_trades:
            buy_qty = sum(t.quantity for t in insider_trades if t.trade_type.upper() == "BUY")
            sell_qty = sum(t.quantity for t in insider_trades if t.trade_type.upper() == "SELL")
            total_qty = buy_qty + sell_qty
            if total_qty > 0:
                buy_ratio = buy_qty / total_qty
                insider_score = int(30 + 60 * buy_ratio)  # 30–90 range
            scores.append(insider_score)
            if buy_qty > sell_qty:
                key_events.append({
                    "source": "Insider",
                    "event": f"Insiders net bought {buy_qty - sell_qty:,} shares recently",
                    "sentiment": "positive",
                    "date": insider_trades[0].date.strftime("%d %b %Y"),
                })
            elif sell_qty > buy_qty:
                key_events.append({
                    "source": "Insider",
                    "event": f"Insiders net sold {sell_qty - buy_qty:,} shares recently",
                    "sentiment": "negative",
                    "date": insider_trades[0].date.strftime("%d %b %Y"),
                })

        # ── Signal text sentiment ────────────────────────────────────────────
        signals = list(
            Signal.objects.filter(stock=stock).order_by("-created_at")[:10]
        )
        signal_score = 50
        if signals:
            bull_signals = sum(1 for s in signals if s.signal_type == "bullish")
            bear_signals = sum(1 for s in signals if s.signal_type == "bearish")
            total_sigs = len(signals)
            if total_sigs > 0:
                signal_score = int(50 + 40 * (bull_signals - bear_signals) / total_sigs)
            scores.append(signal_score)

        # ── Aggregate ────────────────────────────────────────────────────────
        if scores:
            sentiment_score = self.clamp_confidence(sum(scores) / len(scores))
        else:
            sentiment_score = 50

        # Label
        if sentiment_score >= 75:
            sentiment_label = "very_positive"
            sentiment_emoji = "🟢"
        elif sentiment_score >= 60:
            sentiment_label = "positive"
            sentiment_emoji = "🟢"
        elif sentiment_score >= 42:
            sentiment_label = "neutral"
            sentiment_emoji = "🟡"
        elif sentiment_score >= 28:
            sentiment_label = "negative"
            sentiment_emoji = "🔴"
        else:
            sentiment_label = "very_negative"
            sentiment_emoji = "🔴"

        confidence_score = self.clamp_confidence(
            30 + 20 * min(len(scores), 3)  # up to 90 if all 3 sources available
        )

        return {
            "symbol": symbol,
            "sentiment_score": sentiment_score,
            "sentiment_label": sentiment_label,
            "sentiment_emoji": sentiment_emoji,
            "key_events": key_events[:5],
            "filing_sentiment": filing_score,
            "insider_sentiment": insider_score,
            "signal_sentiment": signal_score,
            "data_sources": len(scores),
            "confidence_score": confidence_score,
        }

    def _empty(self, symbol: str) -> dict:
        return {
            "symbol": symbol,
            "sentiment_score": 50,
            "sentiment_label": "neutral",
            "sentiment_emoji": "🟡",
            "key_events": [],
            "filing_sentiment": 50,
            "insider_sentiment": 50,
            "signal_sentiment": 50,
            "data_sources": 0,
            "confidence_score": 0,
        }
