from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    pass


class UserBalance(models.Model):
    """Stores user balance"""
    user = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)
    balance = models.IntegerField(default=1000)


class CurrencyExchange(models.Model):
    """Stores exchange rates linked to a user"""
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    currency_code = models.CharField(max_length=10)
    rate = models.DecimalField(max_digits=10, decimal_places=4)
    created_at = models.DateTimeField(auto_now_add=True)
