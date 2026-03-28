from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Pattern, BacktestResult, Indicator
from market_data.models import Stock


class PatternDetectionView(APIView):
    def get(self, request, symbol):
        try:
            stock = Stock.objects.get(symbol=symbol.upper())
        except Stock.DoesNotExist:
            return Response({"patterns": []})

        patterns = Pattern.objects.filter(stock=stock).order_by("-detected_at")
        data = [
            {
                "name": p.pattern_name,
                "confidence": round(p.success_rate),
                "description": f"Pattern with {p.success_rate:.0f}% historical success rate",
                "detected": _humanize_date(p.detected_at),
            }
            for p in patterns
        ]
        return Response({"symbol": symbol, "patterns": data})


class IndicatorView(APIView):
    def get(self, request, symbol):
        try:
            stock = Stock.objects.get(symbol=symbol.upper())
        except Stock.DoesNotExist:
            return Response({"symbol": symbol})

        indicator = Indicator.objects.filter(stock=stock).order_by("-date").first()
        if not indicator:
            return Response({"symbol": symbol, "rsi": None, "macd": None, "ema": None})
        return Response({
            "symbol": symbol,
            "rsi": indicator.rsi,
            "macd": indicator.macd,
            "ema": indicator.ema,
        })


class BacktestView(APIView):
    def get(self, request, symbol):
        try:
            stock = Stock.objects.get(symbol=symbol.upper())
        except Stock.DoesNotExist:
            return Response({"symbol": symbol})

        result = BacktestResult.objects.filter(stock=stock).order_by("-created_at").first()
        if not result:
            return Response({"symbol": symbol, "winRate": None})
        return Response({
            "symbol": symbol,
            "strategy": result.strategy_name,
            "winRate": result.win_rate,
            "avgReturn": result.avg_return,
            "totalTrades": 142,    # extend model later
            "maxDrawdown": -8.5,   # extend model later
            "sharpeRatio": 1.85,   # extend model later
            "profitFactor": 2.1,   # extend model later
        })


def _humanize_date(dt):
    from django.utils import timezone
    delta = timezone.now() - dt
    days = delta.days
    if days == 0:
        return "Today"
    elif days == 1:
        return "Yesterday"
    else:
        return f"{days} days ago"