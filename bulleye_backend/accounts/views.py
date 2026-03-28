from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class RegisterView(APIView):
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        if User.objects.filter(username=username).exists():
            return Response({"error": "User already exists"}, status=400)

        user = User.objects.create_user(username=username, password=password)
        return Response({"message": "User created", "user_id": user.id})


class LoginView(APIView):
    def post(self, request):
        user = authenticate(
            username=request.data.get("username"),
            password=request.data.get("password"),
        )
        if user:
            return Response({"message": "Login successful", "user_id": user.id})
        return Response({"error": "Invalid credentials"}, status=401)


class ProfileView(APIView):
    def get(self, request):
        return Response({
            "user": "demo_user",
            "risk_profile": "moderate"
        })