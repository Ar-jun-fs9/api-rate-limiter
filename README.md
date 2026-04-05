# API Rate Limiter

A Django REST framework-based API rate limiting system that enforces per-API-key and per-endpoint request limits using Redis (Upstash) for distributed rate tracking.

## Overview

This project implements rate limiting at the API level with:
- **Per-API Key Limiting**: Each API key has its own request counter
- **Per-Endpoint Limiting**: Different endpoints can have different rate limits
- **Redis Backend**: Uses Upstash Redis for fast, distributed rate tracking
- **Response Headers**: Returns `X-RateLimit-Limit` and `X-RateLimit-Remaining` headers

## API Rate Limiter Screenshots

The following images show the API rate limiter in action, from initial requests to rate limiting responses.

### Step 1: Unauthorized Request (Missing API Key)

- A request without an API key returns **401 Unauthorized**:

| ![401error1](assets/401error1.png) | ![200OK2](assets/200OK2.png) |
|-----------------------------------|--------------------------------|
| Unauthorized (401)                | Successful request (200 OK)   |

---

### Step 2: Request Counting

- Requests increment the Redis counter. You can see the live counts for each API key:

| ![count3](assets/count3.png) | ![0count4](assets/0count4.png) |
|-------------------------------|-------------------------------|
| Counter at 3 requests          | Counter reset to 0            |

---

### Step 3: Rate Limit Exceeded

- When the limit is reached, the API returns **429 Too Many Requests**:

| ![429error5](assets/429error5.png) | ![JSON4296](assets/JSON4296.png) |
|-----------------------------------|----------------------------------|
| Browser error view                | JSON response with 429           |

---

### Step 4: Redis Backend Monitoring

- Check the Redis keys in Upstash to verify rate limiting counters:

| ![redis7](assets/redis7.png) |
|-------------------------------|
| Redis showing per-API-key counters |

## Architecture

```
┌─────────────┐     X-API-Key Header     ┌──────────────────┐
│   Client    │ ───────────────────────► │   Django API     │
└─────────────┘                          │                  │
                                          │  rate_limit.py  │
                                          │  - Validate key │
                                          │  - Check limit   │
                                          └────────┬─────────┘
                                                   │
                                          ┌────────▼─────────┐
                                          │   Upstash Redis  │
                                          │                   │
                                          │ rate_limit:{key} │
                                          │ :{endpoint_class}│
                                          └──────────────────┘
```

## Project Structure

```
api_rate_limiter/
├── api/                           # Main API application
│   ├── models.py                  # APIKey model definition
│   ├── views.py                   # API endpoints with rate limiting
│   ├── rate_limit.py              # Core rate limiting logic (custom)
│   ├── urls.py                    # URL routing for endpoints
│   ├── serializers.py             # DRF serializers for APIKey
│   ├── admin.py                   # Django admin configuration
│   └── migrations/                # Database migrations
├── rate_limiter_project/          # Django project settings
│   ├── settings.py                # Project configuration (Redis)
│   ├── urls.py                    # Root URL configuration
│   ├── wsgi.py                    # WSGI entry point
│   └── asgi.py                    # ASGI entry point
├── .env                           # Environment variables (Redis URL)
├── requirements.txt               # Python dependencies
└── manage.py                      # Django management script
```

## Custom Components

### `api/rate_limit.py` - Rate Limiting Core

This module contains the custom rate limiting implementation:

- **`RateLimitedAPIView`**: Base class that all rate-limited views inherit from
  - `max_requests`: Class attribute defining requests allowed per minute (default: 10)
  - `expiry_seconds`: TTL for Redis keys (default: 60 seconds)
  - `get_redis_key(api_key)`: Generates Redis key in format `rate_limit:{api_key}:{class_name}`
  - `check_rate_limit(api_key)`: Queries Redis, increments counter, enforces limit
  - `check_api_key_and_rate_limit(request)`: Validates X-API-Key header and checks rate
  - `handle_request(request, message)`: Centralized response handling with headers

- **`RateLimited10APIView`**: Subclass with 10 requests/minute limit

### `api/models.py` - APIKey Model

Django model for storing API keys:

```python
class APIKey(models.Model):
    key = models.UUIDField(default=uuid.uuid4, unique=True)  # Generated UUID
    owner = models.CharField(max_length=100)                 # Owner identifier
    max_requests_per_minute = models.IntegerField(default=10)
    created_at = models.DateTimeField(auto_now_add=True)
```

- Used to validate incoming API keys from the database
- The `key` field stores the UUID used in the X-API-Key header

### `api/views.py` - API Endpoints

All views inherit from rate limiting classes and implement GET handlers:

| View Class | Endpoint | Rate Limit | Purpose |
|------------|----------|-------------|---------|
| `TestAPIView` | `/api/test/` | 10 req/min | Test endpoint |
| `HelloAPIView` | `/api/hello/` | 10 req/min | Hello endpoint |
| `ProfileAPIView` | `/api/profile/` | 10 req/min | Profile endpoint |
| `LoginAPIView` | `/api/login/` | 20 req/min | Login endpoint |
| `PurchaseAPIView` | `/api/purchase/` | 15 req/min | Purchase endpoint |

Each view:
1. Extends `RateLimited10APIView` or `RateLimitedAPIView` with custom `max_requests`
2. Implements `get(self, request)` method
3. Calls `self.handle_request(request, message)` which performs:
   - API key validation
   - Rate limit checking
   - Returns JSON response with appropriate headers

### `api/urls.py` - URL Routing

Routes incoming requests to the appropriate view:

```python
urlpatterns = [
    path('test/', TestAPIView.as_view(), name='test-api'),
    path('hello/', HelloAPIView.as_view(), name='hello-api'),
    path('login/', LoginAPIView.as_view(), name='login-api'),
    path('purchase/', PurchaseAPIView.as_view(), name='purchase-api'),
    path('profile/', ProfileAPIView.as_view(), name='profile-api'),
]
```

### `api/serializers.py` - APIKey Serializer

DRF serializer for the APIKey model, exposing:
- `owner`
- `key`
- `max_requests_per_minute`
- `created_at`

### `api/admin.py` - Django Admin

Configures the Django admin interface for APIKey management with:
- `list_display`: Shows owner, key, max_requests_per_minute, created_at
- `readonly_fields`: key and created_at are read-only

### `rate_limiter_project/settings.py` - Configuration

Key custom settings:

```python
# Redis (Upstash) configuration
REDIS_URL = os.getenv("REDIS_URL")  # From .env file

# Django cache backend using Redis
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL + "/0",
    }
}
```

## Rate Limiting Flow

1. **Request arrives** with `X-API-Key` header
2. **`check_api_key_and_rate_limit`** validates:
   - API key is present in header
   - API key exists in database (APIKey model)
3. **Redis lookup** using key format: `rate_limit:{api_key}:{endpoint_class}`
4. **If no key exists**: Initialize counter to 1, set 60-second TTL
5. **If key exists**: Increment counter, check against `max_requests`
6. **If limit exceeded**: Return 429 response
7. **On success**: Return response with headers:
   - `X-RateLimit-Limit`: Maximum requests allowed
   - `X-RateLimit-Remaining`: Remaining requests in window

## Endpoints Reference

| Method | Endpoint | Limit | Response |
|--------|----------|-------|----------|
| GET | `/api/test/` | 10/min | `{"message": "Test API Success"}` |
| GET | `/api/hello/` | 10/min | `{"message": "Hello API Success"}` |
| GET | `/api/profile/` | 10/min | `{"message": "Profile API Success"}` |
| GET | `/api/login/` | 20/min | `{"message": "Login API Success"}` |
| GET | `/api/purchase/` | 15/min | `{"message": "Purchase API Success"}` |

### Error Responses

- **401 Unauthorized** (Missing key): `{"detail": "API key required"}`
- **401 Unauthorized** (Invalid key): `{"detail": "Invalid API key"}`
- **429 Too Many Requests**: `{"detail": "Rate limit exceeded"}`

### Success Response Headers

```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 8
```

## Setup Instructions

### Prerequisites

- Python 3.8+
- Upstash Redis account (free tier works)
- Django 6.0+

### 1. Clone and Setup Virtual Environment

```bash
git clone https://github.com/Ar-jun-fs9/api-rate-limiter.git
cd api_rate_limiter
python -m venv api_venv
source api_venv/bin/activate  # Linux/Mac
# or
api_venv\Scripts\activate  # Windows
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Upstash Redis

1. Create a free account at [upstash.com](https://upstash.com)
2. Create a new Redis database
3. Copy the `REDIS_URL` (should be `rediss://...`)
4. Update `.env` file:

```
REDIS_URL="rediss://default:YOUR_PASSWORD@your-instance.upstash.io:6379"
```

### 4. Run Migrations

```bash
python manage.py migrate
```

### 5. Create an API Key

Access Django admin at `http://localhost:8000/admin`:
1. Create a superuser: `python manage.py createsuperuser`
2. Navigate to API Keys section
3. Create a new APIKey with an owner name
4. Copy the generated UUID key

### 6. Run the Server

```bash
python manage.py runserver
```

## Testing the Rate Limiter

### Using cURL

```bash
# Replace YOUR_API_KEY with the UUID from admin
export API_KEY="your-api-key-uuid"

# Make requests (up to limit)
curl -H "X-API-Key: $API_KEY" http://localhost:8000/api/test/
curl -H "X-API-Key: $API_KEY" http://localhost:8000/api/hello/

# Check response headers
curl -i -H "X-API-Key: $API_KEY" http://localhost:8000/api/test/
```

### Expected Responses

**Success:**
```json
{"message": "Test API Success"}
```
With headers:
```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 9
```

**Rate Limit Exceeded:**
```json
{"detail": "Rate limit exceeded"}
```

**Missing API Key:**
```json
{"detail": "API key required"}
```

**Invalid API Key:**
```json
{"detail": "Invalid API key"}
```

# Testing API with Postman

Follow these steps to test your API endpoint using Postman.

1. **Create a new request in Postman**
   - Set **method** to `GET`.
   - Set **URL** to:
     ```
     http://localhost:8000/api/test/
     ```

2. **Add Headers**
   | Key       | Value               |
   |-----------|-------------------|
   | X-API-Key | your-api-key-uuid |

3. **Send the request**
   - Click **Send**.
   - Observe response and headers:
     ```
     X-RateLimit-Limit
     X-RateLimit-Remaining
     ```
   - Repeat to test rate limiting.

4. **Expected Responses**

   - **Success**
     ```json
     {
       "message": "Test API Success"
     }
     ```

   - **Rate Limit Exceeded**
     ```json
     {
       "detail": "Rate limit exceeded"
     }
     ```

   - **Missing API Key**
     ```json
     {
       "detail": "API key required"
     }
     ```

   - **Invalid API Key**
     ```json
     {
       "detail": "Invalid API key"
     }
     ```

### Test Script Example

```bash
#!/bin/bash
API_KEY="your-api-key-here"

for i in {1..12}; do
    echo "Request $i:"
    curl -s -H "X-API-Key: $API_KEY" http://localhost:8000/api/test/ | jq
    echo "---"
done
```

## Dependencies

```
Django==6.0.3           # Web framework
djangorestframework==3.17.1  # REST API
django-cors-headers==4.9.0   # CORS support
django-redis==6.0.0    # Redis cache backend
redis==7.4.0           # Redis client
python-dotenv==1.2.2   # Environment variables
```

## Production Considerations

1. **Change SECRET_KEY** in settings.py
2. **Configure ALLOWED_HOSTS** for your domain
3. **Use HTTPS** for production
4. **Monitor Redis usage** in Upstash dashboard
5. **Consider sliding window** algorithm for smoother limiting
6. **Add logging** for rate limit events

## License

MIT License