from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Alert
from accounts.models import User
from market_data.models import Stock
from django.utils.timesince import timesince


def _get_demo_user():
    try:
        return User.objects.get(username="demo")
    except User.DoesNotExist:
        return None


class AlertListView(APIView):
    def get(self, request):
        user = request.user if request.user.is_authenticated else _get_demo_user()
        if not user:
            return Response([])

        alerts = Alert.objects.filter(user=user).select_related("stock").order_by("-created_at")
        data = [
            {
                "id": a.id,
                "symbol": a.stock.symbol,
                "type": "Alert",
                "message": a.message,
                "timestamp": timesince(a.created_at) + " ago",
                "read": a.is_read,
            }
            for a in alerts
        ]
        return Response(data)


class SubscribeAlertView(APIView):
    def post(self, request):
        user = request.user if request.user.is_authenticated else _get_demo_user()
        if not user:
            return Response({"error": "Not authenticated"}, status=401)

        symbol = request.data.get("symbol", "").upper()
        message = request.data.get("message", f"Alert for {symbol}")
        try:
            stock = Stock.objects.get(symbol=symbol)
        except Stock.DoesNotExist:
            return Response({"error": f"Stock {symbol} not found"}, status=404)

        alert = Alert.objects.create(user=user, stock=stock, message=message, is_read=False)
        return Response({"message": "Alert created", "id": alert.id})


class MarkAlertReadView(APIView):
    def patch(self, request, alert_id):
        user = request.user if request.user.is_authenticated else _get_demo_user()
        if not user:
            return Response({"error": "Not authenticated"}, status=401)
        try:
            alert = Alert.objects.get(id=alert_id, user=user)
            alert.is_read = True
            alert.save()
            return Response({"message": "Marked as read"})
        except Alert.DoesNotExist:
            return Response({"error": "Not found"}, status=404)


class MarkAllAlertsReadView(APIView):
    def post(self, request):
        user = request.user if request.user.is_authenticated else _get_demo_user()
        if not user:
            return Response({"error": "Not authenticated"}, status=401)
        Alert.objects.filter(user=user).update(is_read=True)
        return Response({"message": "All alerts marked as read"})