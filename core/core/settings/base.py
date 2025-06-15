# ==============================
# core/settings/base.py
# Common base settings shared across environments
# ==============================

from pathlib import Path
from decouple import config

# Base directory (3 levels above this file)
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Create a logs directory if it doesn't exist (useful for file-based logging)
LOGS_DIR = BASE_DIR / "logs"
if not LOGS_DIR.exists():
    LOGS_DIR.mkdir(parents=True, exist_ok=True)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config("SECRET_KEY", default="test")


# Application definition
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "django.contrib.sitemaps",
    "robots",
    "rest_framework",
    "rest_framework.authtoken",
    "rest_framework_simplejwt",
    "djoser",
    "mail_templated",
    "corsheaders",
    "django_filters",
    "drf_yasg",
    "django_celery_beat",
    "ckeditor",
    "ckeditor_uploader",
    "accounts",
    "blog",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

# Templates configuration
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],  # Global templates directory
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "core.wsgi.application"


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Asia/Tehran"
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"  # Used in production (collectstatic)
STATICFILES_DIRS = [BASE_DIR / "static"]  # Used in development

# Media files (User-uploaded content)
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# CKEditor configuration
CKEDITOR_UPLOAD_PATH = "uploads/"
CKEDITOR_IMAGE_BACKEND = "pillow"
CKEDITOR_CONFIGS = {
    "default": {
        "toolbar": "full",
        "height": 400,
        "width": "100%",
    },
}

# Default primary key type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Custom user model
AUTH_USER_MODEL = "accounts.User"

# Email configuration
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = config("EMAIL_HOST", default="smtp4dev")
EMAIL_PORT = config("EMAIL_PORT", cast=int, default=25)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
EMAIL_USE_TLS = config("EMAIL_USE_TLS", cast=bool, default=False)


# DRF (Django REST Framework) settings
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_THROTTLE_CLASSES": [
        "rest_framework.throttling.AnonRateThrottle",
        "rest_framework.throttling.UserRateThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": "30/minute",          # For unauthenticated users
        "user": "200/hour",           # For authenticated users
    },
    'NUM_PROXIES': 1,
}


# JWT settings
SIMPLE_JWT = {
    "TOKEN_OBTAIN_SERIALIZER": "accounts.api.v1.serializers.CustomTokenObtainPairSerializer",
    "ALGORITHM": config("ALGORITHM", default="HS256"),
    "SIGNING_KEY": config("SIGNING_KEY", default=SECRET_KEY),
}


# Celery configuration
CELERY_BROKER_URL = config("CELERY_BROKER_URL", default="redis://redis:6379/1")
CELERY_TIMEZONE = "Asia/Tehran"

# Celery Beat configuration (Periodic tasks)
CELERY_BEAT_SCHEDULER = config(
    "CELERY_BEAT_SCHEDULER",
    default="django_celery_beat.schedulers.DatabaseScheduler"
)


# Caching configuration (Redis)
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://redis:6379/2",
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        },
    }
}


# Authentication URLs
LOGIN_URL = "/accounts/login/"
LOGOUT_REDIRECT_URL = "/blog/"


# Sites framework
SITE_ID = config("SITE_ID", cast=int, default=1)


# Robots.txt configuration
ROBOTS_USE_SITEMAP = True
ROBOTS_SITEMAP_VIEW_NAME = "cached-sitemap"

# If True, include scheme (http/https) in the Host header
ROBOTS_USE_SCHEME_IN_HOST = config("ROBOTS_USE_SCHEME_IN_HOST", cast=bool, default=False)
