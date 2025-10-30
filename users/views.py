from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from social_django.utils import load_strategy, load_backend
from social_core.exceptions import MissingBackend, AuthException

class OAuthLoginView(APIView):
    """
    Authenticate via OAuth and issue a JWT token.
    """

    def post(self, request, backend):
        strategy = load_strategy(request)
        try:
            # Load the backend
            backend_instance = load_backend(strategy, backend, None)
        except MissingBackend:
            return Response({'error': f"Backend '{backend}' not found."}, status=status.HTTP_400_BAD_REQUEST)

        # Get the access token from the request
        access_token = request.data.get('access_token')
        if not access_token:
            return Response({'error': 'Access token is required.'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Authenticate the user
            user = backend_instance.do_auth(access_token)
            if user and user.is_active:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                })
            else:
                return Response({'error': 'Authentication failed.'}, status=status.HTTP_401_UNAUTHORIZED)
        except AuthException as e:
            return Response({'error': f"Authentication error: {str(e)}"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': f"Unexpected error: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework.permissions import AllowAny
from .models import Client, AppUser

class ClientTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token['role'] = 'client'
        token['email'] = user.email
        return token

class ClientTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = ClientTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        request.data['username_field'] = 'email'  # Specify email as the username field
        return super().post(request, *args, **kwargs)


class AppUserTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        # Add custom claims
        token['role'] = 'app_user'
        token['email'] = user.email
        return token

class AppUserTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]
    serializer_class = AppUserTokenObtainPairSerializer

    def post(self, request, *args, **kwargs):
        request.data['username_field'] = 'email'  # Specify email as the username field
        return super().post(request, *args, **kwargs)
