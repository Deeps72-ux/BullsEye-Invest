"""
Portfolio Agent — Analyzes user holdings and calculates portfolio impact.

Queries:
  - Portfolio + Holding models (portfolio app)
  - StockPrice for current valuations

Output keys:
  already_holds        : bool — is the queried stock in user's portfolio?
  current_quantity     : shares held (int, 0 if not held)
  avg_buy_price        : user's average buy price (float | None)
  current_value        : current value of existing holding (float)
  unrealized_pnl       : P&L on existing holding (float)
  unrealized_pnl_pct   : % P&L (float)
  exposure_percent     : % of total portfolio in this stock (float)
  concentration_risk   : "high" | "moderate" | "low" (>20%, 10-20%, <10%)
  total_portfolio_value: total portfolio value (float)
  sector_exposure      : dict of sector → % allocation
  risk_level           : overall portfolio risk (str)
  suggestion           : position sizing / action suggestion (str)
  diversification_note : plain-English note for beginner (str)
  confidence_score     : 0-100 (int)
"""

import logging
from .base_agent import BaseAgent

logger = logging.getLogger(__name__)


class PortfolioAgent(BaseAgent):
    agent_name = "PortfolioAgent"

    def analyze(self, symbol: str, user=None) -> dict:
        from portfolio.models import Portfolio, Holding
        from market_data.models import Stock, StockPrice

        symbol = symbol.upper().strip()

        if user is None or not getattr(user, "is_authenticated", False):
            return self._no_user(symbol)

        # ── Resolve portfolio ────────────────────────────────────────────────
        try:
            portfolio = Portfolio.objects.get(user=user)
        except Portfolio.DoesNotExist:
            return self._no_portfolio(symbol, user)

        holdings = list(
            Holding.objects.filter(portfolio=portfolio).select_related("stock")
        )

        # ── Calculate total portfolio value ──────────────────────────────────
        total_value = 0.0
        sector_buckets: dict[str, float] = {}

        for h in holdings:
            latest = (
                StockPrice.objects.filter(stock=h.stock).order_by("-date").first()
            )
            price = latest.close_price if latest else h.avg_price
            val = price * h.quantity
            total_value += val
            sector = h.stock.sector or "Other"
            sector_buckets[sector] = sector_buckets.get(sector, 0.0) + val

        # ── Target stock holding ─────────────────────────────────────────────
        target_stock_obj = None
        try:
            target_stock_obj = Stock.objects.get(symbol=symbol)
        except Stock.DoesNotExist:
            pass

        holding = None
        if target_stock_obj:
            holding = next(
                (h for h in holdings if h.stock.symbol == symbol), None
            )

        already_holds = holding is not None
        current_quantity = holding.quantity if holding else 0
        avg_buy_price = holding.avg_price if holding else None

        current_price = 0.0
        if target_stock_obj:
            latest_target = (
                StockPrice.objects.filter(stock=target_stock_obj)
                .order_by("-date")
                .first()
            )
            current_price = latest_target.close_price if latest_target else 0.0

        current_value = round(current_price * current_quantity, 2)
        invested = round((avg_buy_price or 0) * current_quantity, 2)
        unrealized_pnl = round(current_value - invested, 2)
        unrealized_pnl_pct = (
            round(unrealized_pnl / invested * 100, 2) if invested else 0.0
        )

        # ── Exposure ─────────────────────────────────────────────────────────
        exposure_percent = (
            round(current_value / total_value * 100, 2) if total_value > 0 else 0.0
        )

        if exposure_percent > 20:
            concentration_risk = "high"
        elif exposure_percent > 10:
            concentration_risk = "moderate"
        else:
            concentration_risk = "low"

        # Sector exposure %
        sector_exposure = {
            s: round(v / total_value * 100, 1) if total_value > 0 else 0.0
            for s, v in sector_buckets.items()
        }

        # Overall portfolio risk heuristic
        num_stocks = len(holdings)
        top_sector_pct = max(sector_exposure.values()) if sector_exposure else 0
        if num_stocks < 4 or top_sector_pct > 50:
            risk_level = "High"
        elif num_stocks < 8 or top_sector_pct > 35:
            risk_level = "Moderate"
        else:
            risk_level = "Low"

        # ── Action suggestion ────────────────────────────────────────────────
        suggestion = _suggest_action(
            already_holds, exposure_percent, unrealized_pnl_pct, risk_level
        )
        diversification_note = _diversification_note(
            sector_exposure, num_stocks, top_sector_pct
        )

        confidence_score = 85 if already_holds else 70

        return {
            "symbol": symbol,
            "already_holds": already_holds,
            "current_quantity": current_quantity,
            "avg_buy_price": avg_buy_price,
            "current_price": round(current_price, 2),
            "current_value": current_value,
            "unrealized_pnl": unrealized_pnl,
            "unrealized_pnl_pct": unrealized_pnl_pct,
            "exposure_percent": exposure_percent,
            "concentration_risk": concentration_risk,
            "total_portfolio_value": round(total_value, 2),
            "sector_exposure": sector_exposure,
            "num_holdings": num_stocks,
            "risk_level": risk_level,
            "suggestion": suggestion,
            "diversification_note": diversification_note,
            "confidence_score": confidence_score,
        }

    def _no_user(self, symbol: str) -> dict:
        return {
            "symbol": symbol,
            "already_holds": False,
            "current_quantity": 0,
            "avg_buy_price": None,
            "current_price": 0.0,
            "current_value": 0.0,
            "unrealized_pnl": 0.0,
            "unrealized_pnl_pct": 0.0,
            "exposure_percent": 0.0,
            "concentration_risk": "unknown",
            "total_portfolio_value": 0.0,
            "sector_exposure": {},
            "num_holdings": 0,
            "risk_level": "Unknown",
            "suggestion": "Log in to get personalized portfolio analysis.",
            "diversification_note": "Sign in to see your portfolio's diversity score.",
            "confidence_score": 0,
            "unauthenticated": True,
        }

    def _no_portfolio(self, symbol: str, user) -> dict:
        return {
            "symbol": symbol,
            "already_holds": False,
            "current_quantity": 0,
            "avg_buy_price": None,
            "current_price": 0.0,
            "current_value": 0.0,
            "unrealized_pnl": 0.0,
            "unrealized_pnl_pct": 0.0,
            "exposure_percent": 0.0,
            "concentration_risk": "low",
            "total_portfolio_value": 0.0,
            "sector_exposure": {},
            "num_holdings": 0,
            "risk_level": "Unknown",
            "suggestion": f"You don't have a portfolio yet. Consider allocating 5-8% of your capital to {symbol} as a starter position.",
            "diversification_note": "Building a diversified portfolio of 10-15 Indian stocks across 4-5 sectors is a solid foundation.",
            "confidence_score": 50,
        }


def _suggest_action(
    already_holds: bool,
    exposure_pct: float,
    pnl_pct: float,
    risk_level: str,
) -> str:
    if not already_holds:
        if risk_level == "High":
            return "Your portfolio is concentrated. Add this stock cautiously — limit to 3-5% allocation."
        return "You don't hold this stock. If the signals are compelling, consider a 5-10% allocation of your investable capital."

    # Already holds
    if exposure_pct > 25:
        return f"You already have {exposure_pct:.1f}% of your portfolio in this stock — that's high. Consider trimming to below 20%."
    if pnl_pct > 30:
        return f"You're up {pnl_pct:.1f}% on this position. Consider booking partial profits (sell 30-50% of holding)."
    if pnl_pct < -20:
        return f"You're down {pnl_pct:.1f}% on this position. Reassess fundamentals before averaging down."
    return f"Your current position looks healthy at {exposure_pct:.1f}% portfolio weight. Hold and monitor."


def _diversification_note(
    sector_exposure: dict, num_stocks: int, top_sector_pct: float
) -> str:
    if num_stocks == 0:
        return "Start with 5-10 stocks across different sectors like IT, Banking, FMCG, and Pharma."
    if top_sector_pct > 50:
        top_sector = max(sector_exposure.items(), key=lambda x: x[1])[0]
        return f"Your portfolio is {top_sector_pct:.0f}% in {top_sector}. Diversify into other sectors to reduce risk."
    if num_stocks < 5:
        return f"You have {num_stocks} stocks. Aim for 10-15 stocks across 4-5 sectors for better risk management."
    return f"Your {num_stocks}-stock portfolio across {len(sector_exposure)} sectors looks reasonably diversified."
