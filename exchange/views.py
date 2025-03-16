from datetime import datetime

from django.contrib.auth import get_user_model
from django.shortcuts import render
from rest_framework import generics, permissions, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView

from exchange.models import CurrencyExchange, UserBalance
from exchange.serializers import RegisterSerializer, CurrencyExchangeSerializer


class RegisterView(generics.CreateAPIView):
    """Register a new user"""
    queryset = get_user_model().objects.all()
    serializer_class = RegisterSerializer
    permission_classes = (permissions.AllowAny,)


class CurrencyExchangeViewSet(viewsets.ModelViewSet):
    """Get currency rate and save it to the database"""
    serializer_class = CurrencyExchangeSerializer
    permission_classes = (permissions.IsAuthenticated,)
    # authentication_classes = (JWTAuthentication,)

    def get_queryset(self):
        return CurrencyExchange.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        """Automatically assigns the user
         and checks balance before exchange"""
        user_balance = UserBalance.objects.get(user=self.request.user)

        if user_balance.balance <= 0:
            raise ValidationError(
                {"error": "Insufficient balance to perform currency exchange"}
            )

        serializer.save(user=self.request.user)


class BalanceView(APIView):
    """Current user`s balance"""
    permission_classes = (permissions.IsAuthenticated,)
    # authentication_classes = (JWTAuthentication,)

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
                pass  # Просто ігноруємо помилку формату

        return queryset
