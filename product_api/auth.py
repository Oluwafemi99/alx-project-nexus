from rest_framework import generics
from rest_framework.views import APIView
from rest_framework_simplejwt.views import (TokenObtainPairView,
                                            TokenRefreshView)
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.response import Response
from rest_framework import permissions
from . serializer import UserSerializer
import logging


logger = logging.getLogger(__name__)

Users = get_user_model()


class CostomTokenObtainPairView(TokenObtainPairView):
    permission_classes = [permissions.AllowAny]


class CostomTokenRefreshView(TokenRefreshView):
    permission_classes = [permissions.AllowAny]


class LogoutView(APIView):
    def post(self, request):
        try:
            refresh_token = request.data['refresh']
            token = RefreshToken(refresh_token)
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)
        except Exception as e:
            logger.error(f"Logout failed: {e}")
            return Response({"detail": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(generics.CreateAPIView):
    queryset = Users.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]
