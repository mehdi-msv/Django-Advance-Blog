# ==============================
# core/settings/development.py
# Development-specific settings
# ==============================

from .base import *


DEBUG = True
ALLOWED_HOSTS = ["*"]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:5500",
]


# Logging config for development:
# - Console + file output
# - Detailed debug info for Django
# - Celery logs at INFO level
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
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "verbose",
        },
        "django_file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": LOGS_DIR / "django_dev.log",
            "formatter": "verbose",
        },
        "celery_worker_file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": LOGS_DIR / "celery_worker_dev.log",
            "formatter": "verbose",
        },
        "celery_beat_file": {
            "level": "INFO",
            "class": "logging.FileHandler",
            "filename": LOGS_DIR / "celery_beat_dev.log",
            "formatter": "verbose",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["console", "django_file"],
            "level": "DEBUG",
            "propagate": True,
        },
        "celery": {
            "handlers": ["console", "celery_worker_file"],
            "level": "INFO",
            "propagate": False,
        },
        "celery.beat": {
            "handlers": ["console", "celery_beat_file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}