"""
Orchestrator Agent — The central brain of BullsEye's AI system.

Workflow:
  1. Parse query intent (symbol + intent type)
  2. Dispatch agents in parallel using ThreadPoolExecutor
  3. Collect and aggregate results
  4. Call ExplanationAgent to synthesize
  5. Persist to ChatQuery for memory/history
  6. Return fully structured response

Usage:
    orchestrator = OrchestratorAgent()
    result = orchestrator.handle_query(user=request.user, query="Should I buy TCS?")
"""

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from django.conf import settings

from .market_data_agent import MarketDataAgent
from .technical_agent import TechnicalAgent
from .signal_agent import SignalAgent
from .portfolio_agent import PortfolioAgent
from .sentiment_agent import SentimentAgent
from .explanation_agent import ExplanationAgent
from ..intent_parser import IntentParser

logger = logging.getLogger(__name__)

# Max parallel threads for agent execution
_MAX_WORKERS = getattr(settings, "AI_ENGINE", {}).get("MAX_WORKERS", 4)


class OrchestratorAgent:
    """
    Central coordinator that routes queries to specialized agents,
    aggregates their outputs, and synthesizes a structured recommendation.
    """

    def __init__(self):
        self.intent_parser = IntentParser()
        self.market_agent = MarketDataAgent()
        self.technical_agent = TechnicalAgent()
        self.signal_agent = SignalAgent()
        self.portfolio_agent = PortfolioAgent()
        self.sentiment_agent = SentimentAgent()
        self.explanation_agent = ExplanationAgent()

    def handle_query(self, query: str, user=None) -> dict:
        """
        Main entry point. Accepts a free-form query and an optional Django User.

        Returns a fully structured response with:
          - query metadata (symbol, intent)
          - per-agent outputs
          - synthesized explanation
          - final recommendation + confidence
          - memory: saved to ChatQuery DB
        """
        start_time = time.time()

        # ── Step 1: Parse Intent ─────────────────────────────────────────────
        parsed = self.intent_parser.parse(query)
        symbol = parsed.get("symbol")
        intent = parsed.get("intent", "general")

        logger.info(f"[Orchestrator] query={query!r} → symbol={symbol}, intent={intent}")

        # ── Step 2: Route based on intent ────────────────────────────────────
        if not symbol:
            return self._handle_no_symbol(query, intent, user)

        # ── Step 3: Parallel agent execution ─────────────────────────────────
        agent_results = self._run_agents_parallel(symbol, user, intent)

        # ── Step 4: Synthesize explanation ───────────────────────────────────
        explanation = self.explanation_agent.explain(symbol, agent_results)

        # ── Step 5: Compose final response ───────────────────────────────────
        elapsed_ms = round((time.time() - start_time) * 1000)

        response = {
            # ─ Query Metadata ─
            "query": query,
            "symbol": symbol,
            "intent": intent,
            "intent_display": parsed.get("intent_display"),

            # ─ Per-Agent Outputs ─
            "market_data": agent_results.get("market_data", {}),
            "technical_analysis": agent_results.get("technical", {}),
            "signals": agent_results.get("signals", {}),
            "portfolio_impact": agent_results.get("portfolio", {}),
            "sentiment": agent_results.get("sentiment", {}),

            # ─ Synthesized Explanation ─
            "summary": explanation.get("summary", ""),
            "reasoning": explanation.get("reasoning", []),
            "beginner_tip": explanation.get("beginner_tip", ""),
            "disclaimer": explanation.get("disclaimer", ""),

            # ─ Final Verdict ─
            "final_recommendation": explanation.get("final_recommendation", "HOLD"),
            "confidence": explanation.get("confidence", 50),
            "confidence_label": explanation.get("confidence_label", "Moderate"),

            # ─ Metadata ─
            "generated_by": explanation.get("generated_by", "rule_based"),
            "processing_time_ms": elapsed_ms,
        }

        # ── Step 6: Save to memory (non-blocking) ──────────────────────────
        self._save_to_memory(user, query, symbol, intent, response)

        return response

    def analyze_stock(self, symbol: str, user=None) -> dict:
        """
        Direct stock analysis without a natural language query.
        Used by the /api/ai/explain/<symbol>/ endpoint.
        """
        symbol = symbol.upper().strip()
        start_time = time.time()

        agent_results = self._run_agents_parallel(symbol, user, intent="explain_stock")
        explanation = self.explanation_agent.explain(symbol, agent_results)
        elapsed_ms = round((time.time() - start_time) * 1000)

        return {
            "query": f"Analyze {symbol}",
            "symbol": symbol,
            "intent": "explain_stock",
            "intent_display": "Stock Analysis",
            "market_data": agent_results.get("market_data", {}),
            "technical_analysis": agent_results.get("technical", {}),
            "signals": agent_results.get("signals", {}),
            "portfolio_impact": agent_results.get("portfolio", {}),
            "sentiment": agent_results.get("sentiment", {}),
            "summary": explanation.get("summary", ""),
            "reasoning": explanation.get("reasoning", []),
            "beginner_tip": explanation.get("beginner_tip", ""),
            "disclaimer": explanation.get("disclaimer", ""),
            "final_recommendation": explanation.get("final_recommendation", "HOLD"),
            "confidence": explanation.get("confidence", 50),
            "confidence_label": explanation.get("confidence_label", "Moderate"),
            "generated_by": explanation.get("generated_by", "rule_based"),
            "processing_time_ms": elapsed_ms,
        }

    # ── Private: Parallel Execution ──────────────────────────────────────────

    def _run_agents_parallel(self, symbol: str, user, intent: str) -> dict:
        """
        Dispatches all agents in parallel using a ThreadPoolExecutor.
        Returns a dict keyed by agent category.
        """
        results = {}

        def run(key, agent):
            return key, agent.safe_analyze(symbol, user)

        # Define which agents to run
        agent_map = {
            "market_data": self.market_agent,
            "technical": self.technical_agent,
            "signals": self.signal_agent,
            "sentiment": self.sentiment_agent,
        }

        # Portfolio agent only for authenticated users
        if user and getattr(user, "is_authenticated", False):
            agent_map["portfolio"] = self.portfolio_agent
        else:
            # Still run but returns unauthenticated stub
            agent_map["portfolio"] = self.portfolio_agent

        with ThreadPoolExecutor(max_workers=_MAX_WORKERS) as executor:
            futures = {executor.submit(run, k, a): k for k, a in agent_map.items()}
            for future in as_completed(futures):
                try:
                    key, result = future.result(timeout=10)
                    results[key] = result
                except Exception as exc:
                    key = futures[future]
                    logger.warning(f"[Orchestrator] Agent {key} timed out or failed: {exc}")
                    results[key] = {"success": False, "error": str(exc)}

        return results

    # ── Private: No-Symbol Fallback ──────────────────────────────────────────

    def _handle_no_symbol(self, query: str, intent: str, user) -> dict:
        """Handle queries with no identifiable stock symbol."""

        if intent == "portfolio_review" and user and getattr(user, "is_authenticated", False):
            portfolio_data = self.portfolio_agent.safe_analyze("PORTFOLIO", user)
            return {
                "query": query,
                "symbol": None,
                "intent": intent,
                "intent_display": "Portfolio Review",
                "portfolio_impact": portfolio_data,
                "summary": "Here's your portfolio overview.",
                "reasoning": [portfolio_data.get("diversification_note", "")],
                "beginner_tip": portfolio_data.get("suggestion", ""),
                "final_recommendation": None,
                "confidence": portfolio_data.get("confidence_score", 50),
                "disclaimer": "⚠️ This is for educational purposes only, not financial advice.",
                "generated_by": "rule_based",
                "processing_time_ms": 0,
            }

        if intent == "market_overview":
            return self._market_overview_response(query)

        # Generic fallback
        return {
            "query": query,
            "symbol": None,
            "intent": intent,
            "intent_display": "General",
            "summary": (
                "I couldn't identify a specific stock in your query. "
                "Try asking something like 'Should I buy TCS?' or 'Analyse Infosys'."
            ),
            "reasoning": [],
            "beginner_tip": "You can ask about any NSE-listed stock by name or ticker symbol.",
            "final_recommendation": None,
            "confidence": 0,
            "disclaimer": "⚠️ This is for educational purposes only, not financial advice.",
            "generated_by": "rule_based",
            "processing_time_ms": 0,
        }

    def _market_overview_response(self, query: str) -> dict:
        """Return a market overview based on top signals."""
        try:
            from signals.models import Signal
            top_signals = Signal.objects.select_related("stock").order_by(
                "-confidence"
            )[:5]
            signal_list = [
                {
                    "symbol": s.stock.symbol,
                    "name": s.stock.name,
                    "type": s.signal_type,
                    "confidence": s.confidence,
                    "reason": s.reason,
                }
                for s in top_signals
            ]
            bullish = sum(1 for s in top_signals if s.signal_type == "bullish")
            bearish = sum(1 for s in top_signals if s.signal_type == "bearish")
            overall = "bullish" if bullish > bearish else ("bearish" if bearish > bullish else "mixed")
        except Exception:
            signal_list = []
            overall = "neutral"

        return {
            "query": query,
            "symbol": None,
            "intent": "market_overview",
            "intent_display": "Market Overview",
            "market_data": {"overall_sentiment": overall},
            "signals": {"active_signals": signal_list},
            "summary": f"The market is currently showing a **{overall}** bias based on active signals from our database.",
            "reasoning": [f"Top signals indicate {overall} market conditions today."],
            "beginner_tip": "Focus on quality large-cap stocks when the market is uncertain.",
            "final_recommendation": None,
            "confidence": 60,
            "disclaimer": "⚠️ This is for educational purposes only, not financial advice.",
            "generated_by": "rule_based",
            "processing_time_ms": 0,
        }

    # ── Private: Memory Persistence ──────────────────────────────────────────

    def _save_to_memory(
        self, user, query: str, symbol: str | None, intent: str, response: dict
    ) -> None:
        """Persist query + response to ChatQuery for history and memory."""
        try:
            from ai_engine.models import ChatQuery
            import json

            # Use the identified user or None
            actual_user = user if (user and getattr(user, "is_authenticated", False)) else None

            ChatQuery.objects.create(
                user=actual_user,
                query=query,
                symbol=symbol or "",
                intent=intent,
                confidence=response.get("confidence", 50),
                recommendation=response.get("final_recommendation", ""),
                response=json.dumps({
                    "summary": response.get("summary", ""),
                    "final_recommendation": response.get("final_recommendation"),
                    "confidence": response.get("confidence"),
                }),
            )
        except Exception as exc:
            # Memory save failure must never break the API response
            logger.warning(f"[Orchestrator] Failed to save memory: {exc}")
