from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Signal
from market_data.models import Stock


class OpportunityRadarView(APIView):
    def get(self, request):
        signals = Signal.objects.select_related("stock").order_by("-confidence")
        data = [
            {
                "id": sig.id,
                "symbol": sig.stock.symbol,
                "name": sig.stock.name,
                "type": sig.signal_type.capitalize(),
                "confidence": sig.confidence,
                "reason": sig.reason,
                "tags": _extract_tags(sig.reason),
                "createdAt": sig.created_at.isoformat(),
            }
            for sig in signals
        ]
        return Response(data)


class StockSignalView(APIView):
    def get(self, request, symbol):
        try:
            stock = Stock.objects.get(symbol=symbol.upper())
        except Stock.DoesNotExist:
            return Response({"signals": []})

        signals = Signal.objects.filter(stock=stock).order_by("-created_at")
        data = [
            {
                "id": sig.id,
                "symbol": sig.stock.symbol,
                "name": sig.stock.name,
                "type": sig.signal_type.capitalize(),
                "confidence": sig.confidence,
                "reason": sig.reason,
                "tags": _extract_tags(sig.reason),
                "createdAt": sig.created_at.isoformat(),
            }
            for sig in signals
        ]
        return Response(data)


def _extract_tags(reason: str) -> list:
    """Simple keyword tag extraction from reason text."""
    keywords = {
        "breakout": "Breakout",
        "volume": "High Volume",
        "golden cross": "Golden Cross",
        "institutional": "Institutional",
        "pattern": "Pattern",
        "earnings": "Earnings Beat",
        "growth": "Growth",
        "ai": "AI Play",
        "support": "Support",
        "rsi": "RSI",
        "macd": "MACD",
        "diverging": "Diverging",
    }
    lower = reason.lower()
    return list({v for k, v in keywords.items() if k in lower})[:3]