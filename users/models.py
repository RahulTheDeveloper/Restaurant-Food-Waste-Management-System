from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.timezone import now
# from django.contrib.gis.db.models import PointField
# from django.contrib.gis.geos import Point
from payments.models import Transaction
# from django.contrib.gis.db.models.functions import Distance


class CustomUserManager(BaseUserManager):
    def create_superuser(self, email, password, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.is_superuser = True
        user.is_staff = True
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """
        Create and return a regular user with an email and password.
        """
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user


class Client(AbstractUser):
    id = models.AutoField(primary_key=True)
    username = None  # Remove the username field
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    oauth_id = models.CharField(
        max_length=255, null=True, blank=True,
        help_text="Unique OAuth ID for authentication (Google, Facebook, etc.)"
    )
    address = models.TextField(help_text="Full address of the client")
    is_active = models.BooleanField(default=True, help_text="Is the client currently active?")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["name"]
    
    objects = CustomUserManager()

    # Relations with other models
    raw_materials = models.ManyToManyField(
        'stock.RawMaterial',
        related_name='clients',
        blank=True,
        help_text="Raw materials owned by the client"
    )
    restaurant_menu = models.ManyToManyField(
        'stock.RestaurantMenu',
        related_name='clients',
        blank=True,
        help_text="Restaurant menu items owned by the client"
    )
    packaged_food = models.ManyToManyField(
        'stock.PackagedFood',
        related_name='clients',
        blank=True,
        help_text="Packaged food items owned by the client"
    )
    
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='client_set',  # Custom related_name
        blank=True,
        help_text="The groups this client belongs to.",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='client_permissions',  # Custom related_name
        blank=True,
        help_text="Specific permissions for this client.",
    )

    class Meta:
        verbose_name = "Client"
        verbose_name_plural = "Clients"

#     def set_location(self, latitude, longitude):
#         """Set location using latitude and longitude."""
#         self.location = Point(longitude, latitude)
#         self.save()

#     def get_nearby_users(self, radius_km=10):
#         """Get AppUsers within a certain radius using GeoDjango."""
#         from django.contrib.gis.db.models.functions import Distance
#         from users.models import AppUser

#         if self.location:
#             nearby_users = AppUser.objects.filter(
#                 location__distance_lte=(self.location, radius_km * 1000)
#             ).annotate(distance=Distance('location', self.location)).order_by('distance')
#             return nearby_users
#         return None


class AppUser(AbstractUser):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, null=True, blank=True)
    oauth_id = models.CharField(
        max_length=255, null=True, blank=True,
        help_text="Unique OAuth ID for authentication (Google, Facebook, etc.)"
    )
    address = models.TextField(help_text="Full address of the user", null=True, blank=True)
#     location = PointField(
#         help_text="Geographical location (latitude, longitude)",
#         null=True, blank=True
#     )
    is_active = models.BooleanField(default=True, help_text="Is the user currently active?")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='appuser_set',  # Custom related_name
        blank=True,
        help_text="The groups this user belongs to.",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='appuser_permissions',  # Custom related_name
        blank=True,
        help_text="Specific permissions for this user.",
    )

    def __str__(self):
        return self.username

#     def set_location(self, latitude, longitude):
#         """Set location using latitude and longitude."""
#         self.location = Point(longitude, latitude)
#         self.save()

    def get_donation_history(self):
        """Get donation history for this user."""
        return Transaction.objects.filter(user=self, transaction_type='donation').order_by('-timestamp')

    def get_purchase_history(self):
        """Get purchase history for this user."""
        return Transaction.objects.filter(user=self, transaction_type='purchase').order_by('-timestamp')

#     def get_nearby_clients(self, radius_km=10):
#         """Get nearby clients within a certain radius using GeoDjango."""


#         if self.location:
#             nearby_clients = Client.objects.filter(
#                 location__distance_lte=(self.location, radius_km * 1000)
#             ).annotate(distance=Distance('location', self.location)).order_by('distance')
#             return nearby_clients
#         return None


    class Meta:
        verbose_name = "App User"
        verbose_name_plural = "App Users"

