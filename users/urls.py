from django.contrib import admin
from django.urls import path, include
from .views import OAuthLoginView

from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import ClientTokenObtainPairView, AppUserTokenObtainPairView


urlpatterns = [
    path('auth/<str:backend>/', OAuthLoginView.as_view(), name='oauth_login'),
    
    path('token/client/', ClientTokenObtainPairView.as_view(), name='client_token_obtain_pair'),
    path('token/refresh/client/', TokenRefreshView.as_view(), name='client_token_refresh'),

    # AppUser Authentication
    path('token/appuser/', AppUserTokenObtainPairView.as_view(), name='appuser_token_obtain_pair'),
    path('token/refresh/appuser/', TokenRefreshView.as_view(), name='appuser_token_refresh'),

]
