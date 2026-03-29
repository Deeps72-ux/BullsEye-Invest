"""
Signal Detection Agent — Identifies high-confidence bullish/bearish opportunities.

Queries:
  - Signal model from signals app (filtered for specific stock or all high-confidence)

Output keys:
  active_signals    : list of signals above confidence threshold (list[dict])
  total_signals     : count of all signals for this stock (int)
  bullish_count     : count of bullish signals (int)
  bearish_count     : count of bearish signals (int)
  consensus         : "bullish" | "bearish" | "neutral" | "mixed"
  top_signal        : highest confidence signal (dict | None)
  signal_tags       : aggregated tags across all signals (list[str])
  confidence_score  : 0-100 aggregate signal confidence (int)
"""

import logging
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

# Minimum confidence to include a signal as "active"
THRESHOLD = 60


class SignalAgent(BaseAgent):
    agent_name = "SignalAgent"

    def analyze(self, symbol: str, user=None) -> dict:
        from signals.models import Signal
        from market_data.models import Stock

        symbol = symbol.upper().strip()

        try:
            stock = Stock.objects.get(symbol=symbol)
        except Stock.DoesNotExist:
            return self._empty(symbol)

        all_signals = list(
            Signal.objects.filter(stock=stock).order_by("-confidence", "-created_at")
        )
        total_signals = len(all_signals)

        active_signals = [s for s in all_signals if s.confidence >= THRESHOLD]

        bullish_count = sum(1 for s in all_signals if s.signal_type == "bullish")
        bearish_count = sum(1 for s in all_signals if s.signal_type == "bearish")

        # Consensus logic
        if total_signals == 0:
            consensus = "neutral"
        elif bullish_count > bearish_count * 1.5:
            consensus = "bullish"
        elif bearish_count > bullish_count * 1.5:
            consensus = "bearish"
        elif bullish_count > 0 and bearish_count > 0:
            consensus = "mixed"
        else:
            consensus = "neutral"

        # Serialize signals
        serialized = [
            {
                "id": s.id,
                "type": s.signal_type,
                "confidence": s.confidence,
                "reason": s.reason,
                "tags": _extract_tags(s.reason),
                "created_at": s.created_at.strftime("%d %b %Y"),
            }
            for s in active_signals[:5]
        ]
        top_signal = serialized[0] if serialized else None

        # Aggregate tags
        all_tags: list[str] = []
        for s in active_signals:
            all_tags.extend(_extract_tags(s.reason))
        signal_tags = list(dict.fromkeys(all_tags))[:6]  # deduplicate, max 6

        # Confidence score: weighted by top signal confidence + consensus strength
        if not active_signals:
            confidence_score = 20
        else:
            top_conf = active_signals[0].confidence
            consensus_boost = {
                "bullish": 10,
                "bearish": 10,
                "mixed": 0,
                "neutral": -10,
            }.get(consensus, 0)
            confidence_score = self.clamp_confidence(top_conf + consensus_boost)

        return {
            "symbol": symbol,
            "active_signals": serialized,
            "total_signals": total_signals,
            "bullish_count": bullish_count,
            "bearish_count": bearish_count,
            "consensus": consensus,
            "top_signal": top_signal,
            "signal_tags": signal_tags,
            "confidence_score": confidence_score,
        }

    def _empty(self, symbol: str) -> dict:
        return {
            "symbol": symbol,
            "active_signals": [],
            "total_signals": 0,
            "bullish_count": 0,
            "bearish_count": 0,
            "consensus": "neutral",
            "top_signal": None,
            "signal_tags": [],
            "confidence_score": 0,
        }


def _extract_tags(reason: str) -> list[str]:
    """Keyword-based tag extraction from signal reason text."""
    keywords = {
        "breakout": "Breakout",
        "volume": "High Volume",
        "golden cross": "Golden Cross",
        "death cross": "Death Cross",
        "institutional": "Institutional",
        "pattern": "Pattern",
        "earnings": "Earnings Beat",
        "growth": "Growth",
        "ai": "AI Play",
        "support": "Support",
        "resistance": "Resistance",
        "rsi": "RSI",
        "macd": "MACD",
        "diverging": "Diverging",
        "oversold": "Oversold",
        "overbought": "Overbought",
        "momentum": "Momentum",
    }
    lower = reason.lower()
    return list({v for k, v in keywords.items() if k in lower})[:4]
