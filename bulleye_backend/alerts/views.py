from rest_framework.views import APIView
from rest_framework.response import Response


class AlertListView(APIView):
    def get(self, request):
        return Response({
            "alerts": [
                {"stock": "RELIANCE", "type": "Breakout Alert"}
            ]
        })


class SubscribeAlertView(APIView):
    def post(self, request):
        return Response({
            "message": "Subscribed successfully"
        })