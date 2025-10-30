from datetime import timedelta
from rest_framework import serializers
from .models import RawMaterial, RestaurantMenu
from .utils import generate_presigned_media_url



class RawMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = RawMaterial
        fields = '__all__'
        

class ListRawMaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = RawMaterial
        fields = '__all__'
        
        
class MenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantMenu
        fields = '__all__'
        
class NewMenuSerializer(serializers.ModelSerializer):
    image_url = serializers.SerializerMethodField(read_only=True)
    
    class Meta:
        model = RestaurantMenu
        fields = ['name','image','price_per_serving','serving_size','total_weight','client','image_url']
        read_only_fields = ['image_url']
    
    def get_image_url(self, obj):
        if obj.image:
            return generate_presigned_media_url(obj.image.name)
        return None
    
        
class ListMenuSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantMenu
        fields = ['id','name','price_per_serving','image','total_weight','expired_at']
        
    def get_image_url(self, obj):
        if obj.image:
            return generate_presigned_media_url(obj.image.name)
        return None

    
class DonateRestaurantMenuSerializer(serializers.ModelSerializer):
    menu_id = serializers.UUIDField()
    quantity = serializers.IntegerField()
    
    class Meta:
        model = RestaurantMenu
        fields = ['menu_id','quantity']

    
class DonateRawMaterialSerializer(serializers.ModelSerializer):
    rawMaterial_id = serializers.UUIDField()
    quantity = serializers.IntegerField()
    
    class Meta:
        model = RawMaterial
        fields = ['rawMaterial_id','quantity']
        
    
from rest_framework import serializers
from .models import Donation

class DonationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Donation
        fields = ['id','client','food_item_type','food_item_id','food_item_name','quantity', 'created_at']
        read_only_fields = ['id', 'created_at']



    
from payments.models import Transaction

class SellRestaurantMenuByClientSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = RestaurantMenu
        fields = ['id','name','price_per_serving','serving_size','total_weight']
        
class RestaurantTransactionHistorySerializer(serializers.ModelSerializer):
    buyer_username = serializers.CharField(source='buyer.username', read_only=True)
    class Meta:
        model = Transaction
        fields = '__all__'
        
class AppUserTransactionHistorySerializer(serializers.ModelSerializer):
    seller_username = serializers.CharField(source='seller.username', read_only=True)
    class Meta:
        model = Transaction
        fields = '__all__'
