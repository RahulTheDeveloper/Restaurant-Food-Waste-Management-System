from django.contrib import admin
from .models import Transaction

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = (
        'id', 
        'buyer', 
        'seller', 
        'food_item_name', 
        'quantity', 
        'amount', 
        'payment_method', 
        'status', 
        'created_at'
    )
    list_filter = ('status', 'payment_method', 'food_item_type', 'created_at')
    search_fields = (
        'food_item_name', 
        'payment_id', 
        'order_id', 
        'signature', 
        'buyer__name', 
        'seller__name'
    )
    ordering = ('-created_at',)
    readonly_fields = ('created_at',)
    fieldsets = (
        ('Transaction Details', {
            'fields': (
                'buyer', 
                'seller', 
                'food_item_type', 
                'food_item_id', 
                'food_item_name', 
                'quantity', 
                'amount'
            ),
        }),
        ('Payment Details', {
            'fields': (
                'payment_id', 
                'order_id', 
                'signature', 
                'payment_method'
            ),
        }),
        ('Status & Timestamps', {
            'fields': (
                'status', 
                'created_at'
            ),
        }),
    )
