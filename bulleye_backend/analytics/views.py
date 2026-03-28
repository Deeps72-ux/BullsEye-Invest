from rest_framework.views import APIView
from rest_framework.response import Response


class PatternDetectionView(APIView):
    def get(self, request, symbol):
        return Response({
            "symbol": symbol,
            "pattern": "Ascending Triangle",
            "success_rate": "72%"
        })


class IndicatorView(APIView):
    def get(self, request, symbol):
        return Response({
            "symbol": symbol,
            "RSI": 68,
            "MACD": "Bullish"
        })


class BacktestView(APIView):
    def get(self, request, symbol):
        return Response({
            "symbol": symbol,
            "backtest_result": "Win rate: 65%"
        })