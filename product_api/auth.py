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
from django_ratelimit.decorators import ratelimit
from django.utils.decorators import method_decorator
from .serializer import (CustomTokenObtainPairSerializer,
                         CustomTokenRefreshSerializer)


logger = logging.getLogger(__name__)

Users = get_user_model()


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    permission_classes = [permissions.AllowAny]

    @method_decorator(ratelimit(key='ip', rate='5/m', method='POST', block=True))
    @method_decorator(ratelimit(key='user_or_ip', rate='5/m', method='POST', block=True))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)


class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer
    permission_classes = [permissions.AllowAny]


class LogoutView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        try:
            refresh_token = request.data['refresh']
            token = RefreshToken(refresh_token)

            # Extract user_id from token payload
            user_id = token.payload.get('user_id')
            if user_id:
                try:
                    user = Users.objects.get(pk=user_id)
                    logger.info(f"User {user.username} logged out successfully")
                except Users.DoesNotExist:
                    logger.warning(f"Logout attempted with unknown user_id: {user_id}")
            else:
                logger.warning("Token missing user_id")

            # Blacklist the token
            token.blacklist()
            return Response(status=status.HTTP_205_RESET_CONTENT)

        except Exception as e:
            logger.error(f"Logout failed: {e}")
            return Response({"detail": "Invalid token"}, status=status.HTTP_400_BAD_REQUEST)


class RegisterView(generics.CreateAPIView):
    queryset = Users.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.AllowAny]

    def perform_create(self, serializer):
        user = serializer.save()
        logger.info(f"New user registered: {user.email}")
