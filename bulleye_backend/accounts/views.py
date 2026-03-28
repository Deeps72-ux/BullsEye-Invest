from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from accounts.models import User


def _get_tokens(user):
    refresh = RefreshToken.for_user(user)
    return {
        "token": str(refresh.access_token),
        "refresh": str(refresh),
    }


class RegisterView(APIView):
    def post(self, request):
        username = request.data.get("username") or request.data.get("email", "").split("@")[0]
        email = request.data.get("email", "")
        password = request.data.get("password", "")
        name = request.data.get("name", "")

        if User.objects.filter(username=username).exists():
            return Response({"error": "User already exists"}, status=400)

        first, *last = name.split(" ") if name else [username]
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first,
            last_name=" ".join(last),
        )
        return Response({"message": "Account created", **_get_tokens(user)}, status=201)


class LoginView(APIView):
    def post(self, request):
        # Support both { username, password } and { email, password }
        username = request.data.get("username") or request.data.get("email", "")
        password = request.data.get("password", "")

        # Try email lookup first
        if "@" in username:
            try:
                user_obj = User.objects.get(email=username)
                username = user_obj.username
            except User.DoesNotExist:
                pass

        user = authenticate(username=username, password=password)
        if user:
            return Response({
                "message": "Login successful",
                "user_id": user.id,
                **_get_tokens(user),
            })
        return Response({"error": "Invalid credentials"}, status=401)


class ProfileView(APIView):
    def get(self, request):
        user = request.user
        if not user.is_authenticated:
            # Fallback to demo user
            try:
                user = User.objects.get(username="demo")
            except User.DoesNotExist:
                return Response({"error": "Not authenticated"}, status=401)
        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "firstName": user.first_name,
            "lastName": user.last_name,
            "riskProfile": user.risk_profile,
            "preferredSectors": user.preferred_sectors,
        })