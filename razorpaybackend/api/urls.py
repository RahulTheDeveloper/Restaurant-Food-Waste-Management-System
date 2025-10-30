from django.urls import path
from .api_razorpay import CreateOrderAPIView, TransactionAPIView

urlpatterns = [
    path("order/create/",CreateOrderAPIView.as_view()),
    path('order/complete/',TransactionAPIView.as_view())
]
