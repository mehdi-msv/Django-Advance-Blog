# ==============================
# core/settings/stage.py
# Staging-specific settings
# ==============================

from .base import *  # noqa: F403,F401


DEBUG = config("DEBUG", cast=bool, default=False)
ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS", cast=lambda v: [s.strip() for s in v.split(",")]
)

DATABASES = {
    "default": {
        "ENGINE": config(
            "DB_ENGINE", default="django.db.backends.postgresql"
        ),
        "NAME": config("DB_NAME", default="POSTGRES_DB"),
        "USER": config("DB_USER", default="POSTGRES_USER"),
        "PASSWORD": config("DB_PASSWORD", default="POSTGRES_PASSWORD"),
        "HOST": config("DB_HOST", default="postgres"),
        "PORT": config("DB_PORT", default="5432"),
    }
}

CORS_ALLOWED_ORIGINS = [
    "http://127.0.0.1:5500",
]

# Logging config for stage:
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
