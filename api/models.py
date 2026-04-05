from django.db import models
import uuid

class APIKey(models.Model):
    key = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    owner = models.CharField(max_length=100)
    max_requests_per_minute = models.IntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.owner} - {self.key}"