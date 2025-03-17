import requests

from datetime import datetime

from django.conf import settings
from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.authentication import JWTAuthentication

from exchange.models import CurrencyExchange, UserBalance
from exchange.serializers import RegisterSerializer, CurrencyExchangeSerializer


class RegisterView(generics.CreateAPIView):
    """Register a new user"""
    queryset = get_user_model().objects.all()
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)


class CurrencyExchangeViewSet(viewsets.ModelViewSet):
    """Get currency rate from external API and save it to the database"""
    serializer_class = CurrencyExchangeSerializer
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def get_queryset(self):
        return CurrencyExchange.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Automatically assigns the user, fetches exchange rate,
        and checks balance before exchange"""
        user = self.request.user

        user_balance, created = UserBalance.objects.get_or_create(user=user)

        if user_balance.balance <= 0:
            raise ValidationError(
                {"error": "Insufficient balance to perform currency exchange"}
            )

        currency_code = self.request.data.get("currency_code")
        if not currency_code:
            raise ValidationError({"error": "Currency code is required"})

        # Request to exchange rate API
        api_url = f"{settings.EXCHANGE_RATE_API_URL}/{settings.EXCHANGE_RATE_API_KEY}/latest/{currency_code}"
        # print(f"📡 Sending request to: {api_url}")  # Add print in console

        response = requests.get(api_url)
        # print(f"📡 API Response: {response.status_code} - {response.text}")  # print in console

        if response.status_code != 200:
            raise ValidationError({"error": "Failed to fetch exchange rate"})

        data = response.json()
        rate = data.get("conversion_rates", {}).get("UAH")  # Hryvna`s rate

        if not rate:
            raise ValidationError({"error": "Invalid currency code"})

        # Saves data
        serializer.save(user=user, rate=rate)

        # Minus 1 from balance
        user_balance.balance -= 1
        user_balance.save()


class BalanceView(APIView):
    """Current user`s balance"""
    permission_classes = (permissions.IsAuthenticated,)
    authentication_classes = (JWTAuthentication,)

    def get(self, request):
        try:
            user_balance = UserBalance.objects.get(user=request.user)
        except UserBalance.DoesNotExist:
            user_balance = UserBalance.objects.create(
                user=request.user,
                balance=1000
            )

        return Response({"balance": user_balance.balance})


class CurrencyHistoryView(generics.ListAPIView):
    """Request history (filterable by currency and date)"""
    serializer_class = CurrencyExchangeSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        queryset = CurrencyExchange.objects.filter(user=self.request.user)
        currency = self.request.query_params.get("currency")
        date_str = self.request.query_params.get("date")

        if currency:
            queryset = queryset.filter(currency_code=currency)
        if date_str:
            try:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
                queryset = queryset.filter(created_at__date=date_obj)
            except ValueError:
                pass

        return queryset
