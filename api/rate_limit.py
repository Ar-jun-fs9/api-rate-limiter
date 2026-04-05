from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import APIKey
import redis
from django.conf import settings

r = redis.Redis.from_url(settings.REDIS_URL)


class RateLimitedAPIView(APIView):
    max_requests = 10
    expiry_seconds = 60  # 1 minute

    def get_redis_key(self, api_key):
        return f"rate_limit:{api_key}:{self.__class__.__name__}"

    def check_rate_limit(self, api_key):
        redis_key = self.get_redis_key(api_key)
        current_count = r.get(redis_key)
        if current_count is None:
            current_count = 1
            r.set(redis_key, current_count, ex=self.expiry_seconds)
        else:
            current_count = int(current_count)
            if current_count >= self.max_requests:
                return False, 0
            current_count += 1
            r.set(redis_key, current_count, ex=self.expiry_seconds)
        remaining = self.max_requests - current_count
        return True, remaining

    def check_api_key_and_rate_limit(self, request):
        api_key = request.headers.get("X-API-Key")
        if not api_key:
            return None, Response(
                {"detail": "API key required"}, status=status.HTTP_401_UNAUTHORIZED
            )

        try:
            APIKey.objects.get(key=api_key)
        except APIKey.DoesNotExist:
            return None, Response(
                {"detail": "Invalid API key"}, status=status.HTTP_401_UNAUTHORIZED
            )

        allowed, remaining = self.check_rate_limit(api_key)
        if not allowed:
            return None, Response({"detail": "Rate limit exceeded"}, status=429)

        return api_key, remaining

    def handle_request(self, request, message):
        """
        CENTRALIZED logic for GET endpoints
        """
        api_key, remaining_or_response = self.check_api_key_and_rate_limit(request)
        if api_key is None:
            return remaining_or_response

        headers = {
            "X-RateLimit-Limit": str(self.max_requests),
            "X-RateLimit-Remaining": str(remaining_or_response)
        }
        return Response({"message": message}, headers=headers)


class RateLimited10APIView(RateLimitedAPIView):
    max_requests = 10