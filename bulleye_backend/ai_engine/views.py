"""
AI Engine — API Views

Endpoints:
  POST /api/ai/chat/          → OrchestratorAgent.handle_query()
  GET  /api/ai/explain/<sym>/ → OrchestratorAgent.analyze_stock()
  GET  /api/ai/history/       → ChatQuery history for authenticated user
"""

import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

logger = logging.getLogger(__name__)


class AIAdvisorChatView(APIView):
    """
    POST /api/ai/chat/

    Body:
        {
            "query": "Should I buy TCS?",
            "user_id": 1   // optional override for demo
        }

    Returns: full structured AI advisory response
    """

    def post(self, request):
        query = request.data.get("query", "").strip()

        if not query:
            return Response(
                {"error": "Query is required. Try: 'Should I buy TCS?'"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if len(query) > 1000:
            return Response(
                {"error": "Query too long. Max 1000 characters."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Resolve user (authenticated > demo user > None)
        user = _resolve_user(request)

        try:
            from ai_engine.agents.orchestrator import OrchestratorAgent
            orchestrator = OrchestratorAgent()
            result = orchestrator.handle_query(query=query, user=user)
            return Response(result, status=status.HTTP_200_OK)

        except Exception as exc:
            logger.error(f"[AIAdvisorChatView] Unexpected error: {exc}", exc_info=True)
            return Response(
                {
                    "error": "The AI advisor encountered an error. Please try again.",
                    "detail": str(exc),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class StockExplainView(APIView):
    """
    GET /api/ai/explain/<symbol>/

    Returns a full AI analysis for the given stock symbol.
    No query required — runs full agent pipeline for the symbol directly.
    """

    def get(self, request, symbol: str):
        symbol = symbol.upper().strip()

        if not symbol or len(symbol) > 20:
            return Response(
                {"error": "Invalid stock symbol."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = _resolve_user(request)

        try:
            from ai_engine.agents.orchestrator import OrchestratorAgent
            orchestrator = OrchestratorAgent()
            result = orchestrator.analyze_stock(symbol=symbol, user=user)

            if result.get("market_data", {}).get("not_found"):
                return Response(
                    {"error": f"Stock '{symbol}' not found in database."},
                    status=status.HTTP_404_NOT_FOUND,
                )

            return Response(result, status=status.HTTP_200_OK)

        except Exception as exc:
            logger.error(f"[StockExplainView] Error for {symbol}: {exc}", exc_info=True)
            return Response(
                {"error": "Analysis failed. Please try again."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class ChatHistoryView(APIView):
    """
    GET /api/ai/history/

    Returns the last 20 AI queries for the authenticated user.
    Supports ?symbol=TCS to filter by stock.
    """

    def get(self, request):
        user = _resolve_user(request)

        if not user:
            return Response(
                {"error": "Authentication required to access chat history."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            from ai_engine.models import ChatQuery
            import json

            qs = ChatQuery.objects.filter(user=user)

            # Optional symbol filter
            symbol_filter = request.query_params.get("symbol", "").upper().strip()
            if symbol_filter:
                qs = qs.filter(symbol=symbol_filter)

            qs = qs.order_by("-created_at")[:20]

            data = []
            for q in qs:
                try:
                    resp_preview = json.loads(q.response) if q.response else {}
                except Exception:
                    resp_preview = {}

                data.append({
                    "id": q.id,
                    "query": q.query,
                    "symbol": q.symbol,
                    "intent": q.intent,
                    "recommendation": q.recommendation,
                    "confidence": q.confidence,
                    "summary": resp_preview.get("summary", ""),
                    "created_at": q.created_at.isoformat(),
                })

            return Response({"count": len(data), "history": data})

        except Exception as exc:
            logger.error(f"[ChatHistoryView] Error: {exc}", exc_info=True)
            return Response(
                {"error": "Failed to load history."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# ── Helpers ──────────────────────────────────────────────────────────────────

def _resolve_user(request):
    """Resolve the user from JWT auth or fall back to demo user."""
    if request.user and getattr(request.user, "is_authenticated", False):
        return request.user

    # Fall back to demo user for unauthenticated requests
    try:
        from accounts.models import User
        return User.objects.filter(username="demo").first()
    except Exception:
        return None