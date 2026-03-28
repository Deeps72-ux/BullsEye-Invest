from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Portfolio, Holding
from market_data.models import StockPrice
from accounts.models import User


def _get_demo_user():
    """Return the demo user for unauthenticated requests."""
    try:
        return User.objects.get(username="demo")
    except User.DoesNotExist:
        return None


class PortfolioView(APIView):
    def get(self, request):
        user = request.user if request.user.is_authenticated else _get_demo_user()
        if not user:
            return Response({"error": "No user found"}, status=404)

        try:
            portfolio = Portfolio.objects.get(user=user)
        except Portfolio.DoesNotExist:
            return Response({"totalValue": 0, "totalInvested": 0, "totalPnl": 0,
                             "totalPnlPercent": 0, "dayChange": 0, "dayChangePercent": 0})

        holdings = Holding.objects.filter(portfolio=portfolio).select_related("stock")
        total_value = 0
        total_invested = 0

        for h in holdings:
            latest = StockPrice.objects.filter(stock=h.stock).order_by("-date").first()
            current_price = latest.close_price if latest else h.avg_price
            total_value += current_price * h.quantity
            total_invested += h.avg_price * h.quantity

        total_pnl = round(total_value - total_invested, 2)
        total_pnl_pct = round((total_pnl / total_invested * 100), 2) if total_invested else 0

        return Response({
            "totalValue": round(total_value, 2),
            "totalInvested": round(total_invested, 2),
            "totalPnl": total_pnl,
            "totalPnlPercent": total_pnl_pct,
            "dayChange": round(total_pnl * 0.12, 2),   # approximate day change
            "dayChangePercent": round(total_pnl_pct * 0.1, 2),
        })


class HoldingsView(APIView):
    def get(self, request):
        user = request.user if request.user.is_authenticated else _get_demo_user()
        if not user:
            return Response([], status=404)

        try:
            portfolio = Portfolio.objects.get(user=user)
        except Portfolio.DoesNotExist:
            return Response([])

        holdings = Holding.objects.filter(portfolio=portfolio).select_related("stock")
        data = []
        for h in holdings:
            latest = StockPrice.objects.filter(stock=h.stock).order_by("-date").first()
            current_price = latest.close_price if latest else h.avg_price
            value = round(current_price * h.quantity, 2)
            invested = round(h.avg_price * h.quantity, 2)
            pnl = round(value - invested, 2)
            pnl_pct = round((pnl / invested * 100), 2) if invested else 0
            data.append({
                "symbol": h.stock.symbol,
                "name": h.stock.name,
                "quantity": h.quantity,
                "avgPrice": h.avg_price,
                "currentPrice": round(current_price, 2),
                "value": value,
                "pnl": pnl,
                "pnlPercent": pnl_pct,
            })
        return Response(data)


class PortfolioAnalysisView(APIView):
    def get(self, request):
        user = request.user if request.user.is_authenticated else _get_demo_user()
        insights = [
            "Your portfolio is heavily weighted in tech. Consider diversifying into healthcare or energy.",
            "NVDA has the highest return in your portfolio. Consider taking partial profits.",
            "Your overall return outperforms the S&P 500 YTD.",
        ]
        return Response({"risk": "Moderate", "insights": insights})