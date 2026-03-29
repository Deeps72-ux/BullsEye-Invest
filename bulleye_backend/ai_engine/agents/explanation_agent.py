"""
Explanation Agent — LLM layer that converts raw agent outputs into plain-English insights.

Strategy:
  1. If OPENAI_API_KEY is configured → use GPT-4o-mini for natural language generation
  2. Fallback → high-quality rule-based template engine (always enabled as safety net)

Output keys:
  summary          : 2-3 sentence executive summary for a beginner (str)
  reasoning        : bullet-point reasoning behind the recommendation (list[str])
  final_recommendation: "BUY" | "HOLD" | "AVOID" | "WATCH"
  confidence       : overall confidence 0-100 (int)
  confidence_label : "Very High" | "High" | "Moderate" | "Low" | "Very Low"
  beginner_tip     : one actionable plain-English tip (str)
  disclaimer       : standard investment disclaimer (str)
  generated_by     : "openai" | "rule_based"
"""

import logging
import os
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)

_DISCLAIMER = (
    "⚠️ This analysis is for educational purposes only and does not constitute "
    "financial advice. Investing in stocks involves risk. Please do your own "
    "research or consult a SEBI-registered financial advisor before investing."
)


class ExplanationAgent(BaseAgent):
    agent_name = "ExplanationAgent"

    def analyze(self, symbol: str, user=None) -> dict:
        """Not used directly — use explain() instead."""
        return self.explain(symbol, {})

    def explain(self, symbol: str, agg: dict) -> dict:
        """
        Generate a plain-English explanation from aggregated agent outputs.

        Args:
            symbol: Stock symbol
            agg: Dict containing outputs from all other agents:
                 keys: market_data, technical, signals, portfolio, sentiment
        """
        # Compute final recommendation from agent confidences
        recommendation, confidence = self._compute_recommendation(agg)
        confidence_label = self.score_to_label(confidence)

        # Try LLM first; fall back gracefully
        api_key = os.getenv("GROQ_API_KEY", "")
        if api_key and len(api_key) > 5:
            try:
                return self._llm_explain(
                    symbol, agg, recommendation, confidence, confidence_label, api_key
                )
            except Exception as exc:
                logger.warning(f"[ExplanationAgent] Groq LLM failed: {exc}. Using rule-based fallback.")

        return self._rule_based_explain(
            symbol, agg, recommendation, confidence, confidence_label
        )

    # ── Recommendation Engine ────────────────────────────────────────────────

    def _compute_recommendation(self, agg: dict) -> tuple[str, int]:
        """
        Weighted vote across all agent confidence scores and consensus signals
        to produce a final BUY / HOLD / AVOID / WATCH recommendation.
        """
        scores = []
        weights = []

        market = agg.get("market_data", {})
        technical = agg.get("technical", {})
        signals = agg.get("signals", {})
        portfolio = agg.get("portfolio", {})
        sentiment = agg.get("sentiment", {})

        # Market trend vote
        trend_map = {"bullish": 75, "neutral": 50, "bearish": 30}
        if market.get("trend"):
            scores.append(trend_map.get(market["trend"], 50))
            weights.append(2)

        # Technical confidence
        tech_conf = technical.get("confidence_score")
        if tech_conf is not None:
            scores.append(tech_conf)
            weights.append(3)

        # Signal consensus vote
        consensus_map = {"bullish": 80, "mixed": 50, "neutral": 45, "bearish": 25}
        sig_consensus = signals.get("consensus")
        sig_confidence = signals.get("confidence_score", 50)
        if sig_consensus:
            scores.append(consensus_map.get(sig_consensus, 50))
            scores.append(sig_confidence)
            weights.extend([2, 2])

        # Sentiment score
        sentiment_score = sentiment.get("sentiment_score", 50)
        scores.append(sentiment_score)
        weights.append(1)

        # Volume signal
        vol_map = {"above_average": 10, "normal": 0, "below_average": -10}
        vol_boost = vol_map.get(market.get("volume_signal", "normal"), 0)

        # Insider boost
        insider_map = {"buying": 8, "selling": -8, "mixed": 0, "none": 0}
        insider_boost = insider_map.get(market.get("insider_sentiment", "none"), 0)

        if scores:
            raw_confidence = self.combine_confidences(*scores, weights=weights)
            confidence = self.clamp_confidence(raw_confidence + vol_boost + insider_boost)
        else:
            confidence = 50

        # Decision thresholds
        if confidence >= 68:
            recommendation = "BUY"
        elif confidence >= 55:
            recommendation = "HOLD"
        elif confidence >= 40:
            recommendation = "WATCH"
        else:
            recommendation = "AVOID"

        return recommendation, confidence

    # ── Rule-Based Explanation ────────────────────────────────────────────────

    def _rule_based_explain(
        self,
        symbol: str,
        agg: dict,
        recommendation: str,
        confidence: int,
        confidence_label: str,
    ) -> dict:
        market = agg.get("market_data", {})
        technical = agg.get("technical", {})
        signals = agg.get("signals", {})
        portfolio = agg.get("portfolio", {})
        sentiment = agg.get("sentiment", {})

        name = market.get("name", symbol)
        price = market.get("price", "N/A")
        trend = market.get("trend", "neutral")
        rsi_zone = technical.get("rsi_zone", "unknown")
        macd_signal = technical.get("macd_signal", "unknown")
        consensus = signals.get("consensus", "neutral")
        sentiment_label = sentiment.get("sentiment_label", "neutral")
        portfolio_note = portfolio.get("suggestion", "")

        # ── Summary ──────────────────────────────────────────────────────────
        rec_phrases = {
            "BUY": f"Our analysis suggests {name} ({symbol}) is showing **bullish signals** with a {confidence_label.lower()} confidence level.",
            "HOLD": f"{name} ({symbol}) is in a **consolidation phase** — not a compelling buy right now, but no major red flags either.",
            "WATCH": f"{name} ({symbol}) shows **mixed signals** — worth monitoring but wait for stronger confirmation before entering.",
            "AVOID": f"Our analysis flags **concerning signals** for {name} ({symbol}). It may be wise to stay on the sidelines for now.",
        }
        summary = rec_phrases.get(recommendation, f"Analysis complete for {symbol}.")
        if price and price != "N/A":
            summary += f" Current price: ₹{price:,.2f}."

        # ── Reasoning bullets ─────────────────────────────────────────────
        reasoning = []

        # Market trend
        trend_text = {
            "bullish": f"📈 Price trend is **bullish** — the 5-day average is above the 20-day average, indicating upward momentum.",
            "bearish": f"📉 Price trend is **bearish** — recent prices are falling below the 20-day average.",
            "neutral": f"➡️ Price trend is **neutral** — the stock is trading sideways without a clear direction.",
        }
        reasoning.append(trend_text.get(trend, "Price trend data unavailable."))

        # RSI
        rsi_val = technical.get("rsi")
        if rsi_val is not None:
            reasoning.append(f"📊 RSI at {rsi_val:.1f}: {technical.get('rsi_signal', '')}")

        # MACD
        if technical.get("macd_label"):
            reasoning.append(f"📉 Momentum: {technical['macd_label']}")

        # EMA
        if technical.get("ema_label"):
            reasoning.append(f"📐 EMA: {technical['ema_label']}")

        # Signals
        bull_count = signals.get("bullish_count", 0)
        bear_count = signals.get("bearish_count", 0)
        if bull_count or bear_count:
            reasoning.append(
                f"🔔 Signals: {bull_count} bullish, {bear_count} bearish detected — consensus is **{consensus}**."
            )

        # Sentiment
        emoji = sentiment.get("sentiment_emoji", "🟡")
        reasoning.append(
            f"{emoji} Overall market sentiment for {symbol} is **{sentiment_label.replace('_', ' ')}**."
        )

        # Insider
        insider = market.get("insider_sentiment", "none")
        if insider != "none":
            insider_text = {
                "buying": "✅ Company insiders are **net buyers** — a positive signal that management is confident.",
                "selling": "⚠️ Company insiders are **net sellers** — could signal caution.",
                "mixed": "ℹ️ Insider activity is **mixed** — no strong directional signal.",
            }
            reasoning.append(insider_text.get(insider, ""))

        # Volume
        vol = market.get("volume_signal", "normal")
        if vol == "above_average":
            reasoning.append("📦 Trading volume is **above average** — strong market participation supporting the move.")
        elif vol == "below_average":
            reasoning.append("📦 Trading volume is **below average** — move may lack conviction.")

        # Top pattern
        if technical.get("top_pattern"):
            p = technical["top_pattern"]
            reasoning.append(
                f"🔍 Chart pattern detected: **{p['name']}** ({p['success_rate']:.0f}% historical success rate) — {p['implication']}."
            )

        # Portfolio note
        if portfolio_note:
            reasoning.append(f"💼 Portfolio impact: {portfolio_note}")

        # ── Beginner tip ─────────────────────────────────────────────────────
        beginner_tips = {
            "BUY": (
                f"If you decide to invest in {symbol}, consider starting with a small amount (3-5% of your portfolio) "
                f"and buying in 2-3 parts rather than all at once. Set a stop-loss at 8-10% below your entry price."
            ),
            "HOLD": (
                f"If you already own {symbol}, patience is key. Wait for clearer signals before adding more. "
                f"Review your position size — make sure it's not more than 10-15% of your portfolio."
            ),
            "WATCH": (
                f"Add {symbol} to your watchlist. Look for a confirmed breakout above resistance with high volume "
                f"before entering. Set a price alert on your broker app."
            ),
            "AVOID": (
                f"Staying in cash is also a valid investment decision. For now, look at other opportunities "
                f"while {symbol} stabilizes. Never invest in panic or FOMO."
            ),
        }
        beginner_tip = beginner_tips.get(recommendation, "Always invest within your risk tolerance.")

        return {
            "symbol": symbol,
            "summary": summary,
            "reasoning": [r for r in reasoning if r],
            "final_recommendation": recommendation,
            "confidence": confidence,
            "confidence_label": confidence_label,
            "beginner_tip": beginner_tip,
            "disclaimer": _DISCLAIMER,
            "generated_by": "rule_based",
        }

    # ── OpenAI LLM Explanation ────────────────────────────────────────────────

    def _llm_explain(
        self,
        symbol: str,
        agg: dict,
        recommendation: str,
        confidence: int,
        confidence_label: str,
        api_key: str,
    ) -> dict:
        from openai import OpenAI
        import requests

        client = OpenAI(api_key=api_key, base_url="https://api.groq.com/openai/v1")
        
        # Fetch real-time news via Tavily if configured
        tavily_api_key = os.getenv("TAVILY_API_KEY", "")
        news_context = "No recent news retrieved."
        if tavily_api_key and len(tavily_api_key) > 5:
            try:
                tavily_response = requests.post("https://api.tavily.com/search", json={
                    "api_key": tavily_api_key,
                    "query": f"{symbol} stock news recent developments India",
                    "search_depth": "basic",
                    "include_answer": False,
                    "max_results": 3,
                }, timeout=5)
                if tavily_response.status_code == 200:
                    results = tavily_response.json().get("results", [])
                    if results:
                        news_context = "\n".join([f"- {r.get('title')}: {r.get('content')}" for r in results])
            except Exception as exc:
                logger.warning(f"[ExplanationAgent] Tavily search failed: {exc}")

        market = agg.get("market_data", {})
        technical = agg.get("technical", {})
        signals = agg.get("signals", {})
        sentiment = agg.get("sentiment", {})
        portfolio = agg.get("portfolio", {})

        context = f"""
Stock: {symbol} ({market.get('name', symbol)})
Sector: {market.get('sector', 'N/A')}
Current Price: ₹{market.get('price', 'N/A')}
Price Trend: {market.get('trend', 'N/A')}
Volume Signal: {market.get('volume_signal', 'N/A')}
Insider Sentiment: {market.get('insider_sentiment', 'N/A')}

Technical Indicators:
- RSI: {technical.get('rsi', 'N/A')} ({technical.get('rsi_zone', 'N/A')})
- MACD Signal: {technical.get('macd_signal', 'N/A')}
- EMA Trend: {technical.get('ema_trend', 'N/A')}
- Top Pattern: {technical.get('top_pattern', {}).get('name', 'None')} ({technical.get('top_pattern', {}).get('success_rate', 0):.0f}% success)

Signal Consensus: {signals.get('consensus', 'N/A')} ({signals.get('bullish_count', 0)} bullish, {signals.get('bearish_count', 0)} bearish)

Sentiment: {sentiment.get('sentiment_label', 'neutral')} (score: {sentiment.get('sentiment_score', 50)}/100)

Portfolio Impact: {portfolio.get('suggestion', 'N/A')}

Recent News (Tavily):
{news_context}

AI Recommendation: {recommendation} (Confidence: {confidence}/100 — {confidence_label})
        """.strip()

        prompt = f"""
You are BullsEye, an AI investment advisor for Indian retail investors.
Analyze the following data and respond in structured JSON with these exact keys:
- summary: 2-3 sentence plain-English executive summary (beginner-friendly, mention price in ₹)
- reasoning: list of 5-7 bullet points explaining why (use emojis, plain language, no jargon)
- beginner_tip: one actionable, friendly tip for a first-time investor about this stock
Do NOT include the disclaimer (already handled separately).
Respond ONLY with valid JSON.

{context}
        """.strip()

        response = client.chat.completions.create(
            model="llama3-70b-8192",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.4,
            max_tokens=800,
            response_format={"type": "json_object"},
        )

        import json
        parsed = json.loads(response.choices[0].message.content)

        return {
            "symbol": symbol,
            "summary": parsed.get("summary", ""),
            "reasoning": parsed.get("reasoning", []),
            "final_recommendation": recommendation,
            "confidence": confidence,
            "confidence_label": confidence_label,
            "beginner_tip": parsed.get("beginner_tip", ""),
            "disclaimer": _DISCLAIMER,
            "generated_by": "groq",
        }
