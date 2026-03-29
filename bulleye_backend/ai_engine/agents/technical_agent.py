"""
Technical Analysis Agent — Interprets RSI, MACD, EMA, and chart patterns.

Queries:
  - Indicator (rsi, macd, ema) from analytics app
  - Pattern (pattern_name, success_rate) from analytics app
  - BacktestResult for strategy performance context

Output keys:
  rsi             : raw RSI value (float | None)
  rsi_zone        : "oversold" | "neutral" | "overbought"
  rsi_signal      : trading implication of RSI zone
  macd            : raw MACD value (float | None)
  macd_signal     : "bullish_crossover" | "bearish_crossover" | "neutral"
  ema             : raw EMA value (float | None)
  ema_trend       : "above_ema" | "below_ema" | "at_ema"
  patterns        : list of detected patterns (list[dict])
  top_pattern     : highest confidence pattern (dict | None)
  backtest        : best backtest strategy result (dict | None)
  confidence_score: 0-100 aggregate technical confidence (int)
"""

import logging
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class TechnicalAgent(BaseAgent):
    agent_name = "TechnicalAgent"

    # RSI thresholds
    RSI_OVERSOLD = 35
    RSI_OVERBOUGHT = 65

    def analyze(self, symbol: str, user=None) -> dict:
        from analytics.models import Indicator, Pattern, BacktestResult
        from market_data.models import Stock, StockPrice

        symbol = symbol.upper().strip()

        try:
            stock = Stock.objects.get(symbol=symbol)
        except Stock.DoesNotExist:
            return self._empty(symbol)

        # ── Indicators ──────────────────────────────────────────────────────
        indicator = (
            Indicator.objects.filter(stock=stock).order_by("-date").first()
        )

        rsi = indicator.rsi if indicator else None
        macd = indicator.macd if indicator else None
        ema = indicator.ema if indicator else None

        # RSI interpretation
        if rsi is None:
            rsi_zone = "unknown"
            rsi_signal = "No RSI data available"
        elif rsi < self.RSI_OVERSOLD:
            rsi_zone = "oversold"
            rsi_signal = f"RSI at {rsi:.1f} — stock may be oversold, potential bounce"
        elif rsi > self.RSI_OVERBOUGHT:
            rsi_zone = "overbought"
            rsi_signal = f"RSI at {rsi:.1f} — stock may be overbought, caution advised"
        else:
            rsi_zone = "neutral"
            rsi_signal = f"RSI at {rsi:.1f} — in neutral territory"

        # MACD interpretation (positive = bullish momentum)
        if macd is None:
            macd_signal = "unknown"
            macd_label = "No MACD data"
        elif macd > 0.5:
            macd_signal = "bullish_crossover"
            macd_label = f"MACD at +{macd:.2f} — bullish momentum building"
        elif macd < -0.5:
            macd_signal = "bearish_crossover"
            macd_label = f"MACD at {macd:.2f} — bearish momentum"
        else:
            macd_signal = "neutral"
            macd_label = f"MACD near zero ({macd:.2f}) — consolidating"

        # EMA vs current price
        latest_price = StockPrice.objects.filter(stock=stock).order_by("-date").first()
        current_price = latest_price.close_price if latest_price else None

        if ema is None or current_price is None:
            ema_trend = "unknown"
            ema_label = "No EMA data"
        elif current_price > ema * 1.01:
            ema_trend = "above_ema"
            ema_label = f"Price (₹{current_price:.2f}) above EMA (₹{ema:.2f}) — bullish positioning"
        elif current_price < ema * 0.99:
            ema_trend = "below_ema"
            ema_label = f"Price (₹{current_price:.2f}) below EMA (₹{ema:.2f}) — bearish positioning"
        else:
            ema_trend = "at_ema"
            ema_label = f"Price hugging EMA (₹{ema:.2f}) — at decision point"

        # ── Patterns ────────────────────────────────────────────────────────
        pattern_qs = Pattern.objects.filter(stock=stock).order_by("-success_rate")[:5]
        patterns = [
            {
                "name": p.pattern_name,
                "success_rate": round(p.success_rate, 1),
                "detected": _humanize_date(p.detected_at),
                "implication": _pattern_implication(p.pattern_name),
            }
            for p in pattern_qs
        ]
        top_pattern = patterns[0] if patterns else None

        # ── Backtest ────────────────────────────────────────────────────────
        bt = BacktestResult.objects.filter(stock=stock).order_by("-win_rate").first()
        backtest = None
        if bt:
            backtest = {
                "strategy": bt.strategy_name,
                "win_rate": round(bt.win_rate, 1),
                "avg_return": round(bt.avg_return, 2),
            }

        # ── Confidence scoring ───────────────────────────────────────────────
        scores = []
        weights = []

        if rsi is not None:
            # Oversold → bullish confidence; overbought → bearish caution
            if rsi_zone == "oversold":
                scores.append(72)
            elif rsi_zone == "overbought":
                scores.append(35)
            else:
                scores.append(55)
            weights.append(3)

        if macd is not None:
            if macd_signal == "bullish_crossover":
                scores.append(75)
            elif macd_signal == "bearish_crossover":
                scores.append(30)
            else:
                scores.append(50)
            weights.append(3)

        if ema_trend == "above_ema":
            scores.append(70)
            weights.append(2)
        elif ema_trend == "below_ema":
            scores.append(35)
            weights.append(2)

        if patterns:
            avg_pattern_confidence = sum(p["success_rate"] for p in patterns) / len(patterns)
            scores.append(avg_pattern_confidence)
            weights.append(2)

        confidence_score = self.combine_confidences(*scores, weights=weights) if scores else 50

        return {
            "symbol": symbol,
            "rsi": round(rsi, 2) if rsi is not None else None,
            "rsi_zone": rsi_zone,
            "rsi_signal": rsi_signal,
            "macd": round(macd, 4) if macd is not None else None,
            "macd_signal": macd_signal,
            "macd_label": macd_label,
            "ema": round(ema, 2) if ema is not None else None,
            "ema_trend": ema_trend,
            "ema_label": ema_label,
            "patterns": patterns,
            "top_pattern": top_pattern,
            "backtest": backtest,
            "confidence_score": confidence_score,
        }

    def _empty(self, symbol: str) -> dict:
        return {
            "symbol": symbol,
            "rsi": None, "rsi_zone": "unknown", "rsi_signal": "Stock not found",
            "macd": None, "macd_signal": "unknown", "macd_label": "Stock not found",
            "ema": None, "ema_trend": "unknown", "ema_label": "Stock not found",
            "patterns": [], "top_pattern": None, "backtest": None,
            "confidence_score": 0,
        }


def _humanize_date(dt) -> str:
    from django.utils import timezone
    delta = timezone.now() - dt
    days = delta.days
    if days == 0:
        return "Today"
    elif days == 1:
        return "Yesterday"
    else:
        return f"{days} days ago"


def _pattern_implication(name: str) -> str:
    """Map common chart pattern names to a beginner-friendly implication."""
    name_lower = name.lower()
    bullish_patterns = ["cup", "handle", "ascending", "double bottom", "inverse head", "hammer", "breakout", "golden"]
    bearish_patterns = ["head and shoulders", "descending", "double top", "shooting star", "bearish", "death cross"]

    for p in bullish_patterns:
        if p in name_lower:
            return "Bullish continuation likely"
    for p in bearish_patterns:
        if p in name_lower:
            return "Bearish reversal possible"
    return "Watch for confirmation"
