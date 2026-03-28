from rest_framework.views import APIView
from rest_framework.response import Response


class PortfolioView(APIView):
    def get(self, request):
        return Response({
            "total_value": 500000,
            "returns": "12%"
        })


class HoldingsView(APIView):
    def get(self, request):
        return Response({
            "holdings": [
                {"stock": "TCS", "qty": 10},
                {"stock": "INFY", "qty": 15}
            ]
        })


class PortfolioAnalysisView(APIView):
    def get(self, request):
        return Response({
            "risk": "Moderate",
            "suggestion": "Diversify into banking sector"
        })