from django.contrib import admin
from .models import Transaction
# Register your models here.





@admin.register(Transaction)
class Transaction(admin.ModelAdmin):
    list_display = ['id','payment_id','order_id','signature','amount']
    
    