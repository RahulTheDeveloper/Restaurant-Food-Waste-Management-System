from rest_framework import serializers
from .models import Client


class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Client
        fields = ['id', 'name', 'email', 'phone_number', 'image']

        extra_kwargs = {
            'phone_number': {'write_only': True},
        }
