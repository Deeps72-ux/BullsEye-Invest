from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from .models import Stock, StockPrice, Filing


class StockListView(APIView):
    def get(self, request):
        query = request.query_params.get("q", "").strip()
        stocks = Stock.objects.all()
        if query:
            stocks = stocks.filter(symbol__icontains=query) | stocks.filter(name__icontains=query)

        data = []
        for stock in stocks:
            # Get latest price entry
            latest = StockPrice.objects.filter(stock=stock).order_by("-date").first()
            prev = StockPrice.objects.filter(stock=stock).order_by("-date")[1:2]
            prev = prev[0] if prev else None

            price = latest.close_price if latest else 0
            prev_price = prev.close_price if prev else price
            change = round(price - prev_price, 2)
            change_pct = round((change / prev_price * 100), 2) if prev_price else 0
            volume = latest.volume if latest else 0

            data.append({
                "symbol": stock.symbol,
                "name": stock.name,
                "sector": stock.sector,
                "price": price,
                "change": change,
                "changePercent": change_pct,
                "volume": f"{volume / 1_000_000:.1f}M" if volume else "N/A",
                "marketCap": "N/A",
            })
        return Response(data)


class StockDetailView(APIView):
    def get(self, request, symbol):
        try:
            stock = Stock.objects.get(symbol=symbol.upper())
        except Stock.DoesNotExist:
            raise Http404

        latest = StockPrice.objects.filter(stock=stock).order_by("-date").first()
        prev = StockPrice.objects.filter(stock=stock).order_by("-date")[1:2]
        prev = prev[0] if prev else None

        price = latest.close_price if latest else 0
        prev_price = prev.close_price if prev else price
        change = round(price - prev_price, 2)
        change_pct = round((change / prev_price * 100), 2) if prev_price else 0
        volume = latest.volume if latest else 0

        # 30-day price history for chart
        history = StockPrice.objects.filter(stock=stock).order_by("date")[:30]
        chart_data = [
            {
                "date": sp.date.strftime("%b %-d"),
                "price": round(sp.close_price, 2),
                "volume": round(sp.volume / 1_000_000, 1),
            }
            for sp in history
        ]

        return Response({
            "symbol": stock.symbol,
            "name": stock.name,
            "sector": stock.sector,
            "price": price,
            "change": change,
            "changePercent": change_pct,
            "volume": f"{volume / 1_000_000:.1f}M" if volume else "N/A",
            "marketCap": "N/A",
            "chartData": chart_data,
        })


class FilingsView(APIView):
    def get(self, request):
        filings = Filing.objects.select_related("stock").order_by("-created_at")
        data = [
            {
                "company": f.stock.name,
                "symbol": f.stock.symbol,
                "type": f.filing_type,
                "date": f.created_at.strftime("%b %-d, %Y"),
                "description": f.description,
            }
            for f in filings
        ]
        return Response(data)