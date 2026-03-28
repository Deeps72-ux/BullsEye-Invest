from rest_framework.views import APIView
from rest_framework.response import Response


class DashboardView(APIView):
    def get(self, request):
        return Response({
            "top_signals": ["RELIANCE Breakout"],
            "portfolio_summary": "Up 12%"
        })


class GlobalSearchView(APIView):
    def get(self, request):
        query = request.GET.get("q")
        return Response({
            "query": query,
            "results": ["TCS", "Infosys", "HDFC"]
        })