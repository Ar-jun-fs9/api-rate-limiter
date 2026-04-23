<div align=center>

# API Rate Limiter - Test Cases

</div>

## Overview

This document provides a complete test plan for testing the API Rate Limiter system using Postman or similar tools.

### Test Environment
- **Base URL**: `http://localhost:8000`
- **Content-Type**: `application/json`

### Test Workflow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        END-TO-END TEST WORKFLOW                            │
└─────────────────────────────────────────────────────────────────────────────┘

Step 1:     GET /                  → Verify API is running
Step 2:     GET /admin/            → Access Django admin (create API key)
Step 3:     POST /admin/api/apikey/add/ → Create API Key via admin
Step 4:     GET /api/test/          → Test basic API endpoint
Step 5:     GET /api/hello/         → Test hello endpoint
Step 6:     GET /api/profile/       → Test profile endpoint
Step 7:     GET /api/login/         → Test login endpoint (higher limit)
Step 8:     GET /api/purchase/      → Test purchase endpoint
Step 9:     GET /api/test/ (10x)    → Test rate limit exceeded
```

---

## Step 1: Verify API is Running

### Endpoint: GET /

**Purpose**: Verify the API server is running and responsive.

**Request**:
```http
GET http://localhost:8000/
```

**Success Response**:
```
200 OK

Welcome to API Rate Limiter - Landing page HTML content
```

**What User CAN Do**:
- Verify the server is online
- Access the landing page with documentation

**What User CANNOT Do**:
- Access any protected API endpoints
- Modify any data

**Important Rules**:
- This is a public endpoint (no authentication required)
- First check if API is responding before testing other endpoints

---

## Step 2: Access Django Admin

### Endpoint: GET /admin/

**Purpose**: Access the Django admin panel to manage API keys.

**Request**:
```http
GET http://localhost:8000/admin/
```

**Success Response**:
```
200 OK

Django admin login page HTML content
```

**What User CAN Do**:
- Access admin panel with valid credentials
- Manage API keys (create, view, delete)

**What User CANNOT Do**:
- Access admin without authentication
- Access API endpoints through admin panel

**Important Rules**:
- Requires superuser credentials
- Admin panel is for managing API keys only
- First step before testing API endpoints

**Test Data**:
- Valid admin: username/password from `python manage.py createsuperuser`
- Invalid: wrong username/password

---

## Step 3: Create API Key via Admin

### Endpoint: POST /admin/api/apikey/add/

**Purpose**: Create a new API key in the Django admin panel.

**Request**:
```http
POST http://localhost:8000/admin/api/apikey/add/
Content-Type: application/x-www-form-urlencoded

csrfmiddlewaretoken=<token>&owner=test-client&max_requests_per_minute=10
```

**Success Response**:
```
302 Found (redirect to API key list)
```

**What User CAN Do**:
- Create API keys with custom rate limits
- Set owner name for identification

**What User CANNOT Do**:
- Create API keys without admin authentication
- Set invalid rate limits

**Important Rules**:
- Requires admin authentication
- API key is auto-generated UUID
- Rate limit defaults to 10 if not specified

**Test Data**:
- Valid: owner="test-client", max_requests_per_minute=10
- Invalid: empty owner, negative rate limit

---

## Step 4: Test Basic API Endpoint

### Endpoint: GET /api/test/

**Purpose**: Test the basic API endpoint with rate limiting.

**Request**:
```http
GET http://localhost:8000/api/test/
X-API-Key: <your-api-key-uuid>
```

**Success Response** (200 OK):
```json
{
    "message": "Test API Success"
}
```

**Response Headers**:
```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 9
```

**Failure Scenarios**:

1. **Missing API Key** (401 Unauthorized):
```json
{
    "detail": "API key required"
}
```

2. **Invalid API Key** (401 Unauthorized):
```json
{
    "detail": "Invalid API key"
}
```

3. **Rate Limit Exceeded** (429 Too Many Requests):
```json
{
    "detail": "Rate limit exceeded"
}
```

**What User CAN Do**:
- Make successful API requests with valid key
- View rate limit headers in response
- Make up to 10 requests per minute

**What User CANNOT Do**:
- Access without API key
- Use invalid API keys
- Exceed rate limit (10/min for test endpoint)

**Important Rules**:
- Requires X-API-Key header
- Rate limit is 10 requests per minute
- Counters reset every 60 seconds
- Each API key has separate counters per endpoint

**Test Data**:
- Valid key: UUID from admin panel
- Invalid key: random string, empty string

---

## Step 5: Test Hello Endpoint

### Endpoint: GET /api/hello/

**Purpose**: Test the hello API endpoint with same rate limits as test.

**Request**:
```http
GET http://localhost:8000/api/hello/
X-API-Key: <your-api-key-uuid>
```

**Success Response** (200 OK):
```json
{
    "message": "Hello API Success"
}
```

**Response Headers**:
```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 9
```

**What User CAN Do**:
- Access hello endpoint with valid API key
- View rate limit status

**What User CANNOT Do**:
- Access without authentication
- Share rate limit counters with other endpoints

**Important Rules**:
- Same rate limit as test endpoint (10/min)
- Separate Redis counter per endpoint
- Same authentication requirements

---

## Step 6: Test Profile Endpoint

### Endpoint: GET /api/profile/

**Purpose**: Test the profile API endpoint.

**Request**:
```http
GET http://localhost:8000/api/profile/
X-API-Key: <your-api-key-uuid>
```

**Success Response** (200 OK):
```json
{
    "message": "Profile API Success"
}
```

**Response Headers**:
```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 9
```

**What User CAN Do**:
- Access profile information with valid key
- Monitor rate limit usage

**What User CANNOT Do**:
- Access profile data of other API keys
- Bypass rate limiting

**Important Rules**:
- Rate limit: 10 requests per minute
- Independent counter from other endpoints

---

## Step 7: Test Login Endpoint (Higher Limit)

### Endpoint: GET /api/login/

**Purpose**: Test the login endpoint with higher rate limit (20/min).

**Request**:
```http
GET http://localhost:8000/api/login/
X-API-Key: <your-api-key-uuid>
```

**Success Response** (200 OK):
```json
{
    "message": "Login API Success"
}
```

**Response Headers**:
```
X-RateLimit-Limit: 20
X-RateLimit-Remaining: 19
```

**What User CAN Do**:
- Make up to 20 requests per minute
- Use for authentication-related operations

**What User CANNOT Do**:
- Exceed 20 requests per minute
- Access without valid API key

**Important Rules**:
- Higher rate limit than other endpoints (20/min)
- Suitable for login/authentication flows

---

## Step 8: Test Purchase Endpoint

### Endpoint: GET /api/purchase/

**Purpose**: Test the purchase endpoint with medium rate limit (15/min).

**Request**:
```http
GET http://localhost:8000/api/purchase/
X-API-Key: <your-api-key-uuid>
```

**Success Response** (200 OK):
```json
{
    "message": "Purchase API Success"
}
```

**Response Headers**:
```
X-RateLimit-Limit: 15
X-RateLimit-Remaining: 14
```

**What User CAN Do**:
- Make purchase-related API calls
- Handle up to 15 requests per minute

**What User CANNOT Do**:
- Exceed purchase rate limit
- Make purchases without authentication

**Important Rules**:
- Rate limit: 15 requests per minute
- Designed for transaction operations

---

## Step 9: Test Rate Limit Exceeded

### Endpoint: GET /api/test/ (repeated requests)

**Purpose**: Test rate limiting by making more requests than allowed.

**Request** (make 11 requests rapidly):
```http
GET http://localhost:8000/api/test/
X-API-Key: <your-api-key-uuid>
```

**First 10 Success Responses** (200 OK):
```json
{
    "message": "Test API Success"
}
```
**Headers**:
```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 9 (decrementing to 0)
```

**11th Request Response** (429 Too Many Requests):
```json
{
    "detail": "Rate limit exceeded"
}
```

**What User CAN Do**:
- Make requests up to the limit
- Monitor remaining requests via headers

**What User CANNOT Do**:
- Make unlimited requests
- Bypass rate limiting

**Important Rules**:
- 429 status code when limit exceeded
- Counters reset after 60 seconds
- Each API key has per-endpoint limits

---

## Testing Matrix

### Endpoint Authentication Matrix

| Endpoint | Auth Required | Rate Limit | Method |
|----------|--------------|-------------|--------|
| GET / | No | None | GET |
| GET /admin/ | Yes (Admin) | None | GET |
| POST /admin/api/apikey/add/ | Yes (Admin) | None | POST |
| GET /api/test/ | Yes (API Key) | 10/min | GET |
| GET /api/hello/ | Yes (API Key) | 10/min | GET |
| GET /api/profile/ | Yes (API Key) | 10/min | GET |
| GET /api/login/ | Yes (API Key) | 20/min | GET |
| GET /api/purchase/ | Yes (API Key) | 15/min | GET |

### Error Response Codes

| Status Code | Meaning |
|-------------|---------|
| 200 | Success |
| 302 | Redirect (admin after create) |
| 401 | Unauthorized (missing/invalid API key) |
| 429 | Too Many Requests (rate limit exceeded) |

---

## Postman Collection Variables

Set these variables in Postman to make testing easier:

```
{{base_url}} = http://localhost:8000
{{api_key}} = <paste UUID from admin>
```

### Sample Test Order

1. **Verify API Running**:
    ```bash
    GET {{base_url}}/
    ```

2. **Access Admin** (browser):
    ```
    {{base_url}}/admin/
    Login with superuser credentials
    ```

3. **Create API Key** (in admin panel):
    ```
    Go to API Keys → Add API Key
    Owner: test-client
    Max requests per minute: 10
    Save and copy the UUID
    ```

4. **Test Basic Endpoint**:
    ```bash
    GET {{base_url}}/api/test/
    Headers: X-API-Key: {{api_key}}
    ```

5. **Test Rate Limiting**:
    ```bash
    # Make 11 requests (use loop or send manually)
    for i in {1..11}; do
        curl -H "X-API-Key: {{api_key}}" {{base_url}}/api/test/
    done
    # 11th should return 429
    ```

6. **Test All Endpoints**:
    ```bash
    curl -H "X-API-Key: {{api_key}}" {{base_url}}/api/hello/
    curl -H "X-API-Key: {{api_key}}" {{base_url}}/api/profile/
    curl -H "X-API-Key: {{api_key}}" {{base_url}}/api/login/
    curl -H "X-API-Key: {{api_key}}" {{base_url}}/api/purchase/
    ```

7. **Test Invalid API Key**:
    ```bash
    curl -H "X-API-Key: invalid-key" {{base_url}}/api/test/
    # Should return 401
    ```

8. **Test Missing API Key**:
    ```bash
    curl {{base_url}}/api/test/
    # Should return 401
    ```

---

## Rate Limiting Behavior

### Per-API-Key Limits
- Each API key has its own rate limit counters
- Limits are enforced per endpoint
- Redis stores counters with format: `rate_limit:{api_key}:{endpoint_class}`

### Time Window
- Rate limits reset every 60 seconds
- Counters expire automatically in Redis
- No manual reset required

### Rate Limit Headers
Every successful response includes:
```
X-RateLimit-Limit: <max_requests>
X-RateLimit-Remaining: <remaining_requests>
```

### Custom Rate Limits
- API keys can have custom `max_requests_per_minute` in admin
- Default is 10 requests per minute
- Overrides endpoint-specific limits

---

## Currently Implemented Features

**Implemented:**
- API key authentication with UUID
- Per-API-key and per-endpoint rate limiting
- Redis backend for counters
- Rate limit response headers
- Django admin for key management
- Multiple endpoints with different limits
- Landing page with documentation
- Proper error responses (401, 429)

---

## Testing Checklist

- [ ] **API Running**: GET / returns 200
- [ ] **Admin Access**: Can login to /admin/
- [ ] **API Key Creation**: Can create keys in admin
- [ ] **Valid API Key**: Endpoints return 200 with headers
- [ ] **Invalid API Key**: Returns 401 "Invalid API key"
- [ ] **Missing API Key**: Returns 401 "API key required"
- [ ] **Rate Limit Exceeded**: Returns 429 "Rate limit exceeded"
- [ ] **Counter Reset**: Limits reset after 60 seconds
- [ ] **Per-Endpoint Limits**: Different endpoints have separate counters
- [ ] **Header Values**: X-RateLimit-Limit and X-RateLimit-Remaining are correct
- [ ] **Custom Limits**: API keys with custom max_requests_per_minute work

---

## Production Considerations

- Redis connection configured via REDIS_URL
- API keys are UUID-based for security
- Rate limits prevent abuse
- Admin panel for key management
- Landing page for documentation

---

## Extended Testing Scenarios remaining Bro

### Multiple API Keys
1. Create multiple API keys in admin
2. Test that each key has independent counters
3. Verify one key's usage doesn't affect others

### Endpoint Isolation
1. Exhaust limit on /api/test/
2. Verify /api/hello/ still works
3. Confirm separate Redis keys

### Time-Based Reset
1. Exhaust rate limit
2. Wait 60+ seconds
3. Verify counters reset and requests work again

### Custom Rate Limits
1. Create API key with custom limit (e.g., 5/min)
2. Verify it allows only 5 requests before 429
3. Test with different endpoints



## Ended Broo HEHE