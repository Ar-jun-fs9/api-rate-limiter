from django.contrib import admin
from .models import APIKey

@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ('owner', 'key', 'max_requests_per_minute', 'created_at')
    readonly_fields = ('key', 'created_at')