from rest_framework import serializers
from .models import APIKey

class APIKeySerializer(serializers.ModelSerializer):
  class Meta: 
    model: APIKey
    fields = ['owner', 'key', 'max_requests_per_minute', 'created_at']