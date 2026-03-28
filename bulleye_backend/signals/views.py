from rest_framework.views import APIView
from rest_framework.response import Response


class OpportunityRadarView(APIView):
    def get(self, request):
        return Response({
            "signals": [
                {
                    "stock": "RELIANCE",
                    "signal": "Breakout",
                    "confidence": 85
                }
            ]
        })


class StockSignalView(APIView):
    def get(self, request, symbol):
        return Response({
            "stock": symbol,
            "signal": "Bullish",
            "reason": "High volume + price breakout"
        })