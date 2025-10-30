from django.db import models
from stock.models import PackagedFood, RestaurantMenu
# Create your models here.

class Order(models.Model):
    ORDER_STATUS_CHOICES = [
        ('delivered', 'Delivered'),
        ('on_the_way', 'On the Way'),
        ('cancelled', 'Cancelled'),
    ]

    order_id = models.AutoField(primary_key=True)
    packaged_food_items = models.ManyToManyField(
        PackagedFood, through="PackagedFoodOrder"
    )
    restaurant_menu_items = models.ManyToManyField(
        RestaurantMenu, through="RestaurantFoodOrder"
    )
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    order_status = models.CharField(max_length=50, choices=ORDER_STATUS_CHOICES)
    transaction_id = models.CharField(max_length=255)

    def calculate_total_price(self):
        total = 0
        # Sum Packaged Food Prices
        for item in self.packagedfoodorder_set.all():
            total += item.packaged_food.price_per_unit * item.quantity
        # Sum Restaurant Food Prices
        for item in self.restaurantfoodorder_set.all():
            total += item.restaurant_menu.price_per_serving * item.quantity
        self.total_price = total
        self.save()

    def __str__(self):
        return f"Order {self.order_id}"


class PackagedFoodOrder(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    packaged_food = models.ForeignKey(PackagedFood, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def save(self, *args, **kwargs):
        if self.quantity > self.packaged_food.quantity:
            raise ValueError("Not enough stock available for the packaged food!")
        super().save(*args, **kwargs)
        self.packaged_food.quantity -= self.quantity
        self.packaged_food.save()
        
        
class RestaurantFoodOrder(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    restaurant_menu = models.ForeignKey(RestaurantMenu, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    def save(self, *args, **kwargs):
        required_weight = self.quantity * self.restaurant_menu.serving_size
        if required_weight > self.restaurant_menu.total_weight:
            raise ValueError("Not enough prepared food available!")
        super().save(*args, **kwargs)
        self.restaurant_menu.total_weight -= required_weight
        self.restaurant_menu.save()

