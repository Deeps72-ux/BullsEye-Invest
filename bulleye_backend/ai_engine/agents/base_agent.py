"""
Base Agent — Abstract interface for all BullsEye AI agents.

Every specialized agent inherits from BaseAgent to guarantee:
  - A consistent `analyze()` interface
  - Shared confidence scoring helpers
  - Standardized error wrapping so one agent failure never crashes the orchestrator
"""

from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class AgentError(Exception):
    """Raised when an agent encounters an unrecoverable error."""
    pass


class BaseAgent(ABC):
    """Abstract base for all BullsEye specialized agents."""

    # Subclasses override this for logging context
    agent_name: str = "BaseAgent"

    @abstractmethod
    def analyze(self, symbol: str, user=None) -> dict:
        """
        Run the agent's analysis for the given stock symbol.

        Args:
            symbol: NSE stock symbol (e.g. "TCS", "INFY")
            user: Django User object (optional, for portfolio-aware agents)

        Returns:
            dict with agent-specific keys plus `agent_name` and `success` flag
        """
        raise NotImplementedError

    def safe_analyze(self, symbol: str, user=None) -> dict:
        """
        Wraps analyze() in a try/except so orchestrator always gets a dict back.
        On failure returns a graceful error dict instead of raising.
        """
        try:
            result = self.analyze(symbol, user)
            result.setdefault("agent_name", self.agent_name)
            result.setdefault("success", True)
            return result
        except Exception as exc:
            logger.warning(f"[{self.agent_name}] Failed for {symbol}: {exc}")
            return {
                "agent_name": self.agent_name,
                "success": False,
                "error": str(exc),
            }

    # ── Confidence Helpers ──────────────────────────────────────────────────

    @staticmethod
    def clamp_confidence(value: float) -> int:
        """Clamp confidence to integer in [0, 100]."""
        return max(0, min(100, int(round(value))))

    @staticmethod
    def score_to_label(score: int) -> str:
        """Convert a 0-100 confidence score to a human label."""
        if score >= 80:
            return "Very High"
        elif score >= 65:
            return "High"
        elif score >= 50:
            return "Moderate"
        elif score >= 35:
            return "Low"
        else:
            return "Very Low"

    @staticmethod
    def combine_confidences(*scores: float, weights=None) -> int:
        """
        Weighted average of multiple confidence scores.
        If weights is None, uses equal weighting.
        """
        valid = [(s, w) for s, w in zip(scores, weights or [1] * len(scores))
                 if s is not None]
        if not valid:
            return 50
        total_weight = sum(w for _, w in valid)
        weighted_sum = sum(s * w for s, w in valid)
        return BaseAgent.clamp_confidence(weighted_sum / total_weight)
