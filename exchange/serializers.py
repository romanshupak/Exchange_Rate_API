from django.contrib.auth import get_user_model
from rest_framework import serializers

from exchange.models import UserBalance, CurrencyExchange


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=5)

    class Meta:
        model = get_user_model()
        fields = ("id", "username", "email", "password")
        read_only_fields = ("id",)

    def create(self, validated_data):
        user = get_user_model().objects.create_user(**validated_data)
        UserBalance.objects.create(user=user)  # add balance
        return user


class CurrencyExchangeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CurrencyExchange
        fields = ("id", "user", "currency_code", "rate", "created_at")
        read_only_fields = ("id", "user", "rate", "created_at")

