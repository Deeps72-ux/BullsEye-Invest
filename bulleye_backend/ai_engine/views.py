from rest_framework.views import APIView
from rest_framework.response import Response


class MarketChatView(APIView):
    def post(self, request):
        query = request.data.get("query")

        return Response({
            "query": query,
            "answer": "This is an AI-generated market insight."
        })


class StockExplainView(APIView):
    def get(self, request, symbol):
        return Response({
            "stock": symbol,
            "explanation": "Stock is rising due to strong earnings and institutional buying."
        })