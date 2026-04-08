import os
from pathlib import Path
from dotenv import load_dotenv
import redis

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "django-insecure-8glil8xa^e!zppxqcuf*c&%*d$i9*%6f*hagu7rhhk8)*zv%s9"
DEBUG = True
ALLOWED_HOSTS = ["api-rate-limiter-lo1o.onrender.com", "localhost", "127.0.0.1"]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "rest_framework",
    "api",
    "corsheaders",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "corsheaders.middleware.CorsMiddleware",
]

ROOT_URLCONF = "rate_limiter_project.urls"

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'api', 'templates')], # here added templates directory
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = "rate_limiter_project.wsgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
STATIC_URL = "static/"

# ---------------------------
# Upstash Redis settings
# ---------------------------
REDIS_URL = os.getenv("REDIS_URL")  # Already rediss:// with password

# Django cache using Upstash
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": REDIS_URL + "/0",  # DB 0
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
            # No need for SSL option, URL already handles it
        },
    }
}

# Celery
CELERY_BROKER_URL = REDIS_URL
CELERY_RESULT_BACKEND = REDIS_URL

if os.environ.get("RUN_MAIN") == "true":  # Only runs in the child process
    try:
        r = redis.Redis.from_url(REDIS_URL)
        r.ping()
        print("Redis connection successful")
    except Exception as e:
        print("Redis connection failed:", e)