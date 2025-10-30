from django.db import models
from django.utils.timezone import now
from payments.models import Transaction
import uuid

class machine_learning(models.Model):
    ...
    

class   Donation(models.Model):
        id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
        client = models.ForeignKey('users.Client', on_delete=models.CASCADE, related_name="donations")
        food_item_type = models.CharField(
            max_length=50,
            choices=[
                ('raw_material', 'Raw Material'),
                ('restaurant_menu', 'Restaurant Menu'),
                ('packaged_food', 'Packaged Food'),
            ],
            help_text="Type of food item being donated"
        )
        food_item_id = models.PositiveIntegerField(help_text="ID of the donated food item")
        food_item_name = models.CharField(max_length=255, help_text="Name of the donated food item")
        quantity = models.FloatField(help_text="Quantity of the donated item (kg or units)")
        created_at = models.DateTimeField(auto_now_add=True)

        def __str__(self):
            return f"{self.quantity} of {self.food_item_name} donated by {self.client.name}"


class RawMaterial(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255, null=True, blank=True)
    image = models.ImageField(upload_to='raw_materials/images/', null=True, blank=True)
    temperature = models.FloatField(help_text="Temperature in °C", null=True, blank=True)
    humidity = models.FloatField(help_text="Humidity in %", null=True, blank=True)
    pH = models.FloatField(help_text="pH levels", null=True, blank=True)
    microbial_count = models.PositiveIntegerField(help_text="Microbial count in CFU/g", null=True, blank=True)
    weight = models.FloatField(help_text="Weight in kilograms", null=True, blank=True)
    packaging_type = models.CharField(
        max_length=50, 
        choices=[('vacuum_sealed', 'Vacuum Sealed'), ('air_tight', 'Air Tight')],
        null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField(null=True, blank=True)  # Set after ML processing
    is_wasted = models.BooleanField(default=False, help_text="Mark as wasted after expiration")
    client = models.ForeignKey('users.Client', on_delete=models.CASCADE)

 
    def __str__(self):
        return self.name
    
    def sell(self, buyer, quantity, price_per_kg, payment_method):
        """
        Handles the sale of raw materials.
        """
        if self.weight >= quantity:
            total_price = quantity * price_per_kg
            self.weight -= quantity
            self.save()

            # Create a Transaction record
            transaction = Transaction.objects.create(
                buyer=buyer,
                seller=self.client,
                food_item_type='raw_material',
                food_item_id=self.id,
                food_item_name=self.name,
                quantity=quantity,
                price=total_price,
                transaction_id=f"TRX-{now().strftime('%Y%m%d%H%M%S')}",
                payment_method=payment_method,
                status='completed',
            )
            return transaction
        return f"Insufficient stock to sell {quantity} kg of {self.name}."
    
    def donate(self, client, quantity):
        """
        Handles the donation of raw materials.
        """
        if self.weight >= quantity:
            self.weight -= quantity
            self.save()

            # Create a Donation record
            Donation.objects.create(
                client=client,
                food_item_type='raw_material',
                food_item_id=self.id,
                food_item_name=self.name,
                quantity=quantity,
            )
            return f"Successfully donated {quantity} kg of {self.name}."
        return f"Insufficient stock to donate {quantity} kg of {self.name}."

    



class RestaurantMenu(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='restaurant_menu/images/', null=True, blank=True)
    temperature = models.FloatField(help_text="Ideal serving temperature in °C", null=True, blank=True)
    ingredients = models.ManyToManyField(RawMaterial, related_name="menus", blank=True)
    price_per_serving = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price per serving", null=True, blank=True)
    serving_size = models.FloatField(help_text="Serving size in kilograms", null=True, blank=True)
    total_weight = models.FloatField(help_text="Total prepared weight in kilograms", null=True, blank=True)
    donate = models.BooleanField(default=False, help_text="Mark as donated", null=True, blank=True)
    client = models.ForeignKey('users.Client', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField(null=True, blank=True)
    is_wasted = models.BooleanField(default=False, help_text="Mark as wasted after expiration")
    


    def __str__(self):
        return self.name
    
    def sell(self, buyer, quantity, price_per_serving, payment_method):
        """
        Handles the sale of prepared food.
        """
        if self.total_weight >= quantity:
            total_price = quantity * price_per_serving
            self.total_weight -= quantity
            self.save()

            # Create a Transaction record
            transaction = Transaction.objects.create(
                buyer=buyer,
                seller=self.client,  # Assuming seller is the client
                food_item_type='restaurant_menu',
                food_item_id=self.id,
                food_item_name=self.name,
                quantity=quantity,
                price=total_price,
                transaction_id=f"TRX-{now().strftime('%Y%m%d%H%M%S')}",
                payment_method=payment_method,
                status='completed',
            )
            return transaction
        return f"Insufficient stock to sell {quantity} kg of {self.name}."

    def donate_item(self, client, quantity):
        """
        Handles the donation of prepared food items.
        """
        if self.total_weight >= quantity:
            self.total_weight -= quantity
            self.donate = True
            self.save()

            # Create a Donation record
            Donation.objects.create(
                client=client,
                food_item_type='restaurant_menu',
                food_item_id=self.id,
                food_item_name=self.name,
                quantity=quantity,
            )
            return f"Successfully donated {quantity} kg of {self.name}."
        return f"Insufficient stock to donate {quantity} kg of {self.name}."


class PackagedFood(models.Model):
    id = models.UUIDField(primary_key=True, unique=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='packaged_food/images/', null=True, blank=True)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price per unit")
    donate = models.BooleanField(default=False, help_text="Mark as donated")
    weight = models.FloatField(help_text="Weight in kilograms")
    quantity = models.PositiveIntegerField(help_text="Number of items in stock")
    client = models.ForeignKey('users.Client', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    expired_at = models.DateTimeField(null=True, blank=True)
    is_wasted = models.BooleanField(default=False, help_text="Mark as wasted after expiration")

    def __str__(self):
        return self.name
    
    def sell(self, buyer, quantity, price_per_unit, payment_method):
        """
        Handles the sale of packaged food.
        """
        if self.quantity >= quantity:
            total_price = quantity * price_per_unit
            self.quantity -= quantity
            self.save()

            # Create a Transaction record
            transaction = Transaction.objects.create(
                buyer=buyer,
                seller=self.user,
                food_item_type='packaged_food',
                food_item_id=self.id,
                food_item_name=self.name,
                quantity=quantity,
                price=total_price,
                transaction_id=f"TRX-{now().strftime('%Y%m%d%H%M%S')}",
                payment_method=payment_method,
                status='completed',
            )
            return transaction
        return f"Insufficient stock to sell {quantity} units of {self.name}."
    
    def donate(self, client, quantity):
        """
        Handles the donation of packaged food.
        """
        if self.quantity >= quantity:
            self.quantity -= quantity
            self.donate = True
            self.save()

            # Create a Donation record
            Donation.objects.create(
                client=client,
                food_item_type='packaged_food',
                food_item_id=self.id,
                food_item_name=self.name,
                quantity=quantity,
            )
            return f"Successfully donated {quantity} units of {self.name}."
        return f"Insufficient stock to donate {quantity} units of {self.name}."


