# ==============================
# core/settings/production.py
# Production-specific settings (secure)
# ==============================

from .base import *


DEBUG = config("DEBUG", cast=bool, default=False)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=lambda v: [s.strip() for s in v.split(",")])

DATABASES = {
    "default": {
        "ENGINE": config("DB_ENGINE", default="django.db.backends.postgresql"),
        "NAME": config("DB_NAME", default="POSTGRES_DB"),
        "USER": config("DB_USER", default="POSTGRES_USER"),
        "PASSWORD": config("DB_PASSWORD", default="POSTGRES_PASSWORD"),
        "HOST": config("DB_HOST", default="postgres"),
        "PORT": config("DB_PORT", default="5432"),
    }
}

CORS_ALLOWED_ORIGINS = config("CORS_ALLOWED_ORIGINS", cast=lambda v: [s.strip() for s in v.split(",")])

# Security settings
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Logging config for production:
# - Only file-based logging
# - Errors only for Django, warnings+ for Celery
# - Uses TimedRotatingFileHandler for daily log rotation
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] {levelname} {name} {message}",
            "style": "{",
        },
    },
    "handlers": {
        "django_file": {
            "level": "ERROR",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": LOGS_DIR / "django_errors.log",
            "when": "midnight",
            "backupCount": 7,
            "formatter": "verbose",
        },
        "celery_worker_file": {
            "level": "WARNING",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": LOGS_DIR / "celery_worker.log",
            "when": "midnight",
            "backupCount": 7,
            "formatter": "verbose",
        },
        "celery_beat_file": {
            "level": "WARNING",
            "class": "logging.handlers.TimedRotatingFileHandler",
            "filename": LOGS_DIR / "celery_beat.log",
            "when": "midnight",
            "backupCount": 7,
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["django_file"],
            "level": "ERROR",
            "propagate": True,
        },
        "celery": {
            "handlers": ["celery_worker_file"],
            "level": "WARNING",
            "propagate": False,
        },
        "celery.beat": {
            "handlers": ["celery_beat_file"],
            "level": "WARNING",
            "propagate": False,
        },
    },
}
