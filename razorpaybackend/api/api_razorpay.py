from rest_framework.views import APIView
from rest_framework import status
from .razorpay_serializers import CreateOrderSerializer, BuyProductSerializer
from rest_framework.response import Response
from razorpaybackend.api.razorpay.main import RazorpayClient, client
from rest_framework.permissions import IsAuthenticated
rz_client = RazorpayClient()

class CreateOrderAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = CreateOrderSerializer(data=request.data)

        if serializer.is_valid():
            amount = serializer.validated_data.get("amount")
            currency = serializer.validated_data.get("currency")

            order_response = rz_client.create_order(
                amount=amount,
                currency=currency
            )

            response = {
                'status_code': status.HTTP_201_CREATED,
                'message': 'order_created',
                'data': order_response
            }
            return Response(response, status=status.HTTP_201_CREATED)
        else:
            response = {
                "status_code": status.HTTP_400_BAD_REQUEST,
                "message": "bad_request",
                "error": serializer.errors
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
        
        
    

class TransactionAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        user = request.user
        request.data['buyer'] = user.id
        request.data['amount'] = request.data['amount'] / 100
        transaction_serializer = BuyProductSerializer(data=request.data)

        if transaction_serializer.is_valid():
            rz_client.verify_payment(
                razorpay_order_id=transaction_serializer.validated_data.get('order_id'),
                razorpay_payment_id=transaction_serializer.validated_data.get('payment_id'),
                razorpay_signature_id=transaction_serializer.validated_data.get('signature')
            )
            transaction_serializer.save()
            return Response({transaction_serializer.data}, status=status.HTTP_201_CREATED)
        else:
            return Response(transaction_serializer.errors, status=status.HTTP_400_BAD_REQUEST)