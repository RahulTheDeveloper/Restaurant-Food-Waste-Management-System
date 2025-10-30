from django.urls import path, include
from .views import RawMaterialUploadView, MenuApiView, ListMenuView, ListRawMaterialView, RestaurantTransactionHistoryView, AppUserTransactionView, ListAppUserMenuView

urlpatterns = [
    path("save-excel-data/", RawMaterialUploadView.as_view()),
    
    path('create-menu/',MenuApiView.as_view()),
    path('update-menu/',MenuApiView.as_view()),
    
    path('list-menu/',ListMenuView.as_view()),
    path('list-app-menu-view/',ListAppUserMenuView.as_view()),
    
    path('list-raw-material/',ListRawMaterialView.as_view()),
    
    path('restaurant-transaction-history/', RestaurantTransactionHistoryView.as_view()),
    path('appuser-transaction-history/', AppUserTransactionView.as_view())

]