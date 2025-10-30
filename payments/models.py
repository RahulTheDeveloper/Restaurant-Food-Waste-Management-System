from django.db import models
from django.utils.timezone import now
import razorpay
from django.db import models, transaction
from django.core.exceptions import ValidationError

class Transaction(models.Model):
    TRANSACTION_STATUS = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]

    id = models.AutoField(primary_key=True)
    buyer = models.ForeignKey('users.AppUser', on_delete=models.CASCADE, related_name="transactions")
    seller = models.ForeignKey('users.Client', on_delete=models.CASCADE, related_name="transactions")
    food_item_type = models.CharField(
        max_length=50,
        choices=[
            ('raw_material', 'Raw Material'),
            ('restaurant_menu', 'Restaurant Menu'),
            ('packaged_food', 'Packaged Food'),
        ],
        help_text="Type of food item being sold"
    )
    food_item_id = models.CharField(max_length=255, help_text="Name of the sold food item")
    food_item_name = models.CharField(max_length=255, help_text="Name of the sold food item")
    quantity = models.FloatField(help_text="Quantity sold (kg or units)")
    amount = models.DecimalField(max_digits=10, decimal_places=2, help_text="Total price")
    payment_id = models.CharField(max_length=100, unique=True, help_text="Payment Gateway Transaction ID")
    order_id = models.CharField(max_length=100, unique=True, help_text="Payment Gateway Order ID")
    signature = models.CharField(max_length=100, unique=True, help_text="Payment Gateway signature ID")
    payment_method = models.CharField(
        max_length=50,
        choices=[('upi', 'UPI'), ('paypal', 'PayPal'), ('card', 'Credit/Debit Card')],
        help_text="Payment method used"
    )
    status = models.CharField(max_length=50, choices=TRANSACTION_STATUS, default='completed', help_text="Transaction status", null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.food_item_name} sold by {self.seller.email} to {self.buyer.email}"
    
    def save(self, *args, **kwargs):
        from stock.models import RestaurantMenu  # Assuming the menu item model is in `restaurant.models`

        if self.food_item_type == 'restaurant_menu':
            try:
                with transaction.atomic():
                    menu_item = RestaurantMenu.objects.select_for_update().get(id=self.food_item_id)
                    if menu_item.weight < self.quantity:
                        raise ValidationError(f"Not enough stock for {menu_item.name}. Available: {menu_item.weight}, Requested: {self.quantity}")
                    menu_item.weight -= self.quantity
                    menu_item.save()
            except RestaurantMenu.DoesNotExist:
                raise ValidationError(f"Menu item with ID {self.food_item_id} does not exist.")
            except ValidationError as e:
                raise e

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.food_item_name} sold by {self.seller.email} to {self.buyer.email}"



class Purchase(models.Model):
    id = models.AutoField(primary_key=True)
    user = models.ForeignKey('users.AppUser', on_delete=models.CASCADE, related_name='purchases')
    item = models.CharField(max_length=255, help_text="Name of the purchased item")
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price of the purchased item")
    weight = models.FloatField(help_text="Weight in kilograms (if applicable)", null=True, blank=True)
    quantity = models.PositiveIntegerField(help_text="Number of items purchased", default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Purchase {self.item} by {self.user.name}"

