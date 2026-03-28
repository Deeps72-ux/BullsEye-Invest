from rest_framework.views import APIView
from rest_framework.response import Response


class StockListView(APIView):
    def get(self, request):
        return Response({
            "stocks": ["RELIANCE", "TCS", "INFY"]
        })


class StockDetailView(APIView):
    def get(self, request, symbol):
        return Response({
            "symbol": symbol,
            "price": 2500,
            "change": "+1.2%"
        })


class FilingsView(APIView):
    def get(self, request):
        return Response({
            "filings": [
                {"company": "TCS", "type": "Quarterly Results"},
                {"company": "INFY", "type": "Insider Trade"}
            ]
        })