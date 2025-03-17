"""
URL configuration for Exchange_Rate_API project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.urls import path, include
from rest_framework import routers
from exchange.views import (
    CurrencyExchangeViewSet,
    RegisterView,
    CurrencyHistoryView,
    BalanceView
)

router = routers.DefaultRouter()
router.register(r"currency", CurrencyExchangeViewSet, basename="currency")

urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("history/", CurrencyHistoryView.as_view(), name="history"),
    path("balance/", BalanceView.as_view(), name="balance"),
    path("", include(router.urls)),
    path("user/", include("exchange.urls")),
]
